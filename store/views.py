from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime

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
        #  добавим логику в представление "cart" в нашем условном выражении, чтобы мы получали данные из файлов cookie
        #  только тогда, когда посетитель НЕ вошел в систему. С помощью оператора try / except создаем пустую корзину
        #  для работы, если она не существует
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}
        print('Cart:', cart)

        # создаю пока пустую корзину для не вошедшего в систему пользователя

        items = []
        # Cоздаю объект для пользователей, не вошедших в систему. Для этого объекта добавляю атрибуты get_cart_total
        # и get_cart_items и устанавливаю их равными 0, поскольку корзина гостей сейчас пуста.
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

        # чтобы посмотреть общее количество товаров в корзине, мы можем просто просмотреть наш словарь корзины
        # и добавить общее количество каждого товара

        # Далее добавим цикл в нашу «корзину» и запросим продукт, чтобы получить цену

        # Потенциальная проблема, с которой мы можем столкнуться, заключается в том, что пользователь добавляет товар
        # в свою корзину и за время, необходимое пользователю для оформления заказа, допустим, администратор удаляет товар
        # из базы данных. Это означает, что мы будем запрашивать продукт с не верным идентификатором.
        # Мы можем исправить это, добавив в наш цикл блок «try / except» и проигнорировав эту проблему.
        for i in cart:
            try:
                cartItems += cart[i]['quantity']

                product = Product.objects.get(id=i)
                total = (product.price * cart[i]['quantity'])

                order['get_cart_total'] += total
                order['get_cart_items'] += cart[i]['quantity']
                # На каждой итерации цикла для товаров в нашей корзине мы будем создавать объект item и добавлять его
                # в наш список товаров. Объект item будет содержать все те же атрибуты, что и наша модель OrderItem.
                item = {
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': product.price,
                        'imageURL': product.imageURL
                    },
                    'quantity': cart[i]['quantity'],
                    'get_total': total,
                }
                items.append(item)

                # запросим атрибут «digital» продуктов и Django значение «shipping», чтобы проверить,
                # является ли один из элементов НЕ цифровым элементом

                if product.digital == False:
                    order['shipping'] = True

            except:
                pass

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
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        # выполняю сравнение общего количества отправленных и нашей корзины
        if total == order.get_cart_total:
            order.complete = True
        order.save()

        # создаю экземпляр адреса доставки, если адрес был отправлен
        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )

    else:
        print('User is not logged in')

    return JsonResponse('Payment submitted..', safe=False)
