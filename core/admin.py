from django.contrib import admin
from .models import UserProfile, Category, Product, Cart, Order, OrderProduct, Address, Payment, Review

# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'stripe_customer_id', )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', )

class CartAdmin(admin.ModelAdmin):
    list_display = ('item', 'quantity', 'user', )

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'shipping_address', 'payment', 'status', )

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'item', 'quantity', )

class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'street_address', 'city', )
    
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'timestamp', )

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'reviewtext', 'rating', )

admin.site.register(UserProfile, ProfileAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Review, ReviewAdmin)