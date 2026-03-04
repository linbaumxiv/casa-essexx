from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# API Routing setup
router = DefaultRouter()
router.register(r'api-stores', views.StoreViewSet, basename='store-api')
router.register(r'api-products', views.ProductViewSet, basename='product-api')
router.register(r'api-reviews', views.ReviewViewSet, basename='review-api')

urlpatterns = [
    # --- Public Views ---
    path('', views.ProductListView.as_view(), name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('register/', views.RegisterView.as_view(), name='register'),

    # --- Vendor Dashboard & Management ---
    path('dashboard/', views.VendorDashboardView.as_view(), name='vendor_dashboard'),
    path('store/add/', views.StoreCreateView.as_view(), name='store_create'),
    path('store/edit/<int:pk>/', views.StoreUpdateView.as_view(), name='store_edit'),
    path('store/delete/<int:pk>/', views.StoreDeleteView.as_view(), name='delete_store'),
    
    path('product/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('product/edit/<int:pk>/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('product/delete/<int:pk>/', views.ProductDeleteView.as_view(), name='product_delete'),

    # --- Shopping Cart & Checkout ---
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),

    # --- API Endpoints ---
    path('api/', include(router.urls)),
]