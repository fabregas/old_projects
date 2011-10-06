# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models


class NmUser(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    password_hash = models.CharField(max_length=50)
    email_address = models.CharField(max_length=128)
    additional_info = models.CharField(max_length=1024)
    class Meta:
        db_table = u'nm_user'

class NmClusterType(models.Model):
    id = models.AutoField(primary_key=True)
    type_sid = models.CharField(unique=True, max_length=128)
    description = models.CharField(max_length=1024)
    class Meta:
        db_table = u'nm_cluster_type'

class NmConfigSpec(models.Model):
    id = models.AutoField(primary_key=True)
    config_object = models.SmallIntegerField()
    object_type_id = models.BigIntegerField()
    parameter_name = models.CharField(max_length=128)
    parameter_type = models.SmallIntegerField()
    posible_values_list = models.TextField()
    default_value = models.CharField(max_length=1024)
    class Meta:
        db_table = u'nm_config_spec'

class NmCluster(models.Model):
    id = models.AutoField(primary_key=True)
    cluster_sid = models.CharField(unique=True, max_length=50)
    cluster_type = models.ForeignKey(NmClusterType, db_column='cluster_type')
    cluster_name = models.CharField(max_length=255)
    description = models.CharField(max_length=1024)
    organization = models.CharField(max_length=100)
    status = models.SmallIntegerField()
    last_modifier_id = models.BigIntegerField()
    dc = models.DateTimeField()
    dm = models.DateTimeField()
    class Meta:
        db_table = u'nm_cluster'

class NmNodeType(models.Model):
    id = models.AutoField(primary_key=True)
    type_sid = models.CharField(unique=True, max_length=128)
    description = models.CharField(max_length=1024)
    class Meta:
        db_table = u'nm_node_type'

class NmNode(models.Model):
    id = models.AutoField(primary_key=True)
    node_uuid = models.CharField(unique=True, max_length=50)
    cluster = models.ForeignKey(NmCluster)
    node_type = models.ForeignKey(NmNodeType, db_column='node_type')
    hostname = models.CharField(unique=True, max_length=50)
    logic_name = models.CharField(max_length=128)
    admin_status = models.SmallIntegerField()
    current_state = models.SmallIntegerField()
    last_datestart = models.DateTimeField()
    login = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    last_modifier_id = models.BigIntegerField()
    hw_info = models.TextField()
    sw_info = models.TextField()
    dc = models.DateTimeField()
    dm = models.DateTimeField()
    mac_address = models.CharField(max_length=20)
    ip_address = models.CharField(max_length=20)
    architecture = models.CharField(max_length=10)
    class Meta:
        db_table = u'nm_node'


class NmRole(models.Model):
    id = models.AutoField(primary_key=True)
    role_sid = models.CharField(max_length=50)
    role_name = models.CharField(max_length=128)
    class Meta:
        db_table = u'nm_role'

class NmUserRole(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(NmUser)
    role = models.ForeignKey(NmRole)
    class Meta:
        db_table = u'nm_user_role'

class NmConfig(models.Model):
    id = models.AutoField(primary_key=True)
    object_id = models.BigIntegerField()
    parameter = models.ForeignKey(NmConfigSpec)
    parameter_value = models.CharField(max_length=1024)
    last_midifier = models.ForeignKey(NmUser)
    dc = models.DateTimeField()
    dm = models.DateTimeField()
    class Meta:
        db_table = u'nm_config'


class NmOperation(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=128)
    timeout = models.BigIntegerField()
    node_type = models.ForeignKey(NmNodeType)
    description = models.CharField(max_length=1024)
    class Meta:
        db_table = u'nm_operation'

class NmOperationInstance(models.Model):
    id = models.AutoField(primary_key=True)
    operation = models.ForeignKey(NmOperation)
    initiator = models.ForeignKey(NmUser)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.SmallIntegerField()
    class Meta:
        db_table = u'nm_operation_instance'

class NmOperationProgress(models.Model):
    id = models.AutoField(primary_key=True)
    node = models.ForeignKey(NmNode)
    instance = models.ForeignKey(NmOperationInstance)
    progress = models.SmallIntegerField()
    ret_code = models.SmallIntegerField()
    ret_message = models.CharField(max_length=1024)
    end_datetime = models.DateTimeField()
    class Meta:
        db_table = u'nm_operation_progress'

