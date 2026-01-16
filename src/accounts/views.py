from urllib import parse
# import requests

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Verification Email imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from carts.views import _cart_id
from carts.models import Cart, CartItem
from orders.models import Order, OrderProduct

# Create your views here.


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        if request.method == "POST":
            # getting the post data in the form
            form = RegistrationForm(request.POST)

            # checking if the form is valid
            if form.is_valid():
                # accessing all the values from the fields we got through post request
                first_name = form.cleaned_data["first_name"]
                last_name = form.cleaned_data["last_name"]
                email = form.cleaned_data["email"]
                phone_number = form.cleaned_data["phone_number"]
                password = form.cleaned_data["password"]

                # creating username
                username = email.split("@")[0]

                # creating user using custom create_user method mentioned in model manager
                user = Account.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username,
                    password=password,
                )

                # for phone number, since it is not in custom create_user method
                # (check MyAccountManager in accounts model)
                user.phone_number = phone_number
                user.save()

                # USER ACTIVATION
                # get the current site
                current_site = get_current_site(request)

                # email subject
                mail_subject = "Please activate your account"

                # the message to be sent
                message = render_to_string(
                    "accounts/account_verification_email.html", {
                        "user": user,
                        "domain": current_site,
                        # encoding user id with urlsafe so that no one can see the primary key
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        # default_token is in build library, when we check the user after activation
                        # we will use check_token from the same library
                        "token": default_token_generator.make_token(user),
                    })

                # receiver of email(user/customer)
                to_email = email

                # preparing email to be sent
                send_email = EmailMessage(
                    mail_subject,
                    message,
                    to=[to_email],
                )

                # sending email
                send_email.send()

                # messages.success(
                #    request, "Thank you for registering with us. We have sent you a verification email to your email address. Please verify it.")

                # instead of sending the message, we can send the user to a new url display
                # a message about verifying the email
                # We are sending the user to login.html and we are adding if statement in the
                # login.html (if request.GET.command == "verification"))
                return redirect("/accounts/login/?command=verification&email=" + email)

        else:
            form = RegistrationForm()

        return render(request, "accounts/register.html", {
            "form": form,
        })


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        if request.method == "POST":
            email = request.POST["email"]
            password = request.POST["password"]

            user = authenticate(email=email, password=password)

            if user is not None:
                try:
                    # check if the cart has items when the user is not logged in
                    # this is to ensure that if there are items in the cart before the user was
                    # logged in, then they are combined with the user cart items
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    cart_item_exists = CartItem.objects.filter(
                        cart=cart).exists()
                    if cart_item_exists:
                        # this will get all the cart items that are in the cart for non logged in user
                        cart_item = CartItem.objects.filter(cart=cart)

                        # get the product variations by cart id for above cart_item
                        product_variation = []
                        for item in cart_item:
                            variation = item.variations.all()
                            product_variation.append(list(variation))

                        # Get the cart items from the user cart to access user's product variations
                        cart_item = CartItem.objects.filter(user=user)
                        existing_variation_list = []
                        id = []
                        for item in cart_item:
                            existing_variation = item.variations.all()
                            existing_variation_list.append(
                                list(existing_variation))
                            id.append(item.id)

                        # checking if the current variation(non logged in cart) is in
                        # existing variation list(logged in user cart) by looping through
                        # the current variation(non logged in cart)
                        for variation in product_variation:
                            if variation in existing_variation_list:
                                index = existing_variation_list.index(
                                    variation)
                                item_id = id[index]
                                item = CartItem.objects.get(id=item_id)
                                item.quantity += 1
                                # assigning user to the cart item because we are transitioning
                                # from cart id to user defined cart
                                item.user = user
                                item.save()
                            else:
                                # if current variation (non logged in) is not in the user cart already
                                # then we create a new cart item in the user cart
                                cart_item = CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                    # assigning user to the cart item because we are transitioning
                                    # from cart id to user defined cart
                                    item.user = user
                                    item.save()
                except:
                    # if no item in the cart before logging in
                    pass

                login(request, user)

                # if clicking checkout when not logged in
                # dynamically redirecting the user to the checkout page after logging in

                # get the url
                url = request.META.get("HTTP_REFERER")

                try:
                    parsed_url = parse.urlparse(url)
                    # parsed_url = ParseResult(scheme='http', netloc='127.0.0.1:8000', path='/accounts/login/', params='', query='next=/cart/checkout/', fragment='')

                    query_params = parse.parse_qs(parsed_url.query)
                    # query_params = {'next': ['/cart/checkout/']}
                    if "next" in query_params:
                        next_page = query_params["next"][0]
                        return redirect(next_page)
                    else:
                        return redirect("store")
                except:
                    return redirect("store")

                """
                try:
                    query = requests.utils.urlparse(url).query
                    # next=/cart/checkout/
                    params = dict(x.split("=") for x in query.split("&"))
                    if "next" in params:
                        nextPage = params["next"]
                        return redirect(nextPage)
                except:
                    return redirect("dashboard")
                """
            else:
                messages.error(request, "Invalid Login Credentials.")
                return redirect("login")
        return render(request, "accounts/login.html")


@login_required(login_url="login")
def logout_view(request):
    logout(request)
    messages.success(request, "You are logged out.")
    return redirect("login")


def activate(request, uidb64, token):
    try:
        # get the uid
        uid = urlsafe_base64_decode(uidb64).decode()

        # get the user
        user = Account.objects.get(pk=uid)
       # user = Account._default_manager.get(pk=uid)

    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    # check if the user is valid and token is valid
    if user is not None and default_token_generator.check_token(user, token):
        # set the user to active
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your account is activated")
        return redirect("login")
    else:
        messages.error(request, "Invalid activation link")
        return redirect("register")


@login_required(login_url="login")
def dashboard(request):
    orders = Order.objects.order_by(
        '-created_at').filter(user=request.user, is_ordered=True)

    orders_count = orders.count()

    userprofile = UserProfile.objects.get(user=request.user)

    return render(request, "accounts/dashboard.html", {
        "orders_count": orders_count,
        "userprofile": userprofile,
    })


def forgotPassword(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        if request.method == "POST":
            email = request.POST["email"]

            # check if the account exists
            if Account.objects.filter(email=email).exists():
                # get the user
                user = Account.objects.get(email__exact=email)

                # check if the user is active
                if user.is_active:
                    # RESET PASSWORD EMAIL
                    current_site = get_current_site(request)
                    mail_subject = "Reset your Password"
                    message = render_to_string("accounts/reset_password_email.html", {
                        "user": user,
                        "domain": current_site,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": default_token_generator.make_token(user),
                    })

                    to_email = email
                    send_email = EmailMessage(
                        mail_subject,
                        message,
                        to=[to_email],
                    )

                    send_email.send()

                    messages.success(
                        request, "Password reset email has been sent to your email!")

                    return redirect("login")
                # if user is not active
                else:
                    messages.error(
                        request, "Account is not activated. Please activate your account")
                    return redirect("forgotPassword")
            # if user is not present
            else:
                messages.error(request, "Account does not exist.")
                return redirect("forgotPassword")
        return render(request, "accounts/forgotPassword.html")


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
       # user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Saving the uid in session so that we can access uid later when resetting the password
        request.session["uid"] = uid
        messages.success(request, "Please reset your password")
        return redirect("resetPassword")
    else:
        messages.error(request, "This link has expired.")
        return redirect("login")


def resetPassword(request):
    # check if user is already logged in
    if request.user.is_authenticated:
        return redirect("home")

    # check uid before granting access to this page
    uid = request.session.get("uid")

    if not uid:
        messages.error(request, "Unauthorized.")
        return redirect("forgotPassword")

    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()

            # delete uid from session after request is complete
            del request.session["uid"]
            messages.success(request, "Your password was successfully reset.")
            return redirect("login")

        else:
            messages.error(request, "Passwords do not match!")
            return redirect("resetPassword")
    return render(request, "accounts/resetPassword.html")


@login_required(login_url="/login")
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user, is_ordered=True).order_by('-created_at')

    return render(request, "accounts/my_orders.html", {
        "orders": orders,
    })


@login_required(login_url="login")
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated")
            return redirect("edit_profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    return render(request, "accounts/edit_profile.html", {
        "user_form": user_form,
        "profile_form": profile_form,
        "userprofile": userprofile,
    })


@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            # check the current password entered by the user
            success = user.check_password(current_password)

            if success:
                user.set_password(new_password)
                user.save()
                # auth.Logout(request)
                messages.success(
                    request, "Password updated successfully. Please login with new password.")
                return redirect("login")
            else:
                messages.error(request, "Please enter valid current password")
                return redirect("change_password")
        else:
            messages.error(request, "Password do not match.")
            return redirect("change_password")
    return render(request, "accounts/change_password.html")


@login_required(login_url="login")
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    print(order_id)
    order = Order.objects.get(order_number=order_id)
    sub_total = 0

    for i in order_detail:
        sub_total += i.product_price * i.quantity

    return render(request, "accounts/order_detail.html", {
        "order_detail": order_detail,
        "order": order,
        "sub_total": sub_total,
    })
