"""
Project-level URL Configuration.
Handles admin, authentication, media serving, and app routing.
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin Interface
    path('admin/', admin.site.urls),

    # Authentication - Password Reset Flow (Requirement #5)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html'
         ), name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ), name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), name='password_reset_complete'),

    # Standard Auth (Login/Logout)
    path('accounts/', include('django.contrib.auth.urls')),

    # Core App URLs
    path('', include('core.urls')), 
]

# Serving Media files during development (Requirement #3 & #6)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)