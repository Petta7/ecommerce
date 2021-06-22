from django.shortcuts import render
from .models import *


# импортирую все модели и запрашиваю продукты в представлении магазина
def store(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:

        # создаю пока пустую корзину для не вошедшего в систему пользователя

        items = []
        # Cоздаю объект для пользователей, не вошедших в систему. Для этого объекта добавляю атрибуты get_cart_total
        # и get_cart_items и устанавливаю их равными 0, поскольку корзина гостей сейчас пуста.
        order = {'get_cart_total': 0, 'get_cart_items': 0}

    context = {'items': items, 'order': order}
    return render(request, 'store/cart.html', context)


# Представляю порядок действий пользователя с помощью словаря, чтобы в нашем шаблоне всегда было
# что запросить когда у нас есть покупатель и заказ / корзина, запрашиваю элементы корзины
# с помощью order.orderitem_set.all ()
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        # Create empty cart for now for non-logged in user
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}

    context = {'items': items, 'order': order}
    return render(request, 'store/checkout.html', context)
