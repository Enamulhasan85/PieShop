from django.urls import path
from core import views
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', RedirectView.as_view(url='/home')),
    path('home/', views.home, name='home'),
    path('home/add-to-cart/<slug:slug>', views.addcart, name='home_addtocart'),
    path("products/<slug:slug>", views.product, name='product'),
    path("products/add-to-cart/<slug:slug>", views.productaddcart, name='product_addtocart'),
    path('cart/', views.cart, name='cart'),
    path('shipping/', views.shipping, name='shipping'),
    path('shipping/createaddress/', views.createaddress, name='shipping'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)