import json
from .models import *


# Создаю функцию cookieCart (), которая будет обрабатывать всю логику, которую мы создали
# для порядка наших гостевых пользователей. Далее скопирую всю логику, которая генерирует нашу корзину
# из файлов cookie браузера, и вставлю ее в новую функцию cookieCart

def cookieCart(request):
    # Create empty cart for now for non-logged in user
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
        print('CART:', cart)

    # создаю пока пустую корзину для не вошедшего в систему пользователя

    items = []
    # Cоздаю объект для пользователей, не вошедших в систему. Для этого объекта добавляю атрибуты get_cart_total
    # и get_cart_items и устанавливаю их равными 0, поскольку корзина гостей сейчас пуста.

    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']

    # Чтобы посмотреть общее количество товаров в корзине, мы можем просто просмотреть наш словарь корзины
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
                'id': product.id,
                'product': {'id': product.id, 'name': product.name, 'price': product.price,
                            'imageURL': product.imageURL}, 'quantity': cart[i]['quantity'],
                'digital': product.digital, 'get_total': total,
            }
            items.append(item)
            # запросим атрибут «digital» продуктов и Django значение «shipping», чтобы проверить,
            # является ли один из элементов НЕ цифровым элементом

            if product.digital == False:
                order['shipping'] = True
        except:
            pass

    return {'cartItems': cartItems, 'order': order, 'items': items}


# Создаю еще одну функцию под корзиной файлов cookie с названием «cartData».
# Как и в случае с cookieCart, копирую всю логику из наших представлений и вставляю ее в корзину для файлов cookie.

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'cartItems': cartItems, 'order': order, 'items': items}

# Создаю функцию, которая заботится о создании заказа для «гостя» и «возвращает» его. Скопируем сюда логику проверки гостей.
def guestOrder(request, data):
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
    return customer, order
