import stripe
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from shop import settings
from store.models import Product, Cart, Order

stripe.api_key=settings.STRIPE_API_KEY
def index(request):
    products = Product.objects.all()
    return render(request, 'store/index.html', context={"products": products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    return render(request, 'store/detail.html', context={"product": product})


def add_to_cart(request, slug):
    user = request.user
    product = get_object_or_404(Product, slug=slug)
    cart, _ = Cart.objects.get_or_create(user=user)
    order, created = Order.objects.get_or_create(user=user,ordered=False, product=product)

    if created:
        cart.orders.add(order)
        cart.save()
    else:
        order.quantity +=1
        order.save()
    return redirect(reverse("product",kwargs={"slug":slug}))


def cart(request):
    cart=get_object_or_404(Cart,user=request.user)
    return render(request,'store/cart.html', context={"orders":cart.orders.all()})

def delete_cart(request):
    if cart := request.user.cart:
        cart.delete()

    return redirect('index')

def create_checkout_session(request):
    cart=request.user.cart
    line_items=[{"price":order.product.stripe_id,"quantity":order.quantity}for order in cart.orders.all()]
    session = stripe.checkout.Session.create(
        locale="fr",
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri(reverse('checkout-success')),
        cancel_url='http://127.0.0.1:8000/',
    )

    return redirect(session.url, code=303)

def checkout_success(request):
    return render(request,'store/success.html')

#scenic-relent-succes-poise
#whsec_c25f5dc5665f62a4a81817cd8148f8a136298de1fac47ff7fc84c649eaa13d95
@csrf_exempt
def stripe_webhook(request):
    payload=request.body
    print(payload)

    return HttpResponse(status=200)


