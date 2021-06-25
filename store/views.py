from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime

from .models import *
from .utils import cookieCart, cartData


# импортирую все модели и запрашиваю продукты в представлении магазина
def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

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

    else:
        print('User is not logged in')

# Начнем с создания данных нашей корзины с помощью функции корзины файлов cookie.
        print('COOKIES:', request.COOKIES)
        name = data['form']['name']
        email = data['form']['email']

# Создаем заказ и устанавливаем значение только что установленной переменной клиента.
# Для параметра «Complete» устанавливаем значение «false», поскольку это открытая корзина до подтверждения и обработки платежа.
        cookieData = cookieCart(request)
        items = cookieData['items']

        customer, created = Customer.objects.get_or_create(
            email=email,
        )
        customer.name = name
        customer.save()

# Пройдемся по списку реплик нашей корзины и создадим настоящие OrderItems, запросив продукт и установив необходимые атрибуты.
        order = Order.objects.create(
            customer=customer,
            complete=False,
        )

        for item in items:
            product = Product.objects.get(id=item['product']['id'])
            orderItem = OrderItem.objects.create(
                product=product,
                order=order,
                quantity=item['quantity'],
            )
#  Поскольку мы создали «заказ» как для авторизованных, так и для гостевых пользователей,
#  нам необходимо сделать его доступным для обоих условий.
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
