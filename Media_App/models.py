# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Households(models.Model):
    hid = models.IntegerField(db_column='hID', primary_key=True)  # Field name made lowercase.
    networth = models.IntegerField(db_column='netWorth', blank=True, null=True)  # Field name made lowercase.
    childrennum = models.IntegerField(db_column='ChildrenNum', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Households'


class Programranks(models.Model):
    title = models.OneToOneField('Programs', models.DO_NOTHING, db_column='title', primary_key=True)
    hid = models.ForeignKey(Households, models.DO_NOTHING, db_column='hID')  # Field name made lowercase.
    rank = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ProgramRanks'
        unique_together = (('title', 'hid'),)


class Programs(models.Model):
    title = models.CharField(primary_key=True, max_length=45)
    genre = models.CharField(max_length=25, blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Programs'


class Recordorders(models.Model):
    title = models.OneToOneField(Programs, models.DO_NOTHING, db_column='title', primary_key=True)
    hid = models.ForeignKey(Households, models.DO_NOTHING, db_column='hID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'RecordOrders'
        unique_together = (('title', 'hid'),)


class Recordreturns(models.Model):
    title = models.OneToOneField(Programs, models.DO_NOTHING, db_column='title', primary_key=True)
    hid = models.ForeignKey(Households, models.DO_NOTHING, db_column='hID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'RecordReturns'
        unique_together = (('title', 'hid'),)
