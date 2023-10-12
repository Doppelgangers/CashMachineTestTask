from django.db import models

# Create your models here.


class Item(models.Model):
    #Поле длиной 100 символов для хранения названия товара
    title = models.CharField(max_length=100, verbose_name="наименование")
    # для хранения цены товара с 10 цифрами и 2 знаками после запятой.
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Item({self.pk}, {self.title}, {self.price} руб.)"
