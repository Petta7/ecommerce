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
    price = models.DecimalField(max_digits=7, decimal_places=2)
    digital = models.BooleanField(default=False, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


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

    # делаю цикл, который изменяет статус «доставка» на «истина», если дочерний элемент OrderItem не является цифровым.
    # Затем метод просто возвращает истинное или ложное значение
    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping

    # Для модели заказа добавляю get_cart_total и get_cart_items пользуясь декоратором @property
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


# Для модели OrderItem потребуется атрибут продукта, связанный с моделью продукта, заказ,
# к которому этот товар подключен, количество и дата добавления этого товара в корзину

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    # Для модели OrderItem получаю общую цену из цены продукта, умноженной на количество
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


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
