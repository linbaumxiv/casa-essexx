from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView  
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, ReviewForm
from django.db import transaction  
from django.core.mail import send_mail 
from rest_framework import viewsets, permissions
from .models import Store, Product, Order, OrderItem, Review 
from .serializers import StoreSerializer, ProductSerializer, ReviewSerializer
from django.db.models import Avg

#--- API ACCESS---
class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    # Allow anyone to see stores, but only logged-in users to create/edit
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)

#---API REVIEWS---
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Automatically saves the review under the logged-in user
        serializer.save(user=self.request.user)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

#---NEW USER---
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    
# --- PUBLIC VIEWS ---
class ProductListView(ListView):
    model = Product
    template_name = 'core/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.annotate(avg_rating=Avg('reviews__rating'))
        
        # 1. Search Query
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query) | queryset.filter(description__icontains=query)
            
        # 2. Price Filtering
        min_p = self.request.GET.get('min_price')
        max_p = self.request.GET.get('max_price')

        if min_p:
            queryset = queryset.filter(price__gte=min_p) # gte = Greater Than or Equal to
        if max_p:
            queryset = queryset.filter(price__lte=max_p) # lte = Less Than or Equal to
            
        return queryset

# --- VENDOR DASHBOARD ---
@login_required
@user_passes_test(lambda u: u.is_vendor)
def vendor_dashboard(request):
    my_stores = Store.objects.filter(vendor=request.user)
    return render(request, 'core/vendor_dashboard.html', {'stores': my_stores})

# --- STORE MANAGEMENT ---
class StoreCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Store
    fields = ['name', 'description']
    template_name = 'core/store_form.html'
    success_url = reverse_lazy('vendor_dashboard')

    def test_func(self):
        return self.request.user.is_vendor

    def form_valid(self, form):
        form.instance.vendor = self.request.user
        return super().form_valid(form)

class StoreUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Store
    fields = ['name', 'description',]
    template_name = 'core/store_form.html' 
    success_url = reverse_lazy('vendor_dashboard')

    def test_func(self):
        store = self.get_object()
        return self.request.user == store.vendor


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    fields = ['name', 'description', 'price', 'stock']
    template_name = 'core/product_form.html' 
    success_url = reverse_lazy('vendor_dashboard')

    def test_func(self):
        # Ensures only the vendor who owns the store can edit the product
        product = self.get_object()
        return self.request.user == product.store.vendor

from django.views.generic.edit import CreateView, UpdateView, DeleteView # Add DeleteView here

class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'core/product_confirm_delete.html'
    success_url = reverse_lazy('vendor_dashboard')

    def test_func(self):
        # Only the owner of the store can delete the product
        product = self.get_object()
        return self.request.user == product.store.vendor

# --- PRODUCT MANAGEMENT ---
class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
  
    fields = ['name', 'description', 'price', 'stock', 'store', 'image']
    template_name = 'core/product_form.html'
    success_url = reverse_lazy('vendor_dashboard')
    
    def test_func(self):
        return self.request.user.is_vendor

#---PRODUCT DETAILS---
def product_detail(request, product_id):
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
            review.save()
            messages.success(request, "Your review has been posted!")
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, 'core/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form
    })

#---PRODUCT REVIEWS---
def home(request):
    # This adds an 'avg_rating' attribute to every product object
    products = Product.objects.annotate(avg_rating=Avg('reviews__rating'))
    return render(request, 'core/product_list.html', {'products': products})

# --- SHOPPING LOGIC ---
def add_to_cart(request, product_id):
    
    product = get_object_or_404(Product, id=product_id)
    
    cart = request.session.get('cart', {})
    
    # Logic to add/increment
    item_id = str(product_id)
    if item_id in cart:
        cart[item_id] += 1
    else:
        cart[item_id] = 1
        
    request.session['cart'] = cart
    
    messages.success(request, f"Added {product.name} to your cart!")
    
    return redirect('home')

#---CHECKOUT FUNCTION---
#SAFETY NETS 
@login_required
@transaction.atomic 
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('home')

    # Create the order record first
    order = Order.objects.create(buyer=request.user)
    
    try:
        for item_id, quantity in cart.items():
            # SAFETY 1: Check if the product still exists in the database
            try:
                product = Product.objects.select_for_update().get(id=item_id)
            except Product.DoesNotExist:
                return render(request, 'core/error.html', {
                    'message': "One of the items in your cart is no longer available. Please update your cart."
                })

            # SAFETY 2: Check stock levels
            if product.stock >= quantity:
                product.stock -= quantity
                product.save()
                OrderItem.objects.create(
                    order=order, 
                    product=product, 
                    quantity=quantity,
                    price_at_purchase=product.price 
                )
            else:
                return render(request, 'core/error.html', {
                    'message': f'Sorry, only {product.stock} units of {product.name} are left.'
                })

        # Clear the cart ONLY if everything above succeeded
        request.session['cart'] = {}
        
        # SAFETY 3: Wrap email in a try-block so a mail server error doesn't undo the sale
        try:
            send_mail(
                'Your Invoice - Casa Essexx',
                f'Hi {request.user.username}, thank you for your purchase! Order ID: {order.id}',
                'noreply@casaessexx.com',
                [request.user.email],
                fail_silently=False, 
            )
        except Exception:
            pass # The sale is more important than the email!

        return render(request, 'core/success.html')

    except Exception as e:
        # Catch-all for unexpected database issues
        return render(request, 'core/error.html', {
            'message': "A technical error occurred during checkout. Please try again."
        })

#---CART PAGE--
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
    

# Clear Cart Button
def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
    return redirect('cart_detail')