from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Store, Product, Order, OrderItem

# 1. Define the layout
class CustomUserAdmin(UserAdmin):
    model = User
    # Add 'is_vendor' and 'is_buyer' to the Edit User page
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('is_vendor', 'is_buyer')}),
    )
    # Add them to the User List page so you can see them at a glance
    list_display = ['username', 'email', 'is_vendor', 'is_buyer', 'is_staff']

# 2. Register (or Re-register) the model
admin.site.register(User, CustomUserAdmin)

# 3. Register the other models
admin.site.register(Store)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)