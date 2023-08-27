from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = '__all__'  

class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = '__all__'  

class ModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modulo
        fields = '__all__'  

class ComisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comision
        fields = '__all__'  

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class BancoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banco
        fields = '__all__'

class tPaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = tPais
        fields = '__all__'
      

class tPaisDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = tPaisDocumento
        fields = '__all__'

class tPaisServicioDefixSerializer(serializers.ModelSerializer):
    class Meta:
        model = tPaisServicioDefix
        fields = '__all__'

class tkycCabeceraSerializer(serializers.ModelSerializer):
    class Meta:
       model = tkycCabecera
       fields = '__all__'

class tkycDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = tkycDetalle
        fields = '__all__'

class tPaisBancoSerializer(serializers.ModelSerializer):
    class Meta:
        model = tPaisBanco
        fields = '__all__'

class tTipoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = tTipoPago
        fields = '__all__'        

class tkycCuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = tkycCuenta
        fields = '__all__'

class tkycCuentaDefixSerializer(serializers.ModelSerializer):
    class Meta:
        model = tkycCuentaDefix
        fields = '__all__'

class FiatTransaccionSerializer(serializers.ModelSerializer):
    adjuntofiat = serializers.ImageField(required=False)
    class Meta:
        model = FiatTransaccion
        fields = '__all__'

class CreacionPerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ['usuario']

    usuario = serializers.SerializerMethodField('loadusuario')
    def loadusuario(self, obj):
      return obj.usuario.username
      
class CryptocurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Cryptocurrency
        fields = '__all__'

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'

class tUserFiatSerializer(serializers.ModelSerializer):
    class Meta:
        model = tUserFiat
        fields = '__all__'          

class tdataCryptoSerializer(serializers.ModelSerializer):
    class Meta:
        model = tdataCrypto
        fields = '__all__'   

#class ImagePostSerializer(serializers.ModelSerializer):
#    image = serializers.ImageField(required=False)
#    class Meta:
#        model = models.ImagePost


##class kycHistoricoSerializer(serializers.ModelSerializer):
 ##   class Meta:
 ##      model = kycHistorico
 ##       fields = '__all__'

##class UsuarioMetodosSerializer(serializers.ModelSerializer):
  ##  class Meta:
   ##     model = UsuarioMetodos
   ##     fields = '__all__'

##class UsuarioDefixSerializer(serializers.ModelSerializer):
 ##   class Meta:
  ##      model = UsuarioDefix
   ##     fields = '__all__'

##class UsuarioTransaccionSerializer(serializers.ModelSerializer):
  ##  class Meta:
  ##      model = UsuarioTransaccion
  ##      fields = '__all__'