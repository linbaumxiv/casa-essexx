from django.test import TestCase, Client
from unittest.mock import patch 
from django.urls import reverse
from .models import User, Store, Product, Order, OrderItem, Review


class MarketplaceTestCase(TestCase):
    """
    Test suite for Casa Essexx Marketplace.
    Covers Authentication, Permissions, and Business Logic.
    """

    def setUp(self):
        """Set up initial data for testing."""
        # Create a Vendor
        self.vendor = User.objects.create_user(
            username='vendor_user', 
            password='password123', 
            is_vendor=True
        )
        # Create a Buyer
        self.buyer = User.objects.create_user(
            username='buyer_user', 
            password='password123', 
            is_buyer=True
        )
        # Create a Store
        self.store = Store.objects.create(
            name="Tech Haven", 
            vendor=self.vendor
        )
        # Create a Product
        self.product = Product.objects.create(
            name="Laptop", 
            price=999.99, 
            stock=5, 
            store=self.store
        )

    # --- 1. PERMISSIONS TESTS (Requirement #7) ---

    def test_vendor_dashboard_access(self):
        """Verify only vendors can access the dashboard."""
        # Buyer tries to access
        self.client.login(username='buyer_user', password='password123')
        response = self.client.get(reverse('vendor_dashboard'))
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Vendor tries to access
        self.client.login(username='vendor_user', password='password123')
        response = self.client.get(reverse('vendor_dashboard'))
        self.assertEqual(response.status_code, 200)

    # --- 2. BUSINESS LOGIC TESTS (Requirement #4) ---

    def test_verified_review_logic(self):
        """Verify that reviews are marked 'verified' only if purchased."""
        # 1. Buyer leaves a review WITHOUT purchasing
        review1 = Review.objects.create(
            product=self.product,
            user=self.buyer,
            rating=5,
            comment="Looks cool!"
        )
        self.assertFalse(review1.is_verified)

        # 2. Buyer purchases the product
        order = Order.objects.create(buyer=self.buyer)
        OrderItem.objects.create(
            order=order, 
            product=self.product, 
            quantity=1, 
            price_at_purchase=999.99
        )

        # 3. Buyer leaves a review AFTER purchasing
        review2 = Review.objects.create(
            product=self.product,
            user=self.buyer,
            rating=5,
            comment="Love it, I actually bought it!"
        )
        self.assertTrue(review2.is_verified)

    # --- 3. CART & CHECKOUT TESTS (Requirement #2 & #3) ---

    def test_checkout_reduces_stock(self):
        """Verify that successful checkout reduces product stock."""
        self.client.login(username='buyer_user', password='password123')
        
        # Simulate adding to session cart
        session = self.client.session
        session['cart'] = {str(self.product.id): 2}
        session.save()

        # Execute checkout
        self.client.get(reverse('checkout'))
        
        # Refresh product from DB
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3) # Started at 5, bought 2

    # --- 4. DATA INTEGRITY TESTS ---

    def test_store_deletion_cascades(self):
        """Verify that deleting a store removes its products."""
        product_id = self.product.id
        self.store.delete()
        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(id=product_id)


#--MOCKING X API--

class MarketplaceSignalTestCase(TestCase):
    """Tests that signals fire correctly without hitting the real Twitter API."""

    def setUp(self):
        self.vendor = User.objects.create_user(
            username='test_vendor', 
            password='password123', 
            is_vendor=True
        )

    @patch('core.signals.get_twitter_client')
    def test_twitter_signal_on_store_creation(self, mock_client):
        """Verify that creating a store triggers the Twitter signal."""
        # Setup the mock to return a fake 'create_tweet' method
        mock_instance = mock_client.return_value
        
        # Create a store, which triggers the signal
        Store.objects.create(
            name="Mock Store", 
            vendor=self.vendor, 
            description="A test store"
        )

        # Assert that the Twitter client was called exactly once
        self.assertTrue(mock_client.called)
        self.assertEqual(mock_client.call_count, 1)

    @patch('core.signals.get_twitter_client')
    def test_twitter_signal_on_product_creation(self, mock_client):
        """Verify that adding a product triggers the Twitter signal."""
        store = Store.objects.create(name="Signal Store", vendor=self.vendor)
        
        # Clear the mock call history from the store creation
        mock_client.reset_mock()

        Product.objects.create(
            name="Signal Product", 
            price=10.00, 
            stock=1, 
            store=store
        )

        # Assert the signal fired for the product
        self.assertTrue(mock_client.called)