# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class BasConfig(models.Model):
    id = models.AutoField(primary_key=True)
    config_type = models.SmallIntegerField()
    config_object_id = models.IntegerField()
    param_name = models.CharField(max_length=50)
    param_type = models.SmallIntegerField()
    param_value = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    class Meta:
        db_table = u'bas_config'

class BasCluster(models.Model):
    id = models.AutoField(primary_key=True)
    cluster_name = models.CharField(max_length=255)
    cluster_sid = models.CharField(max_length=100)
    class Meta:
        db_table = u'bas_cluster'

class BasClusterNode(models.Model):
    id = models.AutoField(primary_key=True)
    cluster = models.ForeignKey(BasCluster)
    hostname = models.CharField(max_length=50)
    logic_name = models.CharField(max_length=255)
    datestart = models.DateTimeField()
    class Meta:
        db_table = u'bas_cluster_node'


class BasApplication(models.Model):
    id = models.IntegerField(primary_key=True)
    cluster = models.ForeignKey(BasCluster)
    app_name = models.CharField(max_length=50)
    app_version = models.CharField(max_length=20)
    control_flag = models.SmallIntegerField()
    active_flag = models.SmallIntegerField()
    deploy_datetime = models.DateTimeField()
    app_type = models.CharField(max_length=20)
    status = models.SmallIntegerField()
    class Meta:
        db_table = u'bas_application'

class BasAppStatistic(models.Model):
    id = models.IntegerField(primary_key=True)
    app = models.ForeignKey(BasApplication)
    node = models.ForeignKey(BasClusterNode)
    write_datetime = models.DateTimeField()
    in_count = models.IntegerField()
    out_count = models.IntegerField()
    err_count = models.IntegerField()
    class Meta:
        db_table = u'bas_app_statistic'

class BasAppMethod(models.Model):
    method_id = models.IntegerField(primary_key=True)
    application = models.ForeignKey(BasApplication)
    method_name = models.CharField(max_length=255)
    status = models.SmallIntegerField()
    class Meta:
        db_table = u'bas_app_method'

class BasAppMessage(models.Model):
    id = models.IntegerField(primary_key=True)
    method = models.ForeignKey(BasAppMethod)
    node = models.ForeignKey(BasClusterNode)
    datetime = models.DateTimeField()
    sender_host = models.CharField(max_length=50)
    message_type = models.IntegerField()
    message = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'bas_app_message'

class BasLog(models.Model):
    id = models.IntegerField(primary_key=True)
    node = models.ForeignKey(BasClusterNode)
    msg_datetime = models.DateTimeField()
    msg_level = models.SmallIntegerField()
    log_message = models.CharField(max_length=1024)
    class Meta:
        db_table = u'bas_log'

class BasUser(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    password_md5 = models.CharField(max_length=50)
    class Meta:
        db_table = u'bas_user'

class BasRole(models.Model):
    id = models.IntegerField(primary_key=True)
    role_name = models.CharField(max_length=255)
    role_sid = models.CharField(max_length=50)
    class Meta:
        db_table = u'bas_role'

class BasUserRoles(models.Model):
    user = models.ForeignKey(BasUser)
    role = models.ForeignKey(BasRole)
    class Meta:
        db_table = u'bas_user_roles'


