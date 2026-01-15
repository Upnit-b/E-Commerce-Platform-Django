from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.contrib import messages

from carts.models import CartItem
from carts.views import _cart_id
from .models import Product, ReviewRating, ProductGallery
from .forms import ReviewForm
from category.models import Category
from orders.models import OrderProduct

# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=categories, is_available=True).order_by("product_name")

        # Pagination
        paginator = Paginator(products, 3)
        page = request.GET.get("page")
        paged_products = paginator.get_page(page)

        product_count = products.count()
    else:
        products = Product.objects.all().filter(
            is_available=True).order_by("product_name")

        # Pagination
        paginator = Paginator(products, 3)
        page = request.GET.get("page")
        paged_products = paginator.get_page(page)

        product_count = products.count()

    return render(request, "store/store.html", {
        "products": paged_products,
        "product_count": product_count,

    })


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug)

        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=single_product).exists()

    except Exception as e:
        raise e

    try:
        orderproduct = OrderProduct.objects.filter(
            user=request.user.id, product=single_product).exists()

    except OrderProduct.DoesNotExist:
        orderproduct = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(
        product=single_product, status=True)

    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(
        product_id=single_product.id)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        "product_gallery": product_gallery,

    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            products = Product.objects.order_by(
                "product_name").filter(product_name__icontains=keyword)
            product_count = products.count()

    return render(request, "store/store.html", {
        "products": products,
        "product_count": product_count,
        "keyword": keyword,
    })


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    product = Product.objects.get(pk=product_id)
    user = request.user

    if request.method == 'POST':
        try:
            # Check if the user already reviewed the product
            review = ReviewRating.objects.get(product=product, user=user)
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                messages.success(
                    request, "Thank you! Your review has been updated.")
                return redirect(url)
            else:
                messages.error(request, "Invalid form data")
                return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                new_review = ReviewRating()
                new_review.subject = form.cleaned_data['subject']
                new_review.rating = form.cleaned_data['rating']
                new_review.review = form.cleaned_data['review']
                new_review.ip = request.META.get('REMOTE_ADDR')
                new_review.product = product
                new_review.user = user
                new_review.save()
                messages.success(
                    request, 'Thank you! Your review has been submitted.')
                return redirect(url)
