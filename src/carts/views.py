from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from store.models import Product, Variation
from .models import Cart, CartItem

# Create your views here.

# private function to get cart Id from user session


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


# ADDING TO THE CART
def add_cart(request, product_id):
    # The flow
    # 1. get the product
    # 2. check if the user is authenticated, if authenticated use the user for cart identification
    # 3. get all the variations from the product to be added first and save that product variation
    # in an array
    # 4. Check if there is already a similar product in the cart (not comparing variations)
    # 5. If similar product exists in cart, check its variations
    # 6. If the variations are similar as well, increase the quantity
    # 7. If the variations are not similar but the product is same, add new product, in other words,
    # create new cart item in the cart

    current_user = request.user

    # first get the product using the product_id
    product = Product.objects.get(pk=product_id)

    # if the user is authenticated
    if current_user.is_authenticated:
        # create an empty product variation list
        product_variation = []
        if request.method == "POST":
            # check all the items in the post request to get the variations
            for item in request.POST:
                key = item
                value = request.POST[key]

                # get only the variations from the POST request
                try:
                    variation = Variation.objects.get(
                        product=product, variation_category__iexact=key, variation_value__iexact=value)

                    # add the current product variations in the product_variation list
                    product_variation.append(variation)
                except Variation.DoesNotExist:
                    pass

        # Check if the cart items already exists
        # Important: Do not add cart here because the cart_item is identified by user after authentication
        # and before authentication (logging in), the cart items are identified by cart
        cart_item_exists = CartItem.objects.filter(
            product=product, user=current_user).exists()

        # check if atleast one cart item for this product exists
        if (cart_item_exists):
            # if the cart item exists, we check the variations and see if they are same as well
            cart_item = CartItem.objects.filter(
                product=product, user=current_user)

            # Checking the variations of the product, for this we need:
            # existing variations from database
            # current variations from product_variations above
            # item_id from database

            existing_variation_list = []
            id = []

            for item in cart_item:
                existing_variation = item.variations.all()
                # add all the existing item variations to a list
                existing_variation_list.append(list(existing_variation))
                # also get the cart item id for future use
                id.append(item.id)

            # check if the currrent variation is in existing variation list
            if product_variation in existing_variation_list:
                # to increase the cart quantity of this product
                # we need id of this product with variations first

                # get the index of the existing product variation from existing variation list
                # that matches the current product and variation that we are trying to add to the
                # cart
                index = existing_variation_list.index(product_variation)
                # get the cart item id using the above index
                item_id = id[index]

                # get the cart item by using the cart item id we got above and the product
                item = CartItem.objects.get(product=product, id=item_id)

                # increase the existing cart item quantity by 1
                item.quantity += 1
                item.save()

            # if the product variation is not in the existing variation list
            else:
                # create a new product with current variations
                item = CartItem.objects.create(
                    product=product,
                    user=current_user,
                    quantity=1,
                )

                # clear these variations as we have already added it
                if len(product_variation) > 0:
                    # remove all hanging variations related to the current cart item (safety for db)
                    # django does not overwrite manytomany relationships automatically
                    item.variations.clear()
                    # add selected variation objects to the cart item
                    item.variations.add(*product_variation)

                    # we can also use item.variations.set(product_variations) instead of:
                    # item.variations.clear()
                    # item.variations.add(*product_variation)
                item.save()

        # if there is no cart item like the one we are adding
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )

            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect("cart")

    # if the user is not authenticated
    else:
        # same as above with one key change;
        # instead of user=current_user, we use the cart for non logged in users since they are
        # not the user
        product_variation = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(
                        product=product, variation_category__iexact=key, variation_value__iexact=value)

                    product_variation.append(variation)
                except:
                    pass

        # we create the cart here because the user is not authenticated and we need identification
        # for the cart
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
            cart.save()

        cart_item_exists = CartItem.objects.filter(
            product=product, cart=cart).exists()

        if (cart_item_exists):
            cart_item = CartItem.objects.filter(product=product, cart=cart)

            existing_variation_list = []
            id = []

            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in existing_variation_list:
                index = existing_variation_list.index(product_variation)
                item_id = id[index]

                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(
                    product=product,
                    cart=cart,
                    quantity=1,
                )

                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
        if len(product_variation) > 0:
            cart_item.variations.clear()

            cart_item.variations.add(*product_variation)
        cart_item.save()
    return redirect("cart")


# REMOVING ONE ITEM FROM THE CART USING MINUS
def remove_cart(request, product_id, cart_item_id):
    # get the product
    product = get_object_or_404(Product, pk=product_id)

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                product=product,
                user=request.user,
                id=cart_item_id,
            )
        else:
            # get the cart (cart is required here because there is no user)
            cart = Cart.objects.get(cart_id=_cart_id(request))

            # get the cart item using cart item id so that we dont delete other product with diff variations
            cart_item = CartItem.objects.get(
                product=product,
                cart=cart,
                id=cart_item_id
            )

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return redirect("cart")


# REMOVING THE ENTIRE PRODUCT
def remove_cart_item(request, product_id, cart_item_id):

    # get the product
    product = get_object_or_404(Product, pk=product_id)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(
            product=product, user=request.user, id=cart_item_id)
    else:
        # get the cart (cart is required here because there is no user)
        cart = Cart.objects.get(cart_id=_cart_id(request))
        # get the cart_item using the cart_item_id so that we don't delete other product with diff variations
        cart_item = CartItem.objects.get(
            product=product,
            cart=cart,
            id=cart_item_id
        )

    cart_item.delete()
    return redirect("cart")


# THE CART
def cart_view(request):
    total = 0
    quantity = 0
    cart_items = []
    tax = 0
    grand_total = 0

    try:
        if request.user.is_authenticated:
            # For logged in users, the cart items are imported when they were not logged in
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True)
        else:
            # if the user is not logged in and added cart items, this will display cart items
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (10 * total) / 100
        grand_total = total + tax
    except Cart.DoesNotExist:
        pass

    return render(request, "store/cart.html", {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
    })


# CHECKOUT VIEW
@login_required(login_url="login")
def checkout(request):
    total = 0
    tax = 0
    quantity = 0
    cart_items = []
    tax = 0
    grand_total = 0

    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True)
            if not cart_items:
                messages.error(
                    request, "You must have items in cart to access this route.")
                return redirect("cart")
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            if not cart_items:
                messages.error(
                    request, "You must have items in cart to access this route.")
                return redirect("cart")

        for cart_item in cart_items:
            total += (cart_item.quantity * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (10 * total) / 100
        grand_total = total + tax
    except Cart.DoesNotExist:
        messages.error(
            request, "You must have items in cart to access this route.")
        return redirect("cart")

    return render(request, "store/checkout.html", {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
    })
