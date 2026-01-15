from .models import Cart, CartItem
from .views import _cart_id

# function to get all quantity of cart items so that it can be displayed in nav bar and be used
# elsewhere if needed
def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            #this is to make sure that the cart number is preserved when the user signs in assuming that the user added products to cart when not signed in
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart=cart[:1])

            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0

    return {"cart_count": cart_count}
