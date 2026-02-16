# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Aquifer(models.Model):
    aquiferid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey('Location', models.DO_NOTHING, db_column='bhid')
    depth1 = models.FloatField()
    depth2 = models.FloatField()
    aquifertypeid = models.ForeignKey('Aquifertype', models.DO_NOTHING, db_column='aquifertypeid')
    sampledate = models.DateTimeField()
    comment = models.TextField(blank=True, null=True)
    x1 = models.FloatField(blank=True, null=True)
    y1 = models.FloatField(blank=True, null=True)
    z1 = models.FloatField(blank=True, null=True)
    x2 = models.FloatField(blank=True, null=True)
    y2 = models.FloatField(blank=True, null=True)
    z2 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'aquifer'


class Aquifertype(models.Model):
    aquifertypeid = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    patterntypeid = models.IntegerField(blank=True, null=True)
    patternsize = models.FloatField(blank=True, null=True)
    patternthick = models.IntegerField(blank=True, null=True)
    background = models.IntegerField(blank=True, null=True)
    foreground = models.IntegerField(blank=True, null=True)
    fillpercent = models.IntegerField(blank=True, null=True)
    density = models.FloatField(blank=True, null=True)
    gvalue = models.FloatField()
    showinlegend = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'aquifertype'


class AuditLogs(models.Model):
    id = models.AutoField(primary_key=True)
    action = models.CharField(max_length=20)
    table_name = models.CharField(max_length=20)
    field = models.CharField(max_length=20)
    record_id = models.CharField(max_length=20)
    old_data = models.CharField(max_length=20)
    new_data = models.CharField(max_length=20, blank=True, null=True)
    changed_by = models.CharField(max_length=20, blank=True, null=True)
    changed_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'audit_logs'


class Bitmap(models.Model):
    bitmapid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey('Location', models.DO_NOTHING, db_column='bhid')
    depth1 = models.FloatField()
    depth2 = models.FloatField()
    bitmaptypeid = models.ForeignKey('Bitmaptype', models.DO_NOTHING, db_column='bitmaptypeid')
    header = models.IntegerField(blank=True, null=True)
    footer = models.IntegerField(blank=True, null=True)
    filename = models.CharField(max_length=255)
    depth1adj = models.FloatField(blank=True, null=True)
    depth2adj = models.FloatField(blank=True, null=True)
    bitmapwidth = models.IntegerField(blank=True, null=True)
    bitmapheight = models.IntegerField(blank=True, null=True)
    dataok = models.BooleanField(blank=True, null=True)
    x1 = models.FloatField(blank=True, null=True)
    y1 = models.FloatField(blank=True, null=True)
    z1 = models.FloatField(blank=True, null=True)
    x2 = models.FloatField(blank=True, null=True)
    y2 = models.FloatField(blank=True, null=True)
    z2 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bitmap'


class Bitmaptype(models.Model):
    bitmaptypeid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    patterntypeid = models.IntegerField(blank=True, null=True)
    patternsize = models.FloatField(blank=True, null=True)
    patternthick = models.IntegerField(blank=True, null=True)
    background = models.IntegerField(blank=True, null=True)
    foreground = models.IntegerField(blank=True, null=True)
    fillpercent = models.IntegerField(blank=True, null=True)
    density = models.FloatField(blank=True, null=True)
    gvalue = models.FloatField()
    showinlegend = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bitmaptype'


class BuoyMtcHistories(models.Model):
    id_buoy = models.ForeignKey('Buoys', models.DO_NOTHING, db_column='id_buoy', to_field='code_buoy')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'buoy_mtc_histories'


class BuoySensorHistories(models.Model):
    id_buoy = models.ForeignKey('Buoys', models.DO_NOTHING, db_column='id_buoy', to_field='code_buoy')
    salinitas = models.IntegerField(blank=True, null=True)
    turbidity = models.IntegerField(blank=True, null=True)
    current = models.IntegerField(blank=True, null=True)
    oxygen = models.IntegerField(blank=True, null=True)
    tide = models.IntegerField(blank=True, null=True)
    density = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'buoy_sensor_histories'


class Buoys(models.Model):
    id_site = models.ForeignKey('Sites', models.DO_NOTHING, db_column='id_site', to_field='code_site')
    code_buoy = models.CharField(unique=True, max_length=20)
    longitude = models.FloatField()
    latitude = models.FloatField()
    status = models.CharField(max_length=20, blank=True, null=True)
    last_mtc = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'buoys'


class ClientDepositHistories(models.Model):
    id_client = models.ForeignKey('Clients', models.DO_NOTHING, db_column='id_client', to_field='code_client')
    id_methodpay = models.ForeignKey('MethodPayments', models.DO_NOTHING, db_column='id_methodpay', to_field='code_methodpay')
    deposit = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'client_deposit_histories'


class Clients(models.Model):
    code_client = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=100)
    industry = models.CharField(max_length=20)
    region = models.CharField(max_length=20)
    deposit = models.DecimalField(max_digits=12, decimal_places=2)
    id_contact = models.ForeignKey('Contacts', models.DO_NOTHING, db_column='id_contact', to_field='code_contact')
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clients'


class Contacts(models.Model):
    code_contact = models.CharField(unique=True, max_length=20)
    phone = models.CharField(max_length=18, blank=True, null=True)
    email = models.CharField(max_length=255)
    mobile = models.CharField(max_length=18, blank=True, null=True)
    fax = models.CharField(max_length=18, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contacts'


class Fence(models.Model):
    fenceid = models.IntegerField(primary_key=True)
    x1 = models.FloatField()
    y1 = models.FloatField()
    x2 = models.FloatField()
    y2 = models.FloatField()

    class Meta:
        managed = False
        db_table = 'fence'


class Fracture(models.Model):
    fractureid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey('Location', models.DO_NOTHING, db_column='bhid')
    depth = models.FloatField()
    azimuth = models.FloatField()
    inclination = models.FloatField()
    radius = models.FloatField()
    aperture = models.FloatField()
    color = models.IntegerField()
    comment = models.CharField(max_length=255, blank=True, null=True)
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    z = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fracture'


class Hydrostratigraphy(models.Model):
    hydrostratid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey('Location', models.DO_NOTHING, db_column='bhid')
    depth1 = models.FloatField(blank=True, null=True)
    depth2 = models.FloatField(blank=True, null=True)
    hydrostrattypeid = models.ForeignKey('Hydrostrattype', models.DO_NOTHING, db_column='hydrostrattypeid')
    comment = models.TextField(blank=True, null=True)
    x1 = models.FloatField(blank=True, null=True)
    y1 = models.FloatField(blank=True, null=True)
    z1 = models.FloatField(blank=True, null=True)
    x2 = models.FloatField(blank=True, null=True)
    y2 = models.FloatField(blank=True, null=True)
    z2 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hydrostratigraphy'


class Hydrostrattype(models.Model):
    hydrostrattypeid = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    patterntypeid = models.IntegerField(blank=True, null=True)
    patternsize = models.FloatField(blank=True, null=True)
    patternthick = models.IntegerField(blank=True, null=True)
    background = models.IntegerField(blank=True, null=True)
    foreground = models.IntegerField(blank=True, null=True)
    fillpercent = models.IntegerField(blank=True, null=True)
    density = models.FloatField(blank=True, null=True)
    gvalue = models.FloatField()
    showinlegend = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hydrostrattype'


class Interval(models.Model):
    intervalid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey('Location', models.DO_NOTHING, db_column='bhid')
    intervaltypeid = models.ForeignKey('Intervaltype', models.DO_NOTHING, db_column='intervaltypeid')
    depth1 = models.FloatField(blank=True, null=True)
    depth2 = models.FloatField(blank=True, null=True)
    value = models.FloatField(blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)
    x1 = models.FloatField(blank=True, null=True)
    y1 = models.FloatField(blank=True, null=True)
    z1 = models.FloatField(blank=True, null=True)
    x2 = models.FloatField(blank=True, null=True)
    y2 = models.FloatField(blank=True, null=True)
    z2 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'interval'


class Intervaltype(models.Model):
    intervaltypeid = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    minvalue = models.FloatField(blank=True, null=True)
    maxvalue = models.FloatField(blank=True, null=True)
    units = models.CharField(max_length=10, blank=True, null=True)
    detectionlimit = models.FloatField(blank=True, null=True)
    rangechecking = models.BooleanField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    sortorder = models.FloatField(blank=True, null=True)
    page = models.IntegerField(blank=True, null=True)
    visible = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'intervaltype'


class Itext(models.Model):
    itextid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey('Location', models.DO_NOTHING, db_column='bhid')
    itexttypeid = models.ForeignKey('Itexttype', models.DO_NOTHING, db_column='itexttypeid')
    depth1 = models.FloatField(blank=True, null=True)
    depth2 = models.FloatField(blank=True, null=True)
    value = models.CharField(max_length=255, blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)
    x1 = models.FloatField(blank=True, null=True)
    y1 = models.FloatField(blank=True, null=True)
    z1 = models.FloatField(blank=True, null=True)
    x2 = models.FloatField(blank=True, null=True)
    y2 = models.FloatField(blank=True, null=True)
    z2 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'itext'


class Itexttype(models.Model):
    itexttypeid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=255, blank=True, null=True)
    sortorder = models.FloatField(blank=True, null=True)
    page = models.IntegerField(blank=True, null=True)
    visible = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'itexttype'


class Lithology(models.Model):
    lithid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey('Location', models.DO_NOTHING, db_column='bhid')
    depth1 = models.FloatField()
    depth2 = models.FloatField()
    lithtypeid = models.ForeignKey('Lithtype', models.DO_NOTHING, db_column='lithtypeid')
    comment = models.TextField(blank=True, null=True)
    x1 = models.FloatField(blank=True, null=True)
    y1 = models.FloatField(blank=True, null=True)
    z1 = models.FloatField(blank=True, null=True)
    x2 = models.FloatField(blank=True, null=True)
    y2 = models.FloatField(blank=True, null=True)
    z2 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lithology'


class Lithtype(models.Model):
    lithtypeid = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    patterntypeid = models.IntegerField(blank=True, null=True)
    patternsize = models.FloatField(blank=True, null=True)
    patternthick = models.IntegerField(blank=True, null=True)
    background = models.IntegerField(blank=True, null=True)
    foreground = models.IntegerField(blank=True, null=True)
    fillpercent = models.IntegerField(blank=True, null=True)
    density = models.FloatField(blank=True, null=True)
    gvalue = models.FloatField()
    showinlegend = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lithtype'


class Location(models.Model):
    bhid = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    enabled = models.BooleanField(blank=True, null=True)
    easting = models.FloatField()
    northing = models.FloatField()
    elevation = models.FloatField()
    totaldepth = models.FloatField()
    collarelevation = models.FloatField()
    comments = models.TextField(blank=True, null=True)
    geicon = models.IntegerField(blank=True, null=True)
    color = models.IntegerField(blank=True, null=True)
    symboltypeid = models.IntegerField(blank=True, null=True)
    needxyzcalc = models.BooleanField(blank=True, null=True)
    orientation = models.IntegerField(blank=True, null=True)
    dd_lon = models.FloatField(blank=True, null=True)
    dd_lat = models.FloatField(blank=True, null=True)
    lcs_x = models.FloatField(blank=True, null=True)
    lcs_y = models.FloatField(blank=True, null=True)
    lcs_unit = models.IntegerField(blank=True, null=True)
    pls_meridian = models.IntegerField(blank=True, null=True)
    pls_range = models.IntegerField(blank=True, null=True)
    pls_township = models.IntegerField(blank=True, null=True)
    pls_section = models.IntegerField(blank=True, null=True)
    pls_offset_based = models.BooleanField(blank=True, null=True)
    pls_x_offset = models.FloatField(blank=True, null=True)
    pls_y_offset = models.FloatField(blank=True, null=True)
    pls_fwl = models.BooleanField(blank=True, null=True)
    pls_fsl = models.BooleanField(blank=True, null=True)
    pls_description = models.CharField(max_length=255, blank=True, null=True)
    spc_zone = models.IntegerField(blank=True, null=True)
    spc_x = models.FloatField(blank=True, null=True)
    spc_y = models.FloatField(blank=True, null=True)
    spc_unit = models.IntegerField(blank=True, null=True)
    utm_datum = models.IntegerField(blank=True, null=True)
    utm_zone = models.IntegerField(blank=True, null=True)
    utm_x = models.FloatField(blank=True, null=True)
    utm_y = models.FloatField(blank=True, null=True)
    utm_unit = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'location'


class Lookuplists(models.Model):
    listid = models.IntegerField(primary_key=True)
    tablename = models.CharField(max_length=255)
    fieldname = models.CharField(max_length=255)
    listvalue = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'lookuplists'
        unique_together = (('tablename', 'fieldname', 'listvalue'),)


class MethodPayments(models.Model):
    code_methodpay = models.CharField(unique=True, max_length=20)
    transaction_name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'method_payments'


class OrderDetails(models.Model):
    id_order = models.ForeignKey('Orders', models.DO_NOTHING, db_column='id_order', to_field='code_order')
    id_vessel = models.ForeignKey('Vessels', models.DO_NOTHING, db_column='id_vessel', to_field='code_vessel')
    code_task = models.CharField(unique=True, max_length=20)
    sand_quantity = models.IntegerField(blank=True, null=True)
    clay_quantity = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_details'


class Orders(models.Model):
    id_client = models.ForeignKey(Clients, models.DO_NOTHING, db_column='id_client', to_field='code_client')
    code_order = models.CharField(unique=True, max_length=20)
    order_date = models.DateTimeField()
    required_delivery_date = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(max_length=20, blank=True, null=True)
    quantity = models.IntegerField()
    special_requirements = models.TextField(blank=True, null=True)
    scheduled_delivery_date = models.DateTimeField(blank=True, null=True)
    actual_delivery_date = models.DateTimeField()
    destination = models.CharField(max_length=20)
    destination_longitude = models.FloatField()
    destination_latitude = models.FloatField()
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orders'


class Orientation(models.Model):
    orientationid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey(Location, models.DO_NOTHING, db_column='bhid', related_name='orientation_records')
    depth = models.FloatField()
    azimuth = models.FloatField()
    inclination = models.FloatField()

    class Meta:
        managed = False
        db_table = 'orientation'


class Ouroboros(models.Model):
    ouroborosid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey(Location, models.DO_NOTHING, db_column='bhid')
    depth = models.FloatField(blank=True, null=True)
    azimuth = models.FloatField(blank=True, null=True)
    inclination = models.FloatField(blank=True, null=True)
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    z = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ouroboros'


class Parameters(models.Model):
    parent_desc = models.CharField(max_length=20, blank=True, null=True)
    kode_desc = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'parameters'


class Partners(models.Model):
    id_contact = models.ForeignKey(Contacts, models.DO_NOTHING, db_column='id_contact', to_field='code_contact')
    code_partner = models.CharField(unique=True, max_length=20, blank=True, null=True)
    name = models.CharField(max_length=100)
    industry = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'partners'


class Pattern(models.Model):
    patternid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey(Location, models.DO_NOTHING, db_column='bhid')
    depth1 = models.FloatField()
    depth2 = models.FloatField()
    patterntypeid = models.IntegerField(blank=True, null=True)
    patternsize = models.FloatField(blank=True, null=True)
    patternthick = models.IntegerField(blank=True, null=True)
    background = models.IntegerField(blank=True, null=True)
    foreground = models.IntegerField(blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)
    x1 = models.FloatField(blank=True, null=True)
    y1 = models.FloatField(blank=True, null=True)
    z1 = models.FloatField(blank=True, null=True)
    x2 = models.FloatField(blank=True, null=True)
    y2 = models.FloatField(blank=True, null=True)
    z2 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pattern'


class PaymentDetails(models.Model):
    id_payment = models.ForeignKey('Payments', models.DO_NOTHING, db_column='id_payment', to_field='code_payment')
    doc_no = models.CharField(max_length=20)
    tax = models.IntegerField(blank=True, null=True)
    exchange_rate = models.IntegerField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment_details'


class Payments(models.Model):
    id_client = models.ForeignKey(Clients, models.DO_NOTHING, db_column='id_client', to_field='code_client')
    id_order = models.ForeignKey(Orders, models.DO_NOTHING, db_column='id_order', to_field='code_order')
    id_methodpay = models.ForeignKey(MethodPayments, models.DO_NOTHING, db_column='id_methodpay', to_field='code_methodpay')
    code_payment = models.CharField(unique=True, max_length=20)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField()
    payment_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payments'


class Point(models.Model):
    pointid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey(Location, models.DO_NOTHING, db_column='bhid')
    pointtypeid = models.ForeignKey('Pointtype', models.DO_NOTHING, db_column='pointtypeid')
    depth = models.FloatField()
    value = models.FloatField()
    comment = models.CharField(max_length=255, blank=True, null=True)
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    z = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'point'


class Pointtype(models.Model):
    pointtypeid = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    minvalue = models.FloatField(blank=True, null=True)
    maxvalue = models.FloatField(blank=True, null=True)
    units = models.CharField(max_length=10, blank=True, null=True)
    detectionlimit = models.FloatField(blank=True, null=True)
    rangechecking = models.BooleanField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    sortorder = models.FloatField(blank=True, null=True)
    page = models.IntegerField(blank=True, null=True)
    visible = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pointtype'


class Projectdesc(models.Model):
    projectdescid = models.IntegerField(primary_key=True)
    projdesc = models.BinaryField(blank=True, null=True)
    dlgtop = models.IntegerField(blank=True, null=True)
    dlgleft = models.IntegerField(blank=True, null=True)
    dlgheight = models.IntegerField(blank=True, null=True)
    dlgwidth = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'projectdesc'


class Projectinfo(models.Model):
    projectinfoid = models.IntegerField(primary_key=True)
    item = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    value = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'projectinfo'
        unique_together = (('category', 'item'),)


class Projecttables(models.Model):
    projecttablesid = models.IntegerField(primary_key=True)
    tabletype = models.CharField(max_length=50)
    tablename = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'projecttables'
        unique_together = (('tabletype', 'tablename'),)


class Ptext(models.Model):
    ptextid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey(Location, models.DO_NOTHING, db_column='bhid')
    ptexttypeid = models.ForeignKey('Ptexttype', models.DO_NOTHING, db_column='ptexttypeid')
    depth = models.FloatField()
    value = models.CharField(max_length=255)
    comment = models.CharField(max_length=255, blank=True, null=True)
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    z = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ptext'


class Ptexttype(models.Model):
    ptexttypeid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=255, blank=True, null=True)
    sortorder = models.FloatField(blank=True, null=True)
    page = models.IntegerField(blank=True, null=True)
    visible = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ptexttype'


class Rockcolor(models.Model):
    rockcolorid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey(Location, models.DO_NOTHING, db_column='bhid')
    depth1 = models.FloatField()
    depth2 = models.FloatField()
    color = models.IntegerField()
    colortext = models.CharField(max_length=255, blank=True, null=True)
    x1 = models.FloatField(blank=True, null=True)
    y1 = models.FloatField(blank=True, null=True)
    z1 = models.FloatField(blank=True, null=True)
    x2 = models.FloatField(blank=True, null=True)
    y2 = models.FloatField(blank=True, null=True)
    z2 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rockcolor'


class SampleLogDetails(models.Model):
    id_term = models.ForeignKey('TermDesc', models.DO_NOTHING, db_column='id_term', to_field='code_term')
    id_lithology = models.ForeignKey('SoilDesc', models.DO_NOTHING, db_column='id_lithology', to_field='code_lithology')
    doc_no = models.ForeignKey('SampleLogs', models.DO_NOTHING, db_column='doc_no', to_field='doc_no')
    sample_depth_start = models.IntegerField()
    sample_depth_end = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    torvane = models.IntegerField(blank=True, null=True)
    penetrometer = models.IntegerField(blank=True, null=True)
    penetration = models.IntegerField()
    sequence = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sample_log_details'


class SampleLogs(models.Model):
    id_vessel = models.CharField(max_length=20)
    id_surveyor = models.CharField(max_length=20)
    id_captain = models.CharField(max_length=20)
    id_site = models.CharField(max_length=20)
    doc_no = models.CharField(unique=True, max_length=20)
    log_date = models.DateField()
    sample_type = models.CharField(max_length=20)
    total_sample = models.IntegerField(blank=True, null=True)
    packages_number = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sample_logs'


class Section(models.Model):
    sectionid = models.IntegerField(primary_key=True)
    x = models.FloatField()
    y = models.FloatField()

    class Meta:
        managed = False
        db_table = 'section'


class Sites(models.Model):
    code_site = models.CharField(unique=True, max_length=20)
    type = models.CharField(max_length=20)
    location = models.TextField()
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    zip = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=20)
    port = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sites'


class SoilDesc(models.Model):
    code_lithology = models.CharField(unique=True, max_length=20)
    soil_type = models.CharField(max_length=20, blank=True, null=True)
    soil_name = models.CharField(max_length=20)
    gr_size = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'soil_desc'


class Stratigraphy(models.Model):
    stratid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey(Location, models.DO_NOTHING, db_column='bhid')
    depth1 = models.FloatField(blank=True, null=True)
    depth2 = models.FloatField(blank=True, null=True)
    strattypeid = models.ForeignKey('Strattype', models.DO_NOTHING, db_column='strattypeid')
    d1dipdirection = models.FloatField(blank=True, null=True)
    d1dipangle = models.FloatField(blank=True, null=True)
    d2dipdirection = models.FloatField(blank=True, null=True)
    d2dipangle = models.FloatField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    x1 = models.FloatField(blank=True, null=True)
    y1 = models.FloatField(blank=True, null=True)
    z1 = models.FloatField(blank=True, null=True)
    x2 = models.FloatField(blank=True, null=True)
    y2 = models.FloatField(blank=True, null=True)
    z2 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stratigraphy'


class Strattype(models.Model):
    strattypeid = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    patterntypeid = models.IntegerField(blank=True, null=True)
    patternsize = models.FloatField(blank=True, null=True)
    patternthick = models.IntegerField(blank=True, null=True)
    background = models.IntegerField(blank=True, null=True)
    foreground = models.IntegerField(blank=True, null=True)
    fillpercent = models.IntegerField(blank=True, null=True)
    density = models.FloatField(blank=True, null=True)
    gvalue = models.FloatField()
    showinlegend = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'strattype'


class Surveis(models.Model):
    id_site = models.CharField(max_length=20)
    id_surveyor = models.CharField(max_length=20)
    code_survey = models.CharField(unique=True, max_length=20)
    doc_no = models.CharField(max_length=20)
    core_no = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'surveis'


class SurveyDetails(models.Model):
    id_survey = models.ForeignKey(Surveis, models.DO_NOTHING, db_column='id_survey', to_field='code_survey')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'survey_details'


class Symbol(models.Model):
    symbolid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey(Location, models.DO_NOTHING, db_column='bhid')
    depth = models.FloatField()
    comment = models.CharField(max_length=255, blank=True, null=True)
    symboltypeid = models.IntegerField(blank=True, null=True)
    color = models.IntegerField(blank=True, null=True)
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    z = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'symbol'


class SystemSettings(models.Model):
    key = models.CharField(primary_key=True, max_length=50)
    value = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'system_settings'


class T3Dpointmaprange(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    minimum = models.FloatField(blank=True, null=True)
    maximum = models.FloatField(blank=True, null=True)
    displaysize = models.FloatField(blank=True, null=True)
    color = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't3dpointmaprange'


class Tbargraphscale(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    minvalue = models.FloatField(blank=True, null=True)
    maxvalue = models.FloatField(blank=True, null=True)
    displaysize = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbargraphscale'


class Tcolorindex(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    color = models.IntegerField(blank=True, null=True)
    caption = models.CharField(max_length=60, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tcolorindex'


class Tcontour(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    level = models.FloatField(blank=True, null=True)
    linestyle = models.IntegerField(blank=True, null=True)
    linewidth = models.IntegerField(blank=True, null=True)
    linecolor = models.IntegerField(blank=True, null=True)
    label = models.CharField(max_length=60, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tcontour'


class Tdwgriddingsector(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    minangle = models.IntegerField(blank=True, null=True)
    maxangle = models.IntegerField(blank=True, null=True)
    exponent = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tdwgriddingsector'


class TermDesc(models.Model):
    code_term = models.CharField(unique=True, max_length=20)
    term = models.CharField(max_length=20)
    compactness = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'term_desc'


class Tfaults(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    x1 = models.FloatField(blank=True, null=True)
    y1 = models.FloatField(blank=True, null=True)
    x2 = models.FloatField(blank=True, null=True)
    y2 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tfaults'


class Tidwsolidmodelingsec(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    mininclination = models.FloatField(blank=True, null=True)
    maxinclination = models.FloatField(blank=True, null=True)
    minazimuth = models.FloatField(blank=True, null=True)
    maxazimuth = models.FloatField(blank=True, null=True)
    maxdistance = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tidwsolidmodelingsec'


class Tlinestyleindex(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    linestyle = models.IntegerField(blank=True, null=True)
    linewidth = models.IntegerField(blank=True, null=True)
    linecolor = models.IntegerField(blank=True, null=True)
    caption = models.CharField(max_length=60, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tlinestyleindex'


class Tminmaxcolor(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    minvalue = models.FloatField(blank=True, null=True)
    maxvalue = models.FloatField(blank=True, null=True)
    color = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tminmaxcolor'


class Tminterval(models.Model):
    tmintervalid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey(Location, models.DO_NOTHING, db_column='bhid')
    tmintervaltypeid = models.ForeignKey('Tmintervaltype', models.DO_NOTHING, db_column='tmintervaltypeid')
    depth1 = models.FloatField(blank=True, null=True)
    depth2 = models.FloatField(blank=True, null=True)
    sampledate = models.DateTimeField(blank=True, null=True)
    value = models.FloatField(blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)
    x1 = models.FloatField(blank=True, null=True)
    y1 = models.FloatField(blank=True, null=True)
    z1 = models.FloatField(blank=True, null=True)
    x2 = models.FloatField(blank=True, null=True)
    y2 = models.FloatField(blank=True, null=True)
    z2 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tminterval'


class Tmintervaltype(models.Model):
    tmintervaltypeid = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    minvalue = models.FloatField(blank=True, null=True)
    maxvalue = models.FloatField(blank=True, null=True)
    units = models.CharField(max_length=10, blank=True, null=True)
    detectionlimit = models.FloatField(blank=True, null=True)
    rangechecking = models.BooleanField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    sortorder = models.FloatField(blank=True, null=True)
    page = models.IntegerField(blank=True, null=True)
    visible = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tmintervaltype'


class Tpatternindex(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    patterntypeid = models.IntegerField(blank=True, null=True)
    patternsize = models.FloatField(blank=True, null=True)
    patternthick = models.IntegerField(blank=True, null=True)
    background = models.IntegerField(blank=True, null=True)
    foreground = models.IntegerField(blank=True, null=True)
    caption = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tpatternindex'


class Tpointmaprange(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    minimum = models.FloatField(blank=True, null=True)
    maximum = models.FloatField(blank=True, null=True)
    symboltypeid = models.IntegerField(blank=True, null=True)
    color = models.IntegerField(blank=True, null=True)
    displaysize = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tpointmaprange'


class Tpolygon(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tpolygon'


class Tpolygons(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    linestyle = models.IntegerField(blank=True, null=True)
    linewidth = models.IntegerField(blank=True, null=True)
    linecolor = models.IntegerField(blank=True, null=True)
    patterntypeid = models.IntegerField(blank=True, null=True)
    patternsize = models.FloatField(blank=True, null=True)
    patternthick = models.IntegerField(blank=True, null=True)
    background = models.IntegerField(blank=True, null=True)
    foreground = models.IntegerField(blank=True, null=True)
    caption = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tpolygons'
        unique_together = (('projecttablesid', 'caption'),)


class Tprofile(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    x1 = models.FloatField(blank=True, null=True)
    y1 = models.FloatField(blank=True, null=True)
    x2 = models.FloatField(blank=True, null=True)
    y2 = models.FloatField(blank=True, null=True)
    swath = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tprofile'


class Tsymbolindex(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    symboltypeid = models.IntegerField(blank=True, null=True)
    color = models.IntegerField(blank=True, null=True)
    caption = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tsymbolindex'


class Tsynonym(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    target = models.CharField(max_length=255, blank=True, null=True)
    replacement = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tsynonym'


class Txycoordinate(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'txycoordinate'


class Txypair(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    x1 = models.FloatField(blank=True, null=True)
    y1 = models.FloatField(blank=True, null=True)
    x2 = models.FloatField(blank=True, null=True)
    y2 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'txypair'


class Txyz(models.Model):
    id = models.IntegerField(primary_key=True)
    projecttablesid = models.ForeignKey(Projecttables, models.DO_NOTHING, db_column='projecttablesid')
    sortorder = models.FloatField()
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    z = models.FloatField(blank=True, null=True)
    comment = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'txyz'


class UserManagements(models.Model):
    id_user = models.ForeignKey('Users', models.DO_NOTHING, db_column='id_user', to_field='code_user')
    password = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    last_login = models.DateTimeField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_managements'


class Users(models.Model):
    id_contact = models.ForeignKey(Contacts, models.DO_NOTHING, db_column='id_contact', to_field='code_contact')
    code_user = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=100)
    citizen = models.CharField(max_length=20)
    role = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    organs = models.CharField(max_length=20)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'


class Vector(models.Model):
    vectorid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey(Location, models.DO_NOTHING, db_column='bhid')
    depth = models.FloatField()
    azimuth = models.FloatField()
    inclination = models.FloatField()
    color = models.IntegerField()
    value = models.FloatField()
    comment = models.CharField(max_length=255, blank=True, null=True)
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    z = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vector'


class VesselActivities(models.Model):
    id_vessel = models.ForeignKey('Vessels', models.DO_NOTHING, db_column='id_vessel', to_field='code_vessel')
    id_order = models.ForeignKey(Orders, models.DO_NOTHING, db_column='id_order', to_field='code_order', blank=True, null=True)
    id_task = models.ForeignKey(OrderDetails, models.DO_NOTHING, db_column='id_task', to_field='code_task', blank=True, null=True)
    seq_activity = models.CharField(unique=True, max_length=20)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    estimate_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vessel_activities'


class VesselCrews(models.Model):
    id_user = models.ForeignKey(Users, models.DO_NOTHING, db_column='id_user', to_field='code_user', blank=True, null=True)
    id_vessel = models.ForeignKey('Vessels', models.DO_NOTHING, db_column='id_vessel', to_field='code_vessel')
    status = models.CharField(max_length=20, blank=True, null=True)
    flag = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vessel_crews'


class VesselDetails(models.Model):
    id_vessel = models.ForeignKey('Vessels', models.DO_NOTHING, db_column='id_vessel', to_field='code_vessel')
    picture = models.CharField(max_length=20, blank=True, null=True)
    gross_tonnage = models.IntegerField(blank=True, null=True)
    net_tonnage = models.IntegerField(blank=True, null=True)
    deadweight_tonnage = models.IntegerField(blank=True, null=True)
    length_overall = models.IntegerField(blank=True, null=True)
    beam = models.IntegerField(blank=True, null=True)
    draft = models.IntegerField(blank=True, null=True)
    depth_details = models.IntegerField(blank=True, null=True)
    special_features = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vessel_details'


class VesselPositions(models.Model):
    id_vessel = models.ForeignKey('Vessels', models.DO_NOTHING, db_column='id_vessel', to_field='code_vessel')
    seq_activity = models.ForeignKey(VesselActivities, models.DO_NOTHING, db_column='seq_activity', to_field='seq_activity')
    longitude = models.FloatField()
    latitude = models.FloatField()
    speed = models.IntegerField(blank=True, null=True)
    heading = models.IntegerField(blank=True, null=True)
    note = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vessel_positions'


class Vessels(models.Model):
    id_partner = models.ForeignKey(Partners, models.DO_NOTHING, db_column='id_partner', to_field='code_partner')
    code_vessel = models.CharField(unique=True, max_length=20)
    flag = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vessels'


class VibrocoreLogDetails(models.Model):
    id_term = models.ForeignKey(TermDesc, models.DO_NOTHING, db_column='id_term', to_field='code_term')
    doc_no = models.ForeignKey('VibrocoreLogs', models.DO_NOTHING, db_column='doc_no', to_field='doc_no')
    code_lithology = models.ForeignKey(SoilDesc, models.DO_NOTHING, db_column='code_lithology', to_field='code_lithology')
    sample_depth_start = models.IntegerField()
    sample_depth_end = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    torvane = models.IntegerField(blank=True, null=True)
    penetrometer = models.IntegerField(blank=True, null=True)
    penetration = models.IntegerField()
    sequence = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vibrocore_log_details'


class VibrocoreLogs(models.Model):
    id_site = models.CharField(max_length=20)
    id_client = models.CharField(max_length=20)
    id_user = models.CharField(max_length=20)
    id_core = models.CharField(max_length=20)
    doc_no = models.CharField(unique=True, max_length=20)
    total_sample_depth = models.IntegerField()
    total_attempt = models.IntegerField()
    barrel_length = models.IntegerField()
    penetration = models.IntegerField()
    recovery = models.IntegerField()
    heading = models.IntegerField()
    time = models.TimeField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    water_depth = models.IntegerField()
    total_soil = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vibrocore_logs'


class Wellconstruction(models.Model):
    wellconstructionid = models.IntegerField(primary_key=True)
    bhid = models.ForeignKey(Location, models.DO_NOTHING, db_column='bhid')
    offset = models.FloatField(db_column='Offset', blank=True, null=True)  # Field name made lowercase.
    depth1 = models.FloatField()
    depth2 = models.FloatField()
    diameter1 = models.FloatField()
    diameter2 = models.FloatField()
    wellconsttypeid = models.ForeignKey('Wellconstructiontype', models.DO_NOTHING, db_column='wellconsttypeid')
    comment = models.TextField(db_column='Comment', blank=True, null=True)  # Field name made lowercase.
    x1 = models.FloatField(blank=True, null=True)
    y1 = models.FloatField(blank=True, null=True)
    z1 = models.FloatField(blank=True, null=True)
    x2 = models.FloatField(blank=True, null=True)
    y2 = models.FloatField(blank=True, null=True)
    z2 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wellconstruction'


class Wellconstructiontype(models.Model):
    wellconsttypeid = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    patterntypeid = models.IntegerField(blank=True, null=True)
    patternsize = models.FloatField(blank=True, null=True)
    patternthick = models.IntegerField(blank=True, null=True)
    background = models.IntegerField(blank=True, null=True)
    foreground = models.IntegerField(blank=True, null=True)
    fillpercent = models.IntegerField(blank=True, null=True)
    density = models.FloatField(blank=True, null=True)
    gvalue = models.FloatField()
    showinlegend = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wellconstructiontype'


class Wellpick(models.Model):
    wellpickid = models.IntegerField(primary_key=True)
    bhid = models.OneToOneField(Location, models.DO_NOTHING, db_column='bhid')

    class Meta:
        managed = False
        db_table = 'wellpick'
