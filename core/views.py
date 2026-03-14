from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login # For Requirement: Auto-login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import transaction
from django.core.mail import send_mail
from django.db.models import Avg, Q

from rest_framework import viewsets, permissions

from .forms import CustomUserCreationForm, ReviewForm
from .models import Store, Product, Order, OrderItem, Review
from .serializers import StoreSerializer, ProductSerializer, ReviewSerializer
from .permissions import IsVendorOrReadOnly

# --- API ACCESS ---

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsVendorOrReadOnly] # Requirement: Secure API

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsVendorOrReadOnly]

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# --- USER AUTHENTICATION ---

def register(request):
    """
    Requirement: Directly login the user after successful registration.
    Requirement: Unique email check is handled by the form/model.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Auto-login
            messages.success(request, f"Welcome to Casa Essexx, {user.username}!")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# --- PUBLIC VIEWS ---

class ProductListView(ListView):
    model = Product
    template_name = 'core/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.annotate(avg_rating=Avg('reviews__rating'))
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))
        return queryset

def product_detail(request, product_id):
    """
    Requirement: Verified reviews check purchase history.
    """
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all().order_by('-created_at')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to leave a review.")
            return redirect('login')
            
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            # Check if user purchased product for verified status
            review.is_verified = OrderItem.objects.filter(
                order__buyer=request.user, 
                product=product
            ).exists()
            review.save()
            messages.success(request, "Your review has been posted!")
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()
    return render(request, 'core/product_detail.html', {'product': product, 'reviews': reviews, 'form': form})


# --- VENDOR DASHBOARD & MANAGEMENT ---

class VendorDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Store
    template_name = 'core/vendor_dashboard.html'
    context_object_name = 'stores'

    def test_func(self):
        return self.request.user.is_vendor

    def get_queryset(self):
        return Store.objects.filter(vendor=self.request.user).prefetch_related('products')

class StoreCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Store
    fields = ['name', 'description'] # Requirement: Description is mandatory in model
    template_name = 'core/store_form.html'
    success_url = reverse_lazy('vendor_dashboard')

    def test_func(self):
        return self.request.user.is_vendor

    def form_valid(self, form):
        form.instance.vendor = self.request.user
        return super().form_valid(form)

class StoreUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Store
    fields = ['name', 'description']
    template_name = 'core/store_form.html'
    success_url = reverse_lazy('vendor_dashboard')

    def test_func(self):
        return self.request.user == self.get_object().vendor

class StoreDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Store
    template_name = 'core/store_confirm_delete.html'
    success_url = reverse_lazy('vendor_dashboard')

    def test_func(self):
        return self.request.user == self.get_object().vendor

class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Requirement: Auto-select store from URL instead of asking again.
    """
    model = Product
    fields = ['name', 'description', 'price', 'stock', 'image'] # 'store' removed from fields
    template_name = 'core/product_form.html'
    success_url = reverse_lazy('vendor_dashboard')
    
    def test_func(self):
        return self.request.user.is_vendor

    def form_valid(self, form):
        # Automatically assign the store from the URL kwarg
        store_id = self.kwargs.get('store_id')
        form.instance.store = get_object_or_404(Store, id=store_id, vendor=self.request.user)
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    fields = ['name', 'description', 'price', 'stock']
    template_name = 'core/product_form.html' 
    success_url = reverse_lazy('vendor_dashboard')

    def test_func(self):
        return self.request.user == self.get_object().store.vendor

class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'core/product_confirm_delete.html'
    success_url = reverse_lazy('vendor_dashboard')

    def test_func(self):
        return self.request.user == self.get_object().store.vendor


# --- SHOPPING & CHECKOUT LOGIC ---

def add_to_cart(request, product_id):
    """
    Requirement: Add quantity option and validate against stock.
    """
    product = get_object_or_404(Product, id=product_id)
    # Get quantity from POST, default to 1
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    cart = request.session.get('cart', {})
    current_in_cart = cart.get(str(product_id), 0)
    
    # Requirement: Stock validation including items already in cart
    if current_in_cart + quantity > product.stock:
        messages.error(request, f"Cannot add {quantity} units. Only {product.stock - current_in_cart} remaining.")
    else:
        cart[str(product_id)] = current_in_cart + quantity
        request.session['cart'] = cart
        messages.success(request, f"Added {quantity} x {product.name} to cart.")
    
    return redirect('home')

@login_required
@transaction.atomic 
def checkout(request):
    """
    Requirement: Transaction-safe stock updates.
    """
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('home')

    try:
        order = Order.objects.create(buyer=request.user)
        for item_id, quantity in cart.items():
            product = Product.objects.select_for_update().get(id=item_id)

            if product.stock >= quantity:
                product.stock -= quantity # Requirement: Keep track of stock
                product.save()
                OrderItem.objects.create(
                    order=order, product=product, 
                    quantity=quantity, price_at_purchase=product.price 
                )
            else:
                raise Exception(f"Stock changed for {product.name}. Please review your cart.")

        request.session['cart'] = {}
        return render(request, 'core/success.html')

    except Exception as e:
        messages.error(request, str(e))
        return redirect('cart_detail')

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_total = product.price * quantity
        total += item_total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'item_total': item_total,
        })
    return render(request, 'core/cart_detail.html', {'cart_items': cart_items, 'total': total})

def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
    return redirect('cart_detail')