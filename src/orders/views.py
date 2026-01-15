import datetime
import json
import requests
import uuid

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt

from carts.models import CartItem, Product
from .forms import OrderForm
from .models import Order, Payment, OrderProduct

# Create your views here.

# Paypal Access Token


def get_paypal_token():
    url = f"{settings.PAYPAL_API_BASE}/v1/oauth2/token"
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US",
    }

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(
        url,
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
        headers=headers,
        data=data
    )

    if response.status_code == 200:
        return response.json()["access_token"]

    return None


@csrf_exempt
def create_order(request):

    if request.method == "POST":
        data = json.loads(request.body)
        order_id = data["cart"][0]["id"]

        order = Order.objects.get(order_number=order_id)

        cart_items = CartItem.objects.filter(user=request.user)
        all_items = []

        for item in cart_items:
            all_items.append(item)

        token = get_paypal_token()

        headers = {
            "Content-Type": "application/json",
            "Paypal-Request-Id": data["cart"][0]["id"],
            "Authorization": f"Bearer {token}"
        }

        payload = {
            "intent": "CAPTURE",
            "payment_source": {
                "paypal": {
                    "experience_context": {
                        "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                        "landing_page": "LOGIN",
                        "user_action": "PAY_NOW",
                    }
                }
            },
            "purchase_units": [{
                "reference_id": order.order_number,
                "invoice_id": order.order_number,
                "amount": {
                    "currency_code": "USD",
                    "value": str(order.order_total),
                    "breakdown": {
                        "item_total": {
                            "currency_code": "USD",
                            "value": str(order.order_total)
                        },
                    }
                }
            }],

            "items": [],
        }

        response = requests.post(
            f"{settings.PAYPAL_API_BASE}/v2/checkout/orders", headers=headers, json=payload)

        response_data = response.json()
        # print(response_data)

        return JsonResponse({
            "paypal_order_id": response_data["id"],
            "status": response_data["status"]
        })


def payments(request):
    if request.method == "POST":
        body_data = json.loads(request.body)
        order_id = body_data.get("orderID")

        token = get_paypal_token()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        data = "{}"

        response = requests.post(
            f"{settings.PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture", headers=headers, data=data)

        capture_data = response.json()

        user = request.user

        payment_id = capture_data['purchase_units'][0]['payments']['captures'][0]['id']

        keys = capture_data['payment_source'].keys()
        payment_method = list(keys)[0]

        amount_paid = capture_data['purchase_units'][0]['payments']['captures'][0]['amount']['value']

        status = capture_data['status']

        order_id = capture_data['purchase_units'][0]['reference_id']

        order = Order.objects.get(
            user=request.user, is_ordered=False, order_number=order_id)

        payment = Payment(
            user=user,
            payment_id=payment_id,
            payment_method=payment_method,
            amount_paid=amount_paid,
            status=status,
        )

        payment.save()

        # Update order
        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the cart items to OrderProduct table
        cart_items = CartItem.objects.filter(user=user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order = order
            orderproduct.payment = payment
            orderproduct.user = user
            orderproduct.product = item.product
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(pk=item.id)
            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(pk=orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()

            # Reduce the quantity of sold products
            product = Product.objects.get(pk=item.product.id)
            product.stock -= item.quantity
            product.save()

        # Clear the cart
        CartItem.objects.filter(user=user).delete()

        # Send order received email to customer
        mail_subject = "Thank you for your order!"
        message = render_to_string("orders/order_received_email.html", {
            "user": request.user,
            "order": order,
        })
        to_email = request.user.email
        send_email = EmailMessage(
            mail_subject, message, to=[to_email])
        send_email.send()

        # Send order number and payment id back to onApprove method via JsonResponse
        return JsonResponse({
            'success': True,
            "payment_id": payment_id,
            "status": status,
            "order_number": order_id,
        })
    else:
        return redirect("cart")


def place_order(request):
    current_user = request.user

    # if the user is not logged in, then redirect them back to cart page if they try to access
    # place_order page via url
    if not current_user.is_authenticated:
        messages.error(request, "You must be logged in to acccess this route.")
        return redirect("cart")

    # if the cart count is zero, then redirect back to cart
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        messages.error(
            request, "You must have items in the cart to acccess this route.")
        return redirect("cart")

    grand_total = 0
    total = 0
    tax = 0
    quantity = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (10 * total) / 100
    grand_total = total + tax

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing info inside the database
            # get the instance of the order model to save data in this instance
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data["first_name"]
            data.last_name = form.cleaned_data["last_name"]
            data.phone_number = form.cleaned_data["phone_number"]
            data.email = form.cleaned_data["email"]
            data.address_line_1 = form.cleaned_data["address_line_1"]
            data.address_line_2 = form.cleaned_data["address_line_2"]
            data.country = form.cleaned_data["country"]
            data.state = form.cleaned_data["state"]
            data.city = form.cleaned_data["city"]
            data.order_note = form.cleaned_data["order_note"]
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get("REMOTE_ADDR")
            data.save()

            # Generate order number
            today = datetime.date.today()
            suffix = uuid.uuid4().hex[:8].upper()
            order_number = f"Ord-{today}-{suffix}"
            data.order_number = order_number
            data.save()

            # get the current order to render it on place_order.html
            order = Order.objects.get(
                user=current_user,
                is_ordered=False,
                order_number=order_number
            )

            return render(request, "orders/place_order.html", {
                "order": order,
                "cart_items": cart_items,
                "total": total,
                "tax": tax,
                "grand_total": grand_total,
            })

    return redirect("store")


def order_complete(request):
    order_number = request.GET.get("order_number")
    payment_id = request.GET.get("payment_id")

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        if order.is_ordered == True:
            order.status = "Completed"

        ordered_products = OrderProduct.objects.filter(order=order)
        for item in ordered_products:
            print(item.variations)

        sub_total = 0
        for i in ordered_products:
            sub_total += i.product_price * i.quantity
        payment = Payment.objects.get(payment_id=payment_id)

        context = {
            "order": order,
            "ordered_products": ordered_products,
            "order_number": order.order_number,
            "payment_id": payment.payment_id,
            "sub_total": sub_total,
        }
        return render(request, "orders/order_complete.html", context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect("home")
