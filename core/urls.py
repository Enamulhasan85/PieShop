from django.urls import path
from core import views
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', RedirectView.as_view(url='/home')),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('register/', views.registerpage, name='register'),
    path('login/', views.loginpage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('home/add-to-cart/<slug:slug>', views.addcart, name='home_addtocart'),
    path("products/<slug:slug>", views.product, name='product'),
    path("product-category/<int:id>", views.productsearch, name='productsearch'),
    path("products/add-to-cart/<slug:slug>", views.productaddcart, name='product_addtocart'),
    path("products/createreview/<slug:slug>", views.createreview, name='CreateReview'),
    path('cart/', views.cart, name='cart'),
    path('shipping/', views.shipping, name='shipping'),
    path('shipping/createaddress/', views.createaddress, name='shipping'),
    path('profile/', views.profile, name='profile'),
    path('profile/createaddress/', views.createaddressprofile, name='createaddressprofile'),
    path('profile/deleteaddress/<int:id>', views.deleteaddressprofile, name='address_delete'),
    path('order/', views.order, name='order'),
    path('order/track/<slug:ref_code>', views.trackorder, name='trackorder'),
    path('order/cancelorder/', views.cancelorder, name='cancelorder'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)