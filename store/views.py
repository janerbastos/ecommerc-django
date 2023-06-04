from django.shortcuts import render, get_object_or_404
from category.models import Category
from .models import Product


def store(request, category_slug=None):
    category = None
    products = None

    if category_slug != None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_avaliable=True)
    else:
        products = Product.objects.all().filter(is_avaliable=True)

    product_count = products.count()

    context = {"products": products, "product_count": product_count}
    return render(request, "store/store.html", context)


def product_detail(request, category_slug, product_slug):
    product = None
    try:
        product = Product.objects.get(
            category__slug=category_slug, slug=product_slug, is_avaliable=True
        )
    except Exception as e:
        raise e
    context = {"product": product}

    return render(request, "store/product_detail.html", context)
