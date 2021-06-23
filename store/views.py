from django.shortcuts import render
from django.http import JsonResponse
import json

from .models import *


# импортирую все модели и запрашиваю продукты в представлении магазина
def store(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:

        # создаю пока пустую корзину для не вошедшего в систему пользователя

        items = []
        # Cоздаю объект для пользователей, не вошедших в систему. Для этого объекта добавляю атрибуты get_cart_total
        # и get_cart_items и устанавливаю их равными 0, поскольку корзина гостей сейчас пуста.
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


# Представляю порядок действий пользователя с помощью словаря, чтобы в нашем шаблоне всегда было
# что запросить когда у нас есть покупатель и заказ / корзина, запрашиваю элементы корзины
# с помощью order.orderitem_set.all ()
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


# импортирую Json в верхнюю часть нашего файла "views.py" и использую его внутри нашего представления updateItem
# для анализа данных. Я хочу установить переменные action и productId, обратившись к переменной data.
# После этого можем получить доступ к значениям в виде словаря Python
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    # Я собираеюсь использовать идентификатор продукта для запроса продукта и использовать «get_or_create»
    # для работы со статусом «False», потому что атрибут complete означает, что это открытая корзина,
    # в которую мы можем добавить.
    # Я хотчу сделать то же самое с элементом заказа и установить для заказа и продукта значения,
    # указанные выше. Причина, по которой я использую get_or_create, заключается в том, что позже на странице
    # корзины я хочу иметь возможность обновлять количество заказа с помощью действия «добавить» вместо того,
    # чтобы каждый раз создавать новый.

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    # Добавляю логику для обновления или удаления элемента из нашего заказа.
    # Мы еще не использовали «удалить», но по сути мы хотим обновить количество в зависимости от действия.
    # Проверяем, равно ли количество нулю или меньше, если да, то мы хотим просто удалить этот товар
    # из корзины.

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)
