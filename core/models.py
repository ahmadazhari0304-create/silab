# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Bhp(models.Model):
    nama_barang = models.TextField()
    praktikum = models.TextField()
    jumlah = models.IntegerField()
    tanggal = models.DateField()
    prodi = models.TextField()
    user = models.ForeignKey('Users', models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bhp'


class Bookings(models.Model):
    nama_lab = models.TextField()
    tanggal = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    kelas = models.TextField()
    prodi = models.TextField()
    tujuan = models.TextField()
    user = models.ForeignKey('Users', models.CASCADE, blank=True, null=True)
    status = models.TextField()

    class Meta:
        managed = False
        db_table = 'bookings'


class Items(models.Model):
    nama_barang = models.TextField()
    value = models.TextField()

    class Meta:
        managed = False
        db_table = 'items'


class Labs(models.Model):
    nama_lab = models.TextField()
    status = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'labs'


class Maintenance(models.Model):
    nama_lab = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    keterangan = models.TextField()
    user = models.ForeignKey('Users', models.CASCADE)

    class Meta:
        managed = False
        db_table = 'maintenance'


class Sops(models.Model):
    title = models.TextField()
    category = models.TextField()
    filename = models.TextField()
    user = models.ForeignKey('Users', models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sops'


class Users(models.Model):
    username = models.TextField(unique=True)
    password_hash = models.TextField()
    is_admin = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'

class SopCategories(models.Model):
    name = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = 'sop_categories'
