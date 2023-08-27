from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Perfil)
admin.site.register(Modulo)
admin.site.register(Permiso)
admin.site.register(Comision)
admin.site.register(Banco)
# admin.site.unregister(Permiso)
admin.site.register(tPais)
admin.site.register(tPaisDocumento)

admin.site.register(tPaisServicioDefix)
admin.site.register(tkycCabecera)
admin.site.register(tkycDetalle)
admin.site.register(tPaisBanco)
admin.site.register(tTipoPago)
admin.site.register(tkycCuenta)
admin.site.register(tkycCuentaDefix)
admin.site.register(FiatTransaccion)
admin.site.register(Cryptocurrency)
admin.site.register(Token)
admin.site.register(tUserFiat)
admin.site.register(tdataCrypto)


# admin.site.register(kycHistorico)
# admin.site.register(UsuarioMetodos)
# admin.site.register(UsuarioDefix)
# admin.site.register(UsuarioTransaccion)
