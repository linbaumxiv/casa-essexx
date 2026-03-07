from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import transaction
from django.core.mail import send_mail
from django.db.models import Avg

from rest_framework import viewsets, permissions

from .forms import CustomUserCreationForm, ReviewForm
from .models import Store, Product, Order, OrderItem, Review
from .serializers import StoreSerializer, ProductSerializer, ReviewSerializer
from .permissions import IsVendorOrReadOnly

# --- API ACCESS ---

class StoreViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing stores."""
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing reviews."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing products."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# --- USER AUTHENTICATION ---

class RegisterView(CreateView):
    """View to handle new user registration."""
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')


# --- PUBLIC VIEWS ---

class ProductListView(ListView):
    """Public list of all products with search and price filtering."""
    model = Product
    template_name = 'core/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.annotate(avg_rating=Avg('reviews__rating'))
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                models.Q(name__icontains=query) | 
                models.Q(description__icontains=query)
            )
        
        min_p = self.request.GET.get('min_price')
        max_p = self.request.GET.get('max_price')
        if min_p:
            queryset = queryset.filter(price__gte=min_p)
        if max_p:
            queryset = queryset.filter(price__lte=max_p)
        return queryset


def product_detail(request, product_id):
    """Detailed product view including verified/unverified review logic."""
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
            
            # Logic: Check if user purchased product to mark as verified
            review.is_verified = OrderItem.objects.filter(
                order__buyer=request.user, 
                product=product
            ).exists()
            
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


# --- VENDOR DASHBOARD & MANAGEMENT ---

class VendorDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Dashboard where vendors manage their specific stores and products."""
    model = Store
    template_name = 'core/vendor_dashboard.html'
    context_object_name = 'stores'

    def test_func(self):
        return self.request.user.is_vendor

    def get_queryset(self):
        return Store.objects.filter(vendor=self.request.user).prefetch_related('products')


class StoreCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Allows a vendor to create a new store."""
    model = Store
    fields = ['name', 'description']
    template_name = 'core/store_form.html'
    success_url = reverse_lazy('vendor_dashboard')

    def test_func(self):
        return self.request.user.is_vendor

    def form_valid(self, form):
        # Automatically link the store to the logged-in vendor
        form.instance.vendor = self.request.user
        return super().form_valid(form)


class StoreUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Allows a vendor to edit their store details."""
    model = Store
    fields = ['name', 'description']
    template_name = 'core/store_form.html'
    success_url = reverse_lazy('vendor_dashboard')

    def test_func(self):
        store = self.get_object()
        return self.request.user == store.vendor
    

class StoreDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Allows a vendor to remove their store."""
    model = Store
    template_name = 'core/store_confirm_delete.html'
    success_url = reverse_lazy('vendor_dashboard')

    def test_func(self):
        store = self.get_object()
        return self.request.user == store.vendor


class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Allows a vendor to add a new product."""
    model = Product
    fields = ['name', 'description', 'price', 'stock', 'store', 'image']
    template_name = 'core/product_form.html'
    success_url = reverse_lazy('vendor_dashboard')
    
    def test_func(self):
        return self.request.user.is_vendor


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Allows a vendor to edit existing product details."""
    model = Product
    fields = ['name', 'description', 'price', 'stock']
    template_name = 'core/product_form.html' 
    success_url = reverse_lazy('vendor_dashboard')

    def test_func(self):
        product = self.get_object()
        return self.request.user == product.store.vendor


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Allows a vendor to remove a product."""
    model = Product
    template_name = 'core/product_confirm_delete.html'
    success_url = reverse_lazy('vendor_dashboard')

    def test_func(self):
        product = self.get_object()
        return self.request.user == product.store.vendor


# --- SHOPPING & CHECKOUT LOGIC ---

def add_to_cart(request, product_id):
    """Add a product to the session-based shopping cart."""
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    item_id = str(product_id)
    cart[item_id] = cart.get(item_id, 0) + 1
    request.session['cart'] = cart
    messages.success(request, f"Added {product.name} to your cart!")
    return redirect('home')


@login_required
@transaction.atomic 
def checkout(request):
    """Process order, update stock, clear cart, and send invoice email."""
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('home')

    order = Order.objects.create(buyer=request.user)
    
    try:
        for item_id, quantity in cart.items():
            product = Product.objects.select_for_update().get(id=item_id)

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
                transaction.set_rollback(True)
                return render(request, 'core/error.html', {
                    'message': f'Insufficient stock for {product.name}.'
                })

        request.session['cart'] = {}
        
        try:
            send_mail(
                'Your Invoice - Casa Essexx',
                f'Thank you for your purchase! Order ID: {order.id}',
                'noreply@casaessexx.com',
                [request.user.email],
                fail_silently=True, 
            )
        except Exception:
            pass 

        return render(request, 'core/success.html')

    except Exception:
        return render(request, 'core/error.html', {
            'message': "A technical error occurred. Please try again."
        })


def cart_detail(request):
    """View to display current items in the session cart."""
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
    """Wipes all items from the current session cart."""
    if 'cart' in request.session:
        del request.session['cart']
    return redirect('cart_detail')