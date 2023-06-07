from django.shortcuts import render, get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q

from .models import Product

from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id


def store(request, category_slug=None):
    category = None
    products = None

    if category_slug != None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=category, is_avaliable=True
        ).order_by("id")
    else:
        products = Product.objects.all().filter(is_avaliable=True).order_by("id")

    paginator = Paginator(products, 3)
    page = request.GET.get("page", 1)
    paged_products = paginator.get_page(page)

    product_count = products.count()

    context = {"products": paged_products, "product_count": product_count}
    return render(request, "store/store.html", context)


def product_detail(request, category_slug, product_slug):
    product = None
    try:
        product = Product.objects.get(
            category__slug=category_slug, slug=product_slug, is_avaliable=True
        )
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=product
        ).exists()
    except Exception as e:
        raise e
    context = {"product": product, "in_cart": in_cart}

    return render(request, "store/product_detail.html", context)


def search(request):
    products = []
    product_count = 0
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            products = Product.objects.filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
            ).order_by("-create_date")
            product_count = products.count()
    context = {"products": products, "product_count": product_count}
    return render(request, "store/store.html", context)
