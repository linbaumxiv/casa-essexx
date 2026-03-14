from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views 

# API Routing setup
router = DefaultRouter()
router.register(r'api-stores', views.StoreViewSet, basename='store-api')
router.register(r'api-products', views.ProductViewSet, basename='product-api')
router.register(r'api-reviews', views.ReviewViewSet, basename='review-api')

urlpatterns = [
    # --- Public & Authentication ---
    path('', views.ProductListView.as_view(), name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    # FIXED: Points to the function-based register view for auto-login logic
    path('register/', views.register, name='register'),

    # --- Vendor Dashboard & Store Management ---
    path('dashboard/', views.VendorDashboardView.as_view(), name='vendor_dashboard'),
    path('store/add/', views.StoreCreateView.as_view(), name='store_create'),
    path('store/<int:pk>/edit/', views.StoreUpdateView.as_view(), name='store_edit'),
    path('store/<int:pk>/delete/', views.StoreDeleteView.as_view(), name='delete_store'),
    
    # --- Product Management ---
    # FIXED: Requirement to pass store_id so the store is auto-selected
    path('store/<int:store_id>/product/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('product/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    # --- Shopping Cart & Checkout ---
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),

    # --- API Endpoints ---
    path('api/', include(router.urls)),
]
