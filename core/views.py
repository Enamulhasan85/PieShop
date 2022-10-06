from sqlite3 import Timestamp
from unicodedata import category, name
from django.shortcuts import render, redirect
from .models import UserProfile, Category, Product, Cart, Order, OrderProduct, Address, Payment
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import datetime
import random
import string

# Create your views here.

def home(request):
    categorylist = []
    for category in Category.objects.all():
        if Product.objects.filter(category=category).count() == 0:
            continue
        categorylist.append({
            'category': category.name,
            'products': Product.objects.filter(category=category)
        })
    cartitems = Cart.objects.filter(user=request.user).count()
    return render(request, 'home\index.html',{
        'product': categorylist,
        'cartitems': cartitems
    })


def addcart(request, slug):
    product = Product.objects.get(slug=slug)
    cartitem, notcreated = Cart.objects.get_or_create(item=product, user=request.user)
    if notcreated == False: 
        cartitem.quantity = cartitem.quantity + 1
    cartitem.save()

    return redirect("home")


def product(request, slug):
    product = Product.objects.get(slug=slug)
    if request.method == 'POST' and request.POST.get("quantity"):
        cartitem, notcreated = Cart.objects.get_or_create(item=product, user=request.user)
        if notcreated == False: 
            cartitem.quantity = cartitem.quantity + int(request.POST.get("quantity"))
        else:
            cartitem.quantity = request.POST.get("quantity")
        cartitem.save()

    cartitems = Cart.objects.filter(user=request.user).count()
    products = Product.objects.filter(category=product.category)
    return render(request, 'core\index.html',{
        'product': product,
        'cartitems': cartitems,
        'products': products
    })


def productaddcart(request, slug):
    product = Product.objects.get(slug=slug)
    cartitem, notcreated = Cart.objects.get_or_create(item=product, user=request.user)
    if notcreated == False:
        cartitem.quantity = cartitem.quantity + 1
    cartitem.save()

    cartitems = Cart.objects.filter(user=request.user).count()
    products = Product.objects.filter(category=product.category)
    return render(request, 'core\index.html',{
        'product': product,
        'cartitems': cartitems,
        'products': products
    })


def cart(request):
    products = Cart.objects.filter(user=request.user)
    if request.method == 'POST':
        for item in products:
            if request.POST.get(item.item.slug):
                if request.POST.get(item.item.slug) == '0':
                    item.delete()
                else:
                    item.quantity = request.POST.get(item.item.slug)         
                    item.save()
            else:
                item.delete()

    products = Cart.objects.filter(user=request.user)
    cartitems = Cart.objects.filter(user=request.user).count()
    total = 0.0
    for product in products:
        total += product.get_final_price()
    return render(request, 'core\cart.html',{
        'products': products,
        'cartitems': cartitems,
        'totalprice': total,
        'total': total+50
    })


def shipping(request):
    products = Cart.objects.filter(user=request.user)
    if request.method == 'POST':
        total = 0.0
        for item in products:
            total += item.get_final_price()

        letters = string.digits
        created = True
        customer = UserProfile.objects.get(user=request.user)
        while created:
            result_str = customer.stripe_customer_id + ''.join(random.choice(letters) for i in range(6))
            created = Payment.objects.filter(stripe_charge_id=result_str).exists()

        payment = Payment(user=request.user, amount=total, stripe_charge_id=result_str)
        payment.save()

        created = True
        while created:
            result_str = ''.join(random.choice(letters) for i in range(9))
            created = Order.objects.filter(ref_code=result_str).exists()

        order = Order(user=request.user, status='ORDERED')
        order.ref_code = result_str
        order.name = request.POST.get("name")
        order.phone = request.POST.get("phone")
        order.shipping_address = Address.objects.get(id=request.POST.get("seladdress"))
        order.payment = payment
        order.save()

        products = Cart.objects.filter(user=request.user)
        for item in products:
            orderproduct = OrderProduct(order=order, item=item.item, quantity=item.quantity)
            orderproduct.save()
            item.delete()

        return redirect("/cart/")

    products = Cart.objects.filter(user=request.user)
    cartitems = Cart.objects.filter(user=request.user).count()
    addresses = Address.objects.filter(user=request.user)
    if cartitems == 0:
        return redirect("cart")
    total = 0.0
    for product in products:
        total += product.get_final_price()
    return render(request, 'core\shipping.html',{
        'products': products,
        'cartitems': cartitems,
        'totalprice': total,
        'total': total+50,
        'addresses': addresses
    })


def createaddress(request):
    if request.method == 'POST':
        address = Address()
        address.user = request.user
        address.country = request.POST.get("country")
        address.city = request.POST.get("city")
        address.street_address = request.POST.get("address")
        address.save()
    else:
        return redirect("/shipping/")
    return redirect("/shipping/")