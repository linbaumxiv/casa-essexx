from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Store, Product, Order, OrderItem, Review


# --- INLINES ---

class ProductInline(admin.TabularInline):
    """Allows viewing/editing products directly inside the Store admin page."""
    model = Product
    extra = 0


class OrderItemInline(admin.TabularInline):
    """Allows viewing items directly inside the Order admin page."""
    model = OrderItem
    extra = 0
    readonly_fields = ('price_at_purchase',)


# --- ADMIN MODELS ---

class CustomUserAdmin(UserAdmin):
    """Customized User admin to manage Vendor and Buyer roles."""
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('is_vendor', 'is_buyer')}),
    )
    list_display = ('username', 'email', 'is_vendor', 'is_buyer', 'is_staff')
    list_filter = ('is_vendor', 'is_buyer', 'is_staff')


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    """Admin interface for Store management."""
    list_display = ('name', 'vendor', 'created_at')
    search_fields = ('name', 'vendor__username')
    inlines = [ProductInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product management."""
    list_display = ('name', 'store', 'price', 'stock')
    list_filter = ('store',)
    search_fields = ('name', 'description')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order management."""
    list_display = ('id', 'buyer', 'created_at', 'total_price')
    list_filter = ('created_at',)
    inlines = [OrderItemInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for reviewing customer feedback."""
    list_display = ('product', 'user', 'rating', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'rating')
    readonly_fields = ('is_verified',)

# Registering the User model with the custom admin class
admin.site.register(User, CustomUserAdmin)