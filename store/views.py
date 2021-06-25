from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder

# импортирую все модели и запрашиваю продукты в представлении магазина

def store(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

# Представляю порядок действий пользователя с помощью словаря, чтобы в нашем шаблоне всегда было
# что запросить когда у нас есть покупатель и заказ / корзина, запрашиваю элементы корзины
# с помощью order.orderitem_set.all ()

def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

# Представляю порядок действий пользователя с помощью словаря, чтобы в нашем шаблоне всегда было
# что запросить когда у нас есть покупатель и заказ / корзина, запрашиваю элементы корзины
# с помощью order.orderitem_set.all ()

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

# Устанавливаю переменную идентификатора транзакции
# Дальше нужно проанализировать данные, отправленные из почтового запроса, и запросить/создать некоторые данные,
# если пользователь аутентифицирован. Опять же, мы будем игнорировать неаутентифицированных пользователей до следующего модуля.
# Мы будем использовать json.loads () для анализа данных. Как только мы установим возвращаемое значение
# для переменной «data», мы можем запрашивать элементы внутри как словарь Python.

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)