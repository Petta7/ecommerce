from django.db import models
from django.contrib.auth.models import User


# добавляю модель клиента, которая 3 атрибута: пользователь, имя, электронная почта

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)

    def __str__(self):
        return self.name


# Далее создаю 3 основные модели, составляющие заказ

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=True)

    # img
    def __str__(self):
        return self.name


# Заказ будет сводкой заказа товаров и идентификатора транзакции.
# Модель элемента заказа будет связана с клиентом отношениями «один ко многим» (AKA ForeignKey)
# и будет содержать статус завершения (True или False) и идентификатор транзакции вместе с датой
# размещения этого заказа

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)


# Для модели OrderItem потребуется атрибут продукта, связанный с моделью продукта, заказ,
# к которому этот товар подключен, количество и дата добавления этого товара в корзину

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)


# Добавляю модель адреса доставки, она будет дочерней для заказа и будет создана только в том случае,
# если хотя бы один элемент заказа в заказе является физическим продуктом (если Product.digital == False).
# Подлючу эту модель к клиенту, чтобы клиент мог повторно использовать адрес доставки в будущем

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
