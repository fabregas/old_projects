from django.db import models

class KeysDict(models.Model):
    dict_type = models.CharField(max_length=32)
    key = models.CharField(max_length=1024)

    
class Order(models.Model):
    booking_date = models.DateField(db_index=True)
    receive_date = models.DateField(null=True, db_index=True)
    seller = models.ForeignKey(KeysDict)
    course = models.FloatField()
    discount_percent = models.FloatField(default=0)
    delivery = models.FloatField()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, null=True)
    brand = models.ForeignKey(KeysDict, related_name='brand_to_keys_dict', null=True)
    name = models.ForeignKey(KeysDict, related_name='name_to_keys_dict', null=True)
    option = models.ForeignKey(KeysDict, related_name='itemoption_to_keys_dict', null=True)
    cost = models.FloatField(null=True)
    price = models.FloatField()
    notes = models.TextField(null=True)

    location = models.CharField(max_length=32, null=True, db_index=True)
    shop_seller = models.ForeignKey(KeysDict, null=True)
    sale_date = models.DateField(null=True)
    buyer = models.ForeignKey(KeysDict, null=True, related_name='buyer_to_keys_dict')
    discount = models.FloatField(default=0)

class EmbeddingDebts(models.Model):
    em_date = models.DateField(db_index=True)
    sum = models.FloatField()
    description = models.CharField(max_length=1024, null=True)
    is_repaid = models.BooleanField(default=False)


