from django.db import models


class RPUser(models.Model):
    id = models.AutoField(primary_key=True)
    login = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    password_md5 = models.CharField(max_length=50)
    role = models.CharField(max_length=10)
    #birthday = models.DateField(blank=True)
    email = models.CharField(max_length=255)
    region = models.CharField(max_length=128)
    city = models.CharField(max_length=128)

    balance = models.IntegerField()

    class Meta:
        db_table = u'rp_user'

class RPPayments(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(RPUser)
    money =  models.IntegerField() # in grn.
    transaction_start = models.DateTimeField()
    transaction_end = models.DateTimeField(null=True)
    status = models.IntegerField() #INIT=0, WAIT=1, OK=2, FAIL=3 
    phone_number = models.CharField(max_length=15, null=True)

    class Meta:
        db_table = u'rp_payment'


class RPService(models.Model):
    name = models.CharField(max_length=1024)
    time_min = models.IntegerField() #minutes
    time_max = models.IntegerField() #minutes
    atom_money = models.IntegerField()
    description = models.TextField()
    is_deleted = models.IntegerField(default=0)

    name_ru = models.CharField(max_length=1024)
    description_ru = models.TextField()

    class Meta:
        db_table = u'rp_service'

class RPRecord(models.Model):
    user = models.ForeignKey(RPUser)
    service = models.ForeignKey(RPService)
    start_datetime = models.DateTimeField()
    stop_datetime = models.DateTimeField()
    comment = models.CharField(max_length=1024)

    class Meta:
        db_table = u'rp_record'

class RPWorkTime(models.Model):
    start_worktime = models.DateTimeField()
    stop_worktime = models.DateTimeField()

    class Meta:
        db_table = u'rp_worktime'

class RPMessage(models.Model):
    binded_user = models.ForeignKey(RPUser, null=True)
    sender = models.ForeignKey(RPUser, related_name='rp_sender_user', null=True)
    send_datetime =  models.DateTimeField()
    message = models.TextField()
    is_readed = models.IntegerField()

    class Meta:
        db_table = u'rp_message'
