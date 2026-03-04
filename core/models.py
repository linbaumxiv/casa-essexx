from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# 1. Custom User Model
class User(AbstractUser):
    """
    Custom User model to distinguish between vendors and buyers.
    """
    is_vendor = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=False)

    def __str__(self):
        return self.username


# 2. Vendor Store Model
class Store(models.Model):
    """
    Represents a shop created by a vendor.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    vendor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'is_vendor': True}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# 3. Product Model
class Product(models.Model):
    """
    Represents an item for sale within a specific store.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    store = models.ForeignKey(
        Store, 
        on_delete=models.CASCADE, 
        related_name='products'
    )

    def __str__(self):
        return self.name


# 4. Order Model
class Order(models.Model):
    """
    Records a completed purchase by a buyer.
    """
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} by {self.buyer.username}"


# 5. Order Item Model
class OrderItem(models.Model):
    """
    Line items for an order, capturing the price at the time of purchase.
    """
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Deleted Product'}"


# 6. Review Model
class Review(models.Model):
    """
    Feedback left by users. Automatically checks if the review is 'Verified'.
    """
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}/5)"

    def save(self, *args, **kwargs):
        # Verification logic: Check if a matching OrderItem exists for this user/product
        if not self.pk:
            has_purchased = OrderItem.objects.filter(
                order__buyer=self.user,
                product=self.product
            ).exists()
            self.is_verified = has_purchased
        super().save(*args, **kwargs)