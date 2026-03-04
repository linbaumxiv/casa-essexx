from rest_framework import serializers
from .models import Store, Product, Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Translates Review models into JSON. 
    Uses StringRelatedField to show usernames instead of IDs.
    """
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'is_verified', 'created_at']
        read_only_fields = ['is_verified']


class ProductSerializer(serializers.ModelSerializer):
    """
    Translates Product models into JSON, nesting associated reviews.
    """
    # This "nests" the reviews inside the product JSON data
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 
            'stock', 'image', 'store', 'reviews'
        ]


class StoreSerializer(serializers.ModelSerializer):
    """
    Translates Store models into JSON, nesting associated products.
    """
    products = ProductSerializer(many=True, read_only=True)
    vendor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Store
        fields = ['id', 'name', 'vendor', 'products']