from django.urls import path, include
from rest_framework.routers import DefaultRouter 
from . import views
from .views import RegisterView

router = DefaultRouter()
router.register(r'api-stores', views.StoreViewSet, basename='store-api')
router.register(r'api-products', views.ProductViewSet, basename='product-api')
router.register(r'api-reviews', views.ReviewViewSet, basename='review-api')

urlpatterns = [
    # The empty quotes '' means this is the Home Page
    path('', views.ProductListView.as_view(), name='home'),
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('store/add/', views.StoreCreateView.as_view(), name='store_create'),
    path('store/edit/<int:pk>/', views.StoreUpdateView.as_view(), name='store_edit'),
    path('product/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('product/edit/<int:pk>/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('api/', include(router.urls))
]