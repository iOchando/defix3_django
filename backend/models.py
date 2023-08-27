from cgi import test
# from tkinter import CASCADE
from django.db import models
from django.forms import DateField, DateTimeField
from django.db.models.signals import post_save
from django.contrib.auth.models import *
from datetime import datetime
from decimal import Decimal

# Create your models here.


class Cryptocurrency(models.Model):
    coin = models.CharField(max_length=32, null=False,
                            blank=False, unique=True)
    nombre = models.CharField(max_length=255, null=False, blank=False)
    blockchain = models.CharField(max_length=255, null=False, blank=False)
    icon = models.ImageField(upload_to='media/icons',
                             null=True, help_text="icon Crypto")
    swap = models.BooleanField(default=False, help_text="swap habilitado?")
    bridge = models.BooleanField(default=False, help_text="bridge habilitado?")
    limit_order = models.BooleanField(
        default=False, help_text="limit habilitado?")
    time_transaction = models.IntegerField(
        null=True, blank=True, help_text="time in seconds")

    def __str__(self):
        return '%s' % (self.coin)


class Token(models.Model):
    cryptocurrency = models.ForeignKey(
        Cryptocurrency, null=False, blank=False, on_delete=models.CASCADE)
    coin = models.CharField(max_length=32, null=False, blank=False)
    contract = models.CharField(max_length=255, null=False, blank=False)
    decimals = models.IntegerField(null=True, blank=True)
    icon = models.ImageField(upload_to='media/icons',
                             null=True, help_text="icon Crypto")

    def __str__(self):
        return '%s - %s' % (self.coin, self.cryptocurrency.blockchain)


class Perfil(models.Model):
    TIPO = (('S', 'Super'), ('A', 'Admin'),
            ('U', 'Usuario'), ('B', 'Banco'), ('D', 'Defix'))
    usuario = models.OneToOneField(
        User, on_delete=models.CASCADE, help_text="usuario asociado")
    activo = models.BooleanField(
        default=True, help_text="esta el usuario activo?")
    # avatar=models.ImageField(upload_to='avatars',null=True,help_text="avatar para el usuario")
    tipo = models.CharField(
        max_length=1, null=True, choices=TIPO, default='U', help_text="Tipo de usuario")

    def __str__(self):
        return '%s - %s' % (self.usuario.username, self.tipo)


class tUserFiat(models.Model):
    usuario = models.OneToOneField(
        User, on_delete=models.CASCADE, help_text="usuario asociado")
    activo = models.BooleanField(
        default=True, help_text="esta el token activo?")
    referido = models.CharField(max_length=255, null=False, blank=False)
    tokenemail = models.CharField(max_length=255, null=False, blank=False)
    creacion = models.DateTimeField(
        default=datetime.now, blank=True, help_text="fecha de creacion de token")

    def __str__(self):
        return '%s - %s - %s' % (self.usuario.username, self.tokenemail, self.creacion)


class Modulo(models.Model):
    nombre = models.CharField(
        max_length=255, null=False, blank=False, primary_key=True)
    # mayor=models.ForeignKey('self',default=None,null=True, on_delete=models.SET_DEFAULT)

    def __str__(self):
        return '%s' % (self.nombre)


class Permiso(models.Model):
    modulo = models.ForeignKey(Modulo, null=False, blank=False,
                               on_delete=models.CASCADE, help_text="Opcion de menu asociada")
    perfil = models.ForeignKey(Perfil, null=False, blank=False,
                               on_delete=models.CASCADE, help_text="Usuario asociado")
    # Metodos
    leer = models.BooleanField(
        default=False, help_text="Tiene opcion de leer?")
    escribir = models.BooleanField(
        default=False, help_text="Tiene opcion de escribir?")
    borrar = models.BooleanField(
        default=False, help_text="Tiene opcion de borrar?")
    actualizar = models.BooleanField(
        default=False, help_text="Tiene opcion de actualizar?")

    # def save(self):
    #     if not Permiso.objects.filter(perfil=self.perfil_id,da=self.menuinstancia_id):
    #         super().save()
    def __str__(self):
        return '%s (Permiso: %s - Leer:%s Borrar:%s Actualizar:%s Escribir:%s)' % (self.perfil.usuario.username, self.modulo.nombre, self.leer, self.borrar, self.actualizar, self.escribir)


class Comision(models.Model):
    coin = models.CharField(max_length=32, null=False,
                            blank=False, primary_key=True)
    nombre = models.CharField(max_length=255, null=False, blank=False)
    blockchain = models.CharField(max_length=255, null=False, blank=False)
    transfer = models.FloatField(null=False, blank=False)
    swap = models.FloatField(null=False, blank=False)
    fiat = models.FloatField(null=False, blank=False)

    def __str__(self):
        return '%s' % (self.coin)


class Banco(models.Model):
    nombre = models.CharField(
        max_length=255, null=False, blank=False, default='')

    def __str__(self):
        return '%s' % (self.nombre)


class tPais(models.Model):
    nombre = models.TextField(
        max_length=120, null=False, blank=False, help_text="Nombre Pais")
    coin = models.TextField(max_length=120, null=True,
                            blank=True, help_text="Mondeda del Pais")
    imagen = models.ImageField(
        upload_to='media/paises', null=True, blank=True, help_text="Imagen asociado al pais")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")
    kycventa = models.BooleanField(
        default=True, help_text="valida KYC en venta?")
    kyccompra = models.BooleanField(
        default=True, help_text="valida KYC en compra?")
    tasa = models.TextField(max_length=120, null=True,
                            blank=True, help_text="tasa")
    montoventa = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(
        0.0), null=False, help_text="monto minimo para ventas FIAT")
    montocompra = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(
        0.0), null=False, help_text="monto minimo para compras FIAT")

    def __str__(self):
        return '%s - %s - %s' % (self.id, self.nombre, self.imagen)


class tPaisDocumento(models.Model):
    TIPO = (('I', 'Imagen'), ('A', 'Archivo'), ('T', 'Texto'))
    OPCIONAL = (('S', 'Si'), ('N', 'No'))
    JURIDICO = (('N', 'Natural'), ('J', 'Juridico'))
    nombre = models.TextField(
        max_length=120, null=False, blank=False, help_text="Nombre Documento x Pais")
    pais = models.ForeignKey(tPais, null=False, blank=False,
                             on_delete=models.CASCADE, help_text="Pais asociado")
    tipo = models.CharField(max_length=1, null=True, choices=TIPO,
                            default='I', help_text="Tipo de documento")
    opcional = models.CharField(
        max_length=1, null=True, choices=OPCIONAL, default='I', help_text="Tipo de documento")
    juridico = models.CharField(
        max_length=1, null=True, choices=JURIDICO, default='I', help_text="Tipo de documento")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")
    detalle = models.TextField(
        max_length=240, null=True, blank=True, help_text="Caracteristicas del documento")
    opcional = models.CharField(
        max_length=1, null=True, choices=OPCIONAL, default='N', help_text="Opcional Si o No")
    juridico = models.CharField(
        max_length=1, null=True, choices=JURIDICO, default='N', help_text="Natural o Juridico")

    def __str__(self):
        return '%s - %s - %s' % (self.nombre, self.pais.id, self.pais.nombre)


class tPaisServicioDefix(models.Model):
    nombre = models.TextField(
        max_length=120, null=False, blank=False, help_text="Servicio Defix x Pais")
    datos = models.TextField(max_length=200, null=True, blank=True,
                             help_text="Detalle de infirmacion de FIAT x Pais")
    pais = models.ForeignKey(tPais, null=False, blank=False,
                             on_delete=models.CASCADE, help_text="Pais asociado")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")

    def __str__(self):
        return '%s - %s - %s' % (self.nombre, self.pais.id, self.pais.nombre)


class tkycCabecera(models.Model):
    ESTATUS = (('R', 'Revision'), ('A', 'Aprobada'), ('C', 'Cancelada'))
    estatus = models.CharField(max_length=1, default='R', choices=ESTATUS)
    observacion = models.TextField(
        max_length=240, null=True, blank=True, help_text="usuario con registros de kyc")
    pais = models.ForeignKey(tPais, null=True, blank=True,
                             on_delete=models.CASCADE, help_text="Pais asociado")
    fecha_inicio = models.DateTimeField(
        null=True, blank=True, help_text="Fecha de inicio de la transaccion")
    fecha_final = models.DateTimeField(
        null=True, blank=True, help_text="Fecha de fin de la transaccion")
    juridico = models.CharField(
        max_length=1, null=True, help_text="Natural o Juridico")
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="usuario asociado")
    banco_cuenta = models.TextField(max_length=240, null=True, blank=True,
                                    help_text="detalle de informacion bancaria asociada al KYC")
    fecha_registro = models.DateTimeField(
        default=datetime.now, blank=True, help_text="fecha de registro")
    email = models.TextField(max_length=240, null=True,
                             blank=True, help_text="email del usuario")

    def __str__(self):
        return '%s - %s - %s - %s' % (self.id, self.estatus, self.pais.id, self.usuario.username)


class tkycDetalle(models.Model):
    ESTATUS = (('R', 'Revision'), ('A', 'Aprobada'), ('C', 'Cancelada'))
    estatus = models.CharField(max_length=1, default='R', choices=ESTATUS)
    kyccabecera = models.ForeignKey(
        tkycCabecera, null=True, blank=True, on_delete=models.DO_NOTHING, help_text="Id de KYC asociado")
    texto = models.TextField(max_length=150, blank=True,
                             null=True, help_text="texto...")
    documento = models.TextField(
        max_length=150, blank=True, null=True, help_text="documnto")
    imagen = models.ImageField(
        upload_to='media/archivoskyc', null=True, help_text="Imagen KYC")
    paisdocumento = models.ForeignKey(
        tPaisDocumento, null=True, blank=True, on_delete=models.DO_NOTHING, help_text="Documento KFC pos Pais")
    observacion = models.TextField(
        max_length=240, null=True, blank=True, help_text="usuario con registros de kyc")
    tipo = models.CharField(max_length=1, null=True,
                            help_text="Tipo de documento")

    def __str__(self):
        return '%s - %s' % (self.kyccabecera.id, self.estatus)


class tTipoPago(models.Model):
    nombre = models.TextField(
        max_length=120, null=True, blank=True, help_text="Nombre del Banco")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")

    def __str__(self):
        return '%s - %s' % (self.id, self.nombre)


class tPaisBanco(models.Model):
    pais = models.ForeignKey(tPais, null=False, blank=False,
                             on_delete=models.CASCADE, help_text="Pais asociado")
    nombre = models.TextField(
        max_length=120, null=True, blank=True, help_text="Nombre del Banco")
    codigo = models.TextField(max_length=20, null=True,
                              blank=True, help_text="Codigo del Banco 4 digitos")
    imagen = models.ImageField(
        upload_to='media/bancos', null=True, blank=True, help_text="Logo asociado al banco")
    tasa = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(
        0.0), null=False, help_text="tasa compra")
    monto = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(
        0.0), null=False, help_text="Monto limite para validar para compras")
    montomin = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(
        0.0), null=False, help_text="Monto minimo validar para compras")
    tasaaltomonto = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(
        0.0), null=False, help_text="tasa a aplicar con altos montos de compras")
    tasav = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(
        0.0), null=False, help_text="tasa venta")
    montov = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(
        0.0), null=False, help_text="Monto limite para validar para venta")
    montominv = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(
        0.0), null=False, help_text="Monto minimo validar para venta")
    tasaaltomontov = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(
        0.0), null=False, help_text="tasa a aplicar con altos montos de venta")
    comision = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(
        0.0), null=False, help_text="comision compra")
    comisionv = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(
        0.0), null=False, help_text="comision compra")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")

    def __str__(self):
        return '%s - %s - %s' % (self.nombre, self.pais.id, self.pais.nombre)


class tkycCuenta(models.Model):
    kyccabecera = models.ForeignKey(
        tkycCabecera, null=True, blank=True, on_delete=models.DO_NOTHING, help_text="Id de KYC asociado")
    banco = models.ForeignKey(tPaisBanco, null=True, blank=True,
                              on_delete=models.DO_NOTHING, help_text="Id de Banco Pais")
    tipopago = models.ForeignKey(tTipoPago, null=True, blank=True,
                                 on_delete=models.DO_NOTHING, help_text="Id de tipo de pago")
    titular = models.TextField(
        max_length=150, blank=True, null=True, help_text="Nombre del Titular")
    cedula = models.TextField(
        max_length=20, blank=True, null=True, help_text="Numero de Identificacion")
    telefono = models.TextField(
        max_length=50, blank=True, null=True, help_text="Numero de telefono")
    numerocuenta = models.TextField(
        max_length=20, null=True, blank=True, help_text="numero de cuenta del titular")
    tipocuenta = models.TextField(
        max_length=20, null=True, blank=True, help_text="tipo  de cuenta del titular")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")

    def __str__(self):
        return '%s - %s - %s' % (self.kyccabecera.id, self.habilitado, self.titular)


class tkycCuentaDefix(models.Model):
    pais = models.ForeignKey(tPais, null=False, blank=False,
                             on_delete=models.CASCADE, help_text="Pais asociado")
    banco = models.ForeignKey(tPaisBanco, null=True, blank=True,
                              on_delete=models.DO_NOTHING, help_text="Id de Banco Pais")
    tipopago = models.ForeignKey(tTipoPago, null=True, blank=True,
                                 on_delete=models.DO_NOTHING, help_text="Id de tipo de pago")
    titular = models.TextField(
        max_length=150, blank=True, null=True, help_text="Nombre del Titular")
    cedula = models.TextField(
        max_length=20, blank=True, null=True, help_text="Numero de Identificacion")
    telefono = models.TextField(
        max_length=50, blank=True, null=True, help_text="Numero de telefono del titular")
    numerocuenta = models.TextField(
        max_length=20, null=True, blank=True, help_text="numero de cuenta del titular")
    tipocuenta = models.TextField(
        max_length=20, null=True, blank=True, help_text="tipo  de cuenta del titular")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")

    def __str__(self):
        return '%s - %s - %s - %s' % (self.pais.id, self.pais.nombre, self.habilitado, self.titular)


# class UsuarioMetodos(models.Model):
# pais=models.ForeignKey(Pais,null=False,blank=False,on_delete=models.CASCADE,help_text="Pais asociado")
# nombre=models.TextField(max_length=150,blank=False,null=True,help_text="Nombre...")
# datos=models.TextField(max_length=150,blank=False,null=True,help_text="Datos...")
# def __str__(self):
# return  '%s - %s - %s'%(self.pais.nombre,self.nombre,self.datos)

# class UsuarioDefix(models.Model):
# nombre=models.TextField(max_length=120,unique=True, null=False, blank=False, primary_key=True,help_text="Nombre Pais")
# fecha_creacion=models.DateTimeField(null=True,blank=True,help_text="Fecha creacion del usuario")
# ESTATUS=(('I','Inactivo'),('A','Aprobada'))
# estatus=models.CharField(max_length=1,default='A',choices=ESTATUS)
# def __str__(self):
# return '%s - %s'%(self.nombre,self.estatus)

class FiatTransaccion(models.Model):
    ESTATUS = (('1', 'Creado'), ('2', 'Asignado'),
               ('3', 'Procesado'), ('4', 'Completado'), ('5', 'Anulado'))
    estatus = models.CharField(max_length=1, default='1', choices=ESTATUS)
    ACCION = (('C', 'Compra'), ('V', 'Venta'))
    accion = models.CharField(max_length=1, default='C', choices=ACCION)
    referencia = models.TextField(
        max_length=20, null=True, blank=True, help_text="numero de referencia")
    pais = models.ForeignKey(tPais, null=True, blank=True,
                             on_delete=models.CASCADE, help_text="Pais asociado")
    cripto = models.TextField(max_length=20, null=True,
                              blank=True, help_text="nombre de la criptomoneda")
    cantidad = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(
        0.0), null=False, help_text="cantidad de la criptomoneda")
    tasa = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(
        0.0), null=False, help_text="Tasa de cambio")
    comision = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(
        0.0), null=False, help_text="comision")
    monto = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(
        0.0), null=False, help_text="monto")
    banco = models.ForeignKey(tPaisBanco, null=True, blank=True,
                              on_delete=models.DO_NOTHING, help_text="Id de Banco Pais")
    banco_nombre = models.TextField(
        max_length=150, blank=True, null=True, help_text="Nombre del Titular")
    tipopago = models.ForeignKey(tTipoPago, null=True, blank=True,
                                 on_delete=models.DO_NOTHING, help_text="Id de tipo de pago")
    tipopago_nombre = models.TextField(
        max_length=150, blank=True, null=True, help_text="Nombre del Titular")
    titular = models.TextField(
        max_length=150, blank=True, null=True, help_text="Nombre del Titular")
    cedula = models.TextField(
        max_length=20, blank=True, null=True, help_text="Numero de Identificacion")
    telefono = models.TextField(
        max_length=50, blank=True, null=True, help_text="Numero de telefono del titular")
    numerocuenta = models.TextField(
        max_length=20, null=True, blank=True, help_text="numero de cuenta del titular")
    tipocuenta = models.TextField(
        max_length=20, null=True, blank=True, help_text="tipo  de cuenta del titular")
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="usuario asociado")
    fecha_creado = models.DateTimeField(
        default=datetime.now, blank=True, help_text="fecha de registro")
    fecha_asignado = models.DateTimeField(
        null=True, blank=True, help_text="fecha de registro")
    usuario_asignado = models.TextField(
        max_length=240, null=True, blank=True, help_text="usuario asignador")
    fecha_procesado = models.DateTimeField(
        null=True, blank=True, help_text="fecha de registro procesado")
    fecha_completado = models.DateTimeField(
        null=True, blank=True, help_text="fecha de registro completado")
    fecha_anulado = models.DateTimeField(
        null=True, blank=True, help_text="fecha de registro aunulado")
    observacion = models.TextField(
        max_length=240, null=True, blank=True, help_text="usuario")
    adjuntofiat = models.ImageField(
        upload_to='media/fiat', null=True, blank=True, help_text="adjunto soporte de la venta o compra")
    email = models.TextField(max_length=240, null=True,
                             blank=True, help_text="email del usuario")
    wallet = models.TextField(
        max_length=240, null=True, blank=True, help_text="wallet")

    def __str__(self):
        return '%s - %s - %s - %s' % (self.estatus, self.accion, self.observacion, self.titular)


class tdataCrypto(models.Model):
    key = models.TextField(max_length=150, blank=True,
                           null=True, help_text="Nombre del token")  # "usdt",
    # juanochando.defix3
    wallet_defix = models.TextField(max_length=150, blank=True,
                             null=True, help_text="ruta del token")
    title = models.TextField(max_length=150, blank=True, null=True,
                             help_text="titulo del token")  # "USDT (ERC20)",
    desc = models.TextField(max_length=150, blank=True, null=True,
                            help_text="descripcion del token")  # "Tether",
    network = models.TextField(max_length=150, blank=True, null=True,
                               help_text="descripcion de la red")  # "Tether",
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")

    def __str__(self):
        return '%s - %s - %s' % (self.key, self.wallet_defix, self.title)
