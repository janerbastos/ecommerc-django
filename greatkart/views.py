from django.shortcuts import render

from store.models import Product


def home(request):
    prodocts = Product.objects.all().filter(is_avaliable=True)
    context = {"products": prodocts}
    return render(request, "home.html", context)
