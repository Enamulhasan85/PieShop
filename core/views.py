from sqlite3 import Timestamp
from unicodedata import category, name
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.utils import timezone
from .models import *
from .forms import *
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
    
    cartitems = 0
    if request.user.is_authenticated:
        cartitems = Cart.objects.filter(user=request.user).count()

    return render(request, 'home\index.html',{
        'product': categorylist,
        'cartitems': cartitems
    })


def loginpage(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password = password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.warning(request, 'Username or Password Incorrect')

    context = {}
    return render(request, 'accounts/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect("login")


def registerpage(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            letters = string.digits
            userinfo = UserProfile(user=authenticate(request, username=user, password = form.cleaned_data.get('password1')))
            userinfo.stripe_customer_id = user + ''.join(random.choice(letters) for i in range(6))
            userinfo.save()
            return redirect('login')

    context = {'form': form}
    return render(request, 'accounts/register.html', context)


@login_required(login_url='login')
def addcart(request, slug):
    product = Product.objects.get(slug=slug)
    if product.quantity == 0:
        return redirect('home')
    cartitem, notcreated = Cart.objects.get_or_create(item=product, user=request.user)
    if notcreated == False: 
        cartitem.quantity = cartitem.quantity + 1
    cartitem.save()
    product.quantity -= 1
    product.save()
    return redirect("home")


def product(request, slug):
    product = Product.objects.get(slug=slug)
    if request.method == 'POST' and request.POST.get("quantity"):
        if request.user.is_authenticated == False:
            return redirect("login")
        qty = min(product.quantity, int(request.POST.get("quantity")))
        cartitem, notcreated = Cart.objects.get_or_create(item=product, user=request.user)
        if notcreated == False: 
            cartitem.quantity = cartitem.quantity + qty
        else:
            cartitem.quantity = qty
        cartitem.save()
        product.quantity -= qty
        product.save()
    
    cartitems = 0
    if request.user.is_authenticated:
        cartitems = Cart.objects.filter(user=request.user).count()
    products = Product.objects.filter(category=product.category)
    
    return render(request, 'core\index.html',{
        'product': product,
        'cartitems': cartitems,
        'products': products
    })


@login_required(login_url='login')
def productaddcart(request, slug):
    product = Product.objects.get(slug=slug)
    if product.quantity == 0:
        return redirect('home')
    cartitem, notcreated = Cart.objects.get_or_create(item=product, user=request.user)
    if notcreated == False:
        cartitem.quantity = cartitem.quantity + 1
    cartitem.save()
    product.quantity -= 1
    product.save()
    cartitems = Cart.objects.filter(user=request.user).count()
    products = Product.objects.filter(category=product.category)
    return render(request, 'core\index.html',{
        'product': product,
        'cartitems': cartitems,
        'products': products
    })


@login_required(login_url='login')
def cart(request):
    products = Cart.objects.filter(user=request.user)
    if request.method == 'POST':
        for item in products:
            product = Product.objects.get(slug=item.item.slug)
            qty = 0
            if request.POST.get(item.item.slug):
                if request.POST.get(item.item.slug) == '0':
                    qty = -item.quantity
                    item.delete()
                else:
                    qty = min(int(request.POST.get(item.item.slug))-item.quantity, product.quantity)
                    item.quantity += qty
                    item.save()
            else:
                qty = -item.quantity
                item.delete()
            product.quantity -= qty
            product.save()

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


@login_required(login_url='login')
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

        payment = Payment(user=request.user, amount=total+50, timestamp=datetime.datetime.now(), stripe_charge_id=result_str)
        payment.save()

        created = True
        while created:
            result_str = ''.join(random.choice(letters) for i in range(9))
            created = Order.objects.filter(ref_code=result_str).exists()

        order = Order(user=request.user, start_date=datetime.datetime.now(), status='RECEIVED')
        order.ref_code = result_str
        order.name = request.POST.get("name")
        order.phone = "+88" + request.POST.get("phone")
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


@login_required(login_url='login')
def createaddress(request):
    if request.method == 'POST':
        address = Address()
        address.user = request.user
        address.country = request.POST.get("country")
        address.city = request.POST.get("city")
        address.area = request.POST.get("area")
        address.street_address = request.POST.get("streetaddress")
        address.save()
    else:
        return redirect("/shipping/")
    return redirect("/shipping/")


@login_required(login_url='login')
def profile(request):
    if request.method == 'POST':
        userinfo = UserProfile.objects.get(user=request.user)
        userinfo.fullname = request.POST.get("fullname")
        userinfo.birthdate = request.POST.get("birthdate")
        userinfo.gender = request.POST.get("gender")
        userinfo.phone = request.POST.get("phone")
        userinfo.save()

    userinfo = UserProfile.objects.get(user=request.user)
    if userinfo.birthdate != None:
        birthdate = userinfo.birthdate.strftime('%Y-%m-%d')
    else:
        birthdate = datetime.datetime.now().strftime('%Y-%m-%d')
    cartitems = Cart.objects.filter(user=request.user).count()
    addresses = Address.objects.filter(user=request.user)
    
    return render(request, 'core\profile.html',{
        'userinfo': userinfo,
        'date':birthdate,
        'user': request.user,
        'cartitems': cartitems,
        'addresses': addresses
    })


@login_required(login_url='login')
def createaddressprofile(request):
    if request.method == 'POST':
        address = Address()
        address.user = request.user
        address.country = request.POST.get("country")
        address.city = request.POST.get("city")
        address.area = request.POST.get("area")
        address.street_address = request.POST.get("streetaddress")
        address.save()
    else:
        return redirect("/profile/")
    return redirect("/profile/")


@login_required(login_url='login')
def deleteaddressprofile(request, id):
    if request.method == 'POST':
        Address.objects.filter(id=id).delete()
    else:
        return redirect("/profile/")
    return redirect("/profile/")


@login_required(login_url='login')
def order(request):
    orders = Order.objects.filter(user=request.user).order_by('-start_date')
    ordercount = Order.objects.filter(user=request.user).count()
    cartitems = Cart.objects.filter(user=request.user).count()
    
    orderlist = []
    for order in orders:
        orderlist.append({
            'order': order,
            'products': OrderProduct.objects.filter(order=order)
        })

    return render(request, 'core\order.html',{
        'ordercount': ordercount,
        'orders': orderlist,
        'cartitems': cartitems,
    })


@login_required(login_url='login')
def trackorder(request, ref_code):
    order = Order.objects.get(ref_code=ref_code)
    orderproducts = OrderProduct.objects.filter(order=order)
    orderproductcount = OrderProduct.objects.filter(order=order).count()
    cartitems = Cart.objects.filter(user=request.user).count()
    payment = Payment.objects.get(order=order).amount

    return render(request, 'core\ordertrack.html',{
        'ordercount': orderproductcount,
        'orderproducts': orderproducts,
        'order': order,
        'totalprice': payment-50,
        'total': payment,
        'cartitems': cartitems,
    })


@login_required(login_url='login')
def cancelorder(request):
    if request.method == 'POST':
        order = Order.objects.get(ref_code=request.POST.get("ref_code"))
        order.status = 'CANCELLED'
        order.save()
        orderproducts = OrderProduct.objects.filter(order=order)
        for item in orderproducts:
            product = Product.objects.get(slug=item.item.slug)
            product.quantity += item.quantity
            product.save()
    else:
        return redirect("/order/")
    return redirect("/order/")