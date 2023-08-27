from django.urls import path, include
from rest_framework import routers
from .views import *



router = routers.DefaultRouter()
router.register(r'perfiles',PerfilesVS,basename='perfil')
router.register(r'bancos',BancoVS,basename='banco')
router.register(r'usuarios',UserVS,basename='user')
router.register(r'modulos',ModuloVS,basename='modulo')
router.register(r'comisiones',ComisionVS,basename='comision')
router.register(r'permisos',PermisoVS,basename='permiso')
router.register(r'login',LoginNoir,basename='login')
router.register(r'paises',tPaisVS,basename='tpais')
router.register(r'paisesdoc',tPaisDocumentoVS,basename='tPaisDocumento')
router.register(r'paisesdefix',tPaisServicioDefixVS,basename='tPaisServicioDefix')
router.register(r'kyccabecera',tkycCabeceraVS,basename='tkycCabecera')
router.register(r'kycdetalle',tkycDetalleVS,basename='tkycDetalle')
router.register(r'paisbanco',tPaisBancoVS,basename='tPaisBanco')
router.register(r'tipopago',tTipoPagoVS,basename='tTipoPago')
router.register(r'kyccuenta',tkycCuentaVS,basename='tkycCuenta')
router.register(r'kyccuentadefix',tkycCuentaDefixVS,basename='tkycCuentaDefix')
router.register(r'FiatTransaccion',FiatTransaccionVS,basename='FiatTransaccion')
router.register(r'cryptocurrency',CryptocurrencyVS,basename='Cryptocurrency')
router.register(r'token',TokenVS,basename='token')
router.register(r'userfiat',tUserFiatVS,basename='tUserFiat')
router.register(r'datacrypto',tdataCryptoVS,basename='tdataCrypto')

urlpatterns = [
    path('', include(router.urls)), 
    path('crear-usuario/', crear_nuevo_usuario),
    path('get-users-defix', get_users_defix),
    path('get-users-admin', get_users_admin),
    path('get-transaction-history', get_transaction_history),
    path('get-balance-defix', get_balance_defix),
    path('act-user-admin', actualizar_usuario_admin),
    path('get-comision/<str:coin>', get_comision),
    #path('get-paises/<str:observacion>', get_paises),
    path('get-paises', get_paises),
    path('get-paisesdoc/<str:pais_id>', get_paisesdoc),
    path('get-kyccabecera', get_kyccabecera),
    path('get-fiat', get_fiat),
    path('get-fiat-user', get_fiat_user),
    path('get-fiat-estatus/<str:observacion>', get_fiat_estatus),
    path('crear-kyc', crear_kyc),
    path('get-tcuenta/<str:observacion>', get_tcuenta),
    path('get-tcuenta-defix/<str:observacion>', get_tcuenta_defix),
    path('put-fecha-fiat', put_fecha_fiat),
    path('cancel-buy', cancel_buy),
    path('confirm-sell', confirm_sell),
    #path('create-user/',CreateUser.as_view()),
    path('create-user/',CreateUser),
    path('ValidacionTokenEmail/',ValidacionTokenEmail),
    path('GeneraTokenEmail/',GeneraTokenEmail),
    path('auth/', CustomAuthToken.as_view()),
    path('get-paisbancotasa/<str:pais_id>', get_paisbancotasa),
    path('ValidacionUsuario/<str:user>', ValidacionUsuario),
    path('SendEmailFiat', SendEmailFiat),
    path('SendEmailFiatUser', SendEmailFiatUser),
    path('SendEmailFiatUserCode', SendEmailFiatUserCode),
    path('SendEmailFiatUserToken', SendEmailFiatUserToken),
    path('SendEmailEstatusFIAT', SendEmailEstatusFIAT),
    path('SendEmailEstatusKYC', SendEmailEstatusKYC),
    path('SendEmailKYC', SendEmailKYC),
    path('SendEmailKYCUser', SendEmailKYCUser),
    path('crear-fiat', crear_fiat),
    path('get-kycdetalle/<str:kyccabecera_id>', get_kycdetalle),
    path('generar_historico_fiat/<str:fecha_inicio>/<str:fecha_fin>', generar_historico_fiat),
]
