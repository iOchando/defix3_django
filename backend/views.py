# Imports
from copyreg import constructor
from .serializers import *
from .models import *
from rest_framework import viewsets, status, generics
from django_filters import rest_framework as filters
from rest_framework.permissions import IsAdminUser,IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication,BasicAuthentication,TokenAuthentication
from django.shortcuts import render,get_object_or_404
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import login
from django.http import JsonResponse,HttpResponse
import requests
import pandas as pd
import psycopg2 as pg
from sqlalchemy import create_engine
import json
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authtoken.views import ObtainAuthToken
from django.conf import settings
from django.core.mail import send_mail,EmailMultiAlternatives,EmailMessage
from django.template import  loader, Context
from django.template.loader import get_template,render_to_string
from django.contrib.auth import authenticate
from django.utils import timezone
from openpyxl import Workbook
from xlwt import Workbook, easyxf
from datetime import datetime,timedelta
import pytz

import random

class Generico(viewsets.ModelViewSet):
    # CREAR
    def create(self,request,*args,**kwargs):
        perfil = Perfil.objects.get(usuario=request.user)
        if verificar_permiso(perfil,self.permiso,'escribir'):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data,headers=headers,status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    # ACTUALIZAR
    def update(self,request,*args,**kwargs):
        perfil = Perfil.objects.get(usuario=request.user)
        if verificar_permiso(perfil,self.permiso,'actualizar'):
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    # BORRAR
    def destroy(self,request,*args,**kwargs):
        perfil = Perfil.objects.get(usuario=request.user)
        if verificar_permiso(perfil,self.permiso,'borrar'):
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    # LEER (MANY)
    def list(self,request,*args,**kwargs):
        perfil = Perfil.objects.get(usuario=request.user)
        if verificar_permiso(perfil,self.permiso,'leer'):
            serializer = self.get_serializer(self.queryset, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    # LEER (SINGLE)
    def retrieve(self,request,pk=None):
        perfil = Perfil.objects.get(usuario=request.user)
        if verificar_permiso(perfil,self.permiso,'leer'):
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

class PerfilesVS(Generico):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    permiso='UsersAdmin'
    queryset=Perfil.objects.all()
    serializer_class=PerfilSerializer

    # LEER (SINGLE)
    def retrieve(self,request,pk=None):
        perfil = Perfil.objects.get(usuario=request.user)
        objeto = get_object_or_404(self.queryset, pk=pk)
        if verificar_permiso(perfil,self.permiso,'leer') or perfil.tipo == 'S' or objeto.usuario == request.user:
            return Response(self.serializer_class(objeto).data)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def list(self,request,*args,**kwargs):
        perfil = Perfil.objects.get(usuario=request.user)
        if verificar_permiso(perfil,self.permiso,'leer'):
            serializer = self.get_serializer(self.queryset, many=True).data
            for user in serializer:
                date = User.objects.get(id=user['usuario'])
                user['usuario'] = date.username
                perfil = Perfil.objects.get(usuario=date)
                permisos = Permiso.objects.filter(perfil=perfil)
                user['permisos'] = PermisoSerializer(instance=permisos, many=True).data
                #print(user)
            return Response(serializer,status=status.HTTP_200_OK)


class tUserFiatVS(Generico):
    #permission_classes=[IsAuthenticated]
    #authentication_classes=[TokenAuthentication]
    permiso='UsersAdmin'
    queryset=tUserFiat.objects.all()
    serializer_class=tUserFiatSerializer


class PermisoVS(Generico):
    permiso='UsersAdmin'
    queryset=Permiso.objects.all()
    serializer_class=PermisoSerializer

class ModuloVS(Generico):
    permiso='UsersAdmin'
    queryset=Modulo.objects.all()
    serializer_class=ModuloSerializer

class UserVS(Generico):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    permiso='UsersAdmin'
    queryset=User.objects.all()
    serializer_class=UserSerializer

class BancoVS(Generico):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    permiso='UsersAdmin'
    queryset=Banco.objects.all()
    serializer_class=BancoSerializer

class ComisionVS(Generico):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    permiso='Comisiones'
    queryset=Comision.objects.all()
    serializer_class=ComisionSerializer

    def list(self,request,*args,**kwargs):
        perfil = Perfil.objects.get(usuario=request.user)
        if verificar_permiso(perfil,self.permiso,'leer'):
            comisiones = Comision.objects.all()
            data = []
            for comision in comisiones:
                item = {
                    "coin": comision.coin,
                    "nombre": comision.nombre,
                    "blockchain": comision.blockchain,
                    "transfer": comision.transfer,
                    "swap": comision.swap,
                    "fiat": comision.fiat,
                }
                data.append(item)
            #serializer = ComisionSerializer(comisiones).data
            return Response(data,status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
class CryptocurrencyVS(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    queryset=Cryptocurrency.objects.all()
    serializer_class=CryptocurrencySerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)   
    
class TokenVS(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    queryset=Token.objects.all()
    serializer_class=TokenSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)   

class tPaisVS(Generico):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    permiso='Paises'
    queryset=tPais.objects.all()
    serializer_class=tPaisSerializer

    def list(self,request,*args,**kwargs):
        perfil=Perfil.objects.get(usuario=request.user)
        data = []
        if verificar_permiso(perfil,'Paises','leer'):
            if perfil:
                Paises=tPais.objects.all()
                for dato in Paises:
                    item = {
                        'id':dato.id,
                        'nombre':dato.nombre,
                        'coin':dato.coin,
                        'imagen':settings.RUTA_MEDIA+settings.MEDIA_URL+dato.imagen.name,
                        'habilitado': dato.habilitado,
                        'kycventa': dato.kycventa,
                        'kyccompra': dato.kyccompra,
                        'tasa': dato.tasa,
                        'montoventa': dato.montoventa,
                        'montocompra': dato.montocompra,
                    }
                    data.append(item)
                return Response(data,status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class tPaisDocumentoVS(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    queryset=tPaisDocumento.objects.all()
    serializer_class=tPaisDocumentoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
      'pais':['exact'],
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)   

class tPaisServicioDefixVS(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    queryset=tPaisServicioDefix.objects.all()
    serializer_class=tPaisServicioDefixSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
      'pais':['exact'],
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)   

class tPaisBancoVS(viewsets.ModelViewSet):
#    permission_classes=[IsAuthenticated]
#    authentication_classes=[TokenAuthentication]
    queryset=tPaisBanco.objects.all()
    serializer_class=tPaisBancoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
      'pais':['exact'],
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)  

class tTipoPagoVS(viewsets.ModelViewSet):
#    permission_classes=[IsAuthenticated]
#    authentication_classes=[TokenAuthentication]
    queryset=tTipoPago.objects.all()
    serializer_class=tTipoPagoSerializer
    #filter_backends = [DjangoFilterBackend]
    #filterset_fields = {'pais':['exact'],}

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)  

class tdataCryptoVS(viewsets.ModelViewSet):
    queryset=tdataCrypto.objects.all()
    serializer_class=tdataCryptoSerializer
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs) 


class tkycCabeceraVS(viewsets.ModelViewSet):
    #permission_classes=[IsAuthenticated]
    #authentication_classes=[TokenAuthentication]
    queryset=tkycCabecera.objects.all()
    serializer_class=tkycCabeceraSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
      'usuario':['exact'],
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs) 

class tkycDetalleVS(viewsets.ModelViewSet):
    #permission_classes=[IsAuthenticated]
    #authentication_classes=[TokenAuthentication]
    queryset=tkycDetalle.objects.all()
    serializer_class=tkycDetalleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
      'kyccabecera':['exact'],
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs) 

class tkycCuentaVS(viewsets.ModelViewSet):
    #permission_classes=[IsAuthenticated]
    #authentication_classes=[TokenAuthentication]
    queryset=tkycCuenta.objects.all()
    serializer_class=tkycCuentaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
      'kyccabecera':['exact'],
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)      

class tkycCuentaDefixVS(viewsets.ModelViewSet):
    #permission_classes=[IsAuthenticated]
    #authentication_classes=[TokenAuthentication]
    queryset=tkycCuentaDefix.objects.all()
    serializer_class=tkycCuentaDefixSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
      'pais':['exact'],
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)   


class FiatTransaccionVS(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    queryset=FiatTransaccion.objects.all()
    serializer_class=FiatTransaccionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
      'observacion':['exact'],
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)  



# Verificar que el usuario tenga permisos
def verificar_permiso(perfil,modulo,accion):
    try:
        permiso=Permiso.objects.filter(modulo__nombre__exact=modulo,perfil=perfil).first()
    except:
        return False
    if permiso:
        if accion=='leer':
            return permiso.leer
        elif accion=='escribir':
            return permiso.escribir
        elif accion=='actualizar':
            return permiso.actualizar
        elif accion=='borrar':
            return permiso.borrar
    return False

# Funcion para la primera carga del sistema
def crear_super_usuario(request):
    from . import modulos
    if Modulo.objects.all().count()==0:
        for modelo in modulos.modelos:
            modulo=Modulo(nombre=modelo['nombre'])
            modulo.save()
            # if modelo['mayor']!=None:
            #     menu.parent=Modulo.objects.get(router=modelo['parent'])
            #     menu.save()
        # Super
        superuser=User.objects.create_user(username='super',password='super',is_staff=True, is_superuser=True)
        perfilS=Perfil(usuario=superuser,activo=True,tipo="S")
        perfilS.save()
        # Admin
        admin=User.objects.create_user(username='admin',password='admin')
        perfilA=Perfil(usuario=admin,activo=True,tipo="A")
        perfilA.save()
        # User
        usuario=User.objects.create_user(username='usuario',password='usuario')
        perfilU=Perfil(usuario=usuario,activo=True,tipo="U")
        perfilU.save()
        for m in Modulo.objects.all():
            Permiso.objects.get_or_create(perfil=perfilS,modulo=m,defaults={'leer': True,'escribir': True,'borrar': True,'actualizar': True})
            # if m.mayor!=None:
            #     permiso.parent=permiso.objects.get(permiso__id=m.mayor.id)
            #     permiso.save()
        return "Super creado"
    else:
        return "Ya existe un superusuario"


# Funcion tipo vista para crear un nuevo usuario
@api_view(["POST"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def crear_nuevo_usuario(request):
    datos=request.data
    user=None
    perfil_nuevo=None
    try:
        perfil_creador=Perfil.objects.get(usuario=request.user)
        # En caso de encontrar un usuario con el mismo email
        user=User.objects.filter(email=datos['email'])
        if user:
            return Response("Ya hay un usuario con el mismo correo",status=status.HTTP_400_BAD_REQUEST)
        # En caso de crear un nuevo Admin
        elif perfil_creador.tipo=='S' and datos['tipo']=='A':
            return crear_admin(datos,perfil_creador)
        # En caso de que se quiera crear un usuario normal
        elif perfil_creador.tipo=='A' or perfil_creador.tipo=='S' or verificar_permiso(perfil_creador,'UsersAdmin','escribir'):
            # Crear usuario con 'create_user'
            user=User.objects.create_user(username=datos['username'],email=datos['email'],password=datos['password'])
            # Crear perfil del usuario
            perfil_nuevo=Perfil.objects.create(usuario=user,tipo=datos['tipo'])
            # Crear permisos
            permisos=guardar_permisos(datos['permisos'],perfil_nuevo.id,perfil_creador)
            # En caso de un error al crear los permisos saltar error
            if permisos:
                raise Exception('%s'%(permisos['error']))
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        # Borrar datos en caso de error
        try:
            user.delete()
        except:
            pass
        try:
            perfil_nuevo.delete()
        except:
            pass
        return Response('%s'%(e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Funcion para crear los admins por la nueva instancia
def crear_admin(data,super_p):
    try:
        user=User.objects.create_user(username=data['username'],email=data['email'],password=data['password'])
        perfil=Perfil.objects.create(usuario=user,tipo='A')
        permisos=guardar_permisos(data['permisos'],perfil.id,super_p,perfil)
        if permisos:
            raise Exception('%s'%(permisos['error']))
        return Response(status=status.HTTP_201_CREATED)
    except Exception as e:
        try:
            user.delete()
        except:
            pass
        try:
            perfil.delete()
        except:
            pass
        return Response('%s'%(e),status=status.HTTP_417_EXPECTATION_FAILED)

# Funcion para obtener la data de los permisos
def guardar_permisos(data,perfil_n=None,perfil_c=None,perfil=None):
    try:
        if perfil_c and perfil_n:
            # Obtener datos para la creacion de permisos
            perfil_n=Perfil.objects.get(id=perfil_n)
            modulos=Modulo.objects.all()
            permisos=Permiso.objects.filter(perfil=perfil_c)
            for per in data:
                # Si se debe crear un menu, crearlo
                # padre=crear_menu(instancia,per['parent']) if perfil else None
                # Obtener menu
                modulo=modulos.get(nombre__exact=per['nombre'])
                # Verificar permiso del creador
                permiso_c=permisos.filter(modulo=modulo).first()
                if permiso_c:
                    perfil = perfil_n if not perfil else perfil
                    # if per['parent']:
                    #     # Obtener menu padre
                    #     modulop=modulos.get(instancia=instancia,menu__router__exact=per['parent']) if not perfil else padre
                    #     crear_permiso(instancia,per,modulop,perfil_n,permiso_c)
                    try: 
                        permiso=Permiso.objects.get(modulo=modulo,perfil=perfil)
                    except: 
                        permiso=Permiso(modulo=modulo,perfil=perfil)
                    # Asignar acciones
                    permiso.leer=per['leer'] if permiso_c.leer else False
                    permiso.escribir=per['escribir'] if permiso_c.escribir else False
                    permiso.borrar=per['borrar'] if permiso_c.borrar else False
                    permiso.actualizar=per['actualizar'] if permiso_c.actualizar else False
                    permiso.save()
        return None
    except Exception as e:
        # Borrar datos creados
        try:
            Permiso.objects.filter(perfil=perfil).delete()
        except:
            pass
        return {'error':e}

class LoginNoir(viewsets.ModelViewSet):
    permission_classes=[AllowAny]
    authentication_classes=[TokenAuthentication]
    serializer_class=AuthTokenSerializer
    queryset=User.objects.none()
    # {"username":"super","password":"super"}
    def create(self,request,format=None):
        data = request.data
        try:
            #print(data['username'])
            if '@' in data['username'] and '.' in data['username']:
                #print('email')
                user = User.objects.get(email__exact=request.data['username'])
            else:
                #print('username')
                user = User.objects.get(username__exact=request.data['username'])
            request.data['username'] = user.username
        except:
            return Response({'error':'Not encounter user'},status=status.HTTP_404_NOT_FOUND)
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']
        login(request,user)
        # respuesta={'username':user.username}
        
        token, creado = Token.objects.get_or_create(user__id=user.id, defaults={'user':user})

        perfil = Perfil.objects.get(usuario=user)
        permisos = Permiso.objects.filter(perfil=perfil)

        dataPermisos = PermisoSerializer(instance=permisos, many=True).data
        if perfil.tipo == 'D': # Evitar que el usuario de dApp entre en el Admin
           return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED) 

        user_d=UserSerializer(user).data
        data={
            'username':user_d['username'],
            'first_name':user_d['first_name'],
            'last_name':user_d['last_name'],
            'email':user_d['email'],
            'is_staff':user_d['is_staff'],
            'date_joined':user_d['date_joined'],
            'last_login':user_d['last_login'],
        }
        return Response({'data':data,'token':token.key, 'permisos': dataPermisos},status=status.HTTP_200_OK)
    def list(self):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def retrieve(self):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def update(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

#--------------------------------------------------------------------------login FIAT
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        user = authenticate(username=request.data['username'], email=request.data['email'], password=request.data['password'])
        if user is not None:
            request.data['username']=user.username
            serializer = self.serializer_class(data=request.data,
                                            context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            #perfil, pcreated = Perfil.objects.get_or_create(usuario=user,defaults={'ip_registro':request.data['ip']})
            perfil, pcreated = Perfil.objects.get_or_create(usuario=user,defaults={'tipo':'D'})
            
            #perfil.ultimo_ip = request.data['ip']
            perfil.save()
            return Response({
                'token': token.key,
                'status': perfil.activo,
                'mensaje': 'Las credenciales son correctas'
            }, status=status.HTTP_200_OK) 
        else:
            return Response({
            'mensaje': 'Las credenciales son incorrectas'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@csrf_exempt
@permission_classes([AllowAny])
def CreateUser(request):
    TokenEmail = random.randint(10000, 99999)
    user = User.objects.create_user(username=request.data['username'], email=request.data['email'], password=request.data['password'])
    user.save()
    token, created = Token.objects.get_or_create(user=user)
    perfil, created = Perfil.objects.get_or_create(usuario=user,defaults={'tipo':'D'})
    perfil.save()
    userfiat, created = tUserFiat.objects.get_or_create(usuario=user,referido='',tokenemail=TokenEmail)
    userfiat.save()
    SendEmailFiatUserToken(request.data['username'],request.data['idioma'])
    return Response({'token': token.key}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@csrf_exempt
@permission_classes([AllowAny])
def ValidacionTokenEmail(request):
    """
    Valida si el token existe y/o es válido en el modelo tUserFiat.
    Recibe 2 Parámetros: usuario = Nombre del usuario, tokenemail = Token de 6 dígitos numéricos.
    Retorna: mensaje= Información de la validación,  valido= buleano (True= Token Válido, False= Token inválido).
    """
    try:
        mensaje="Token Válidoxx"
        valido="True"
        user = User.objects.get(username=request.data['usuario'])
        vigente = tUserFiat.objects.get(usuario=user,tokenemail=request.data['tokenemail'])
        tiempoactual=datetime.now().replace(tzinfo=pytz.utc)
        tiempocreacion=(vigente.creacion + timedelta(seconds=90)).replace(tzinfo=pytz.utc)
        if vigente.activo:
            if tiempoactual > tiempocreacion:
                mensaje="Token Vencido"
                valido=False
            vigente.activo=False

            vigente.save()
        else:
            mensaje="Token Vencido"
            valido=False
        return Response({"mensaje": mensaje,"valido":valido},status=status.HTTP_200_OK) 
    except tUserFiat.DoesNotExist:
        return Response({"mensaje": "Token no Válidoxx.","valido":"False"},status=status.HTTP_200_OK)
    except:
        return Response({"mensaje": "Error Usuario no existexx","valido":"False"},status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@csrf_exempt
@permission_classes([AllowAny])
def GeneraTokenEmail(request):
    """
    Genera un nuevo token numérico de 6 dígitos en el modelo tUserFiat.
    Recibe 1 Parámetros: usuario = Nombre del usuario
    Retorna: mensaje= Información de la validación,   valido= buleano (True= Token Válido, False= Token inválido).
    """    
    try:
        mensaje="Token Creadoxx"
        valido="True"
        TokenEmail = random.randint(10000, 99999)
        user = User.objects.get(username=request.data['usuario'])
        vigente = tUserFiat.objects.get(usuario=user)
        vigente.tokenemail=TokenEmail
        vigente.creacion=datetime.now()
        vigente.activo=True
        vigente.save()
        print('1')
        #SendEmailFiatUserCode(request.data['usuario'])
        SendEmailFiatUserToken(request.data['usuario'],request.data['idioma']) 
        print('2')
        return Response({"mensaje": mensaje,"valido":valido},status=status.HTTP_200_OK) 
       
    except tUserFiat.DoesNotExist:
        return Response({"mensaje": "Usuario No existe.Token no creadoxx.","valido":"False"},status=status.HTTP_200_OK)
    except:
        return Response({"mensaje": "Error Usuario no existexx","valido":"False"},status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@csrf_exempt
def ValidacionUsuario(request,user):
    try:
        #sendemail()
        #usuario = User.objects.get(username=request.data['username'])
        usuario = User.objects.get(username=user)
        #token, created = Token.objects.get_or_create(user=usuario)
        return Response({"mensaje": "Accesar al modulo FIAT.","existe":"True","email":usuario.email},status=status.HTTP_200_OK) 
    except User.DoesNotExist:
        #return Response({"mensaje": "Crear Cuenta","existe":False},status=status.HTTP_400_BAD_REQUEST)
        return Response({"mensaje": "Crea tu contraseña de ingreso al modulo FIAT.","existe":"False"},status=status.HTTP_200_OK)

@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def get_users_defix(request):
    perfil=Perfil.objects.get(usuario=request.user)
    if verificar_permiso(perfil,'UsuariosDefix','leer'):
        if perfil:
            url = 'https://testnet.defix3.com:3070/api/v1/get-users-defix'
            response = requests.get(url, headers={'Authorization':'Token caballoviejo'})
            data = response.json()
            return Response(data,status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([AllowAny])
def get_comision(request, coin):
    if (coin == "NEAR"):
        comision = Comision.objects.get(coin=coin)
        data = ComisionSerializer(comision).data
        url = 'https://nearblocks.io/api/near-price'
        response = requests.get(url)
        item = response.json()
        data['transfer'] = data['transfer'] / item['usd']
        return Response(data,status=status.HTTP_200_OK)
    comision = Comision.objects.get(coin=coin)
    data = ComisionSerializer(comision).data
    return Response(data,status=status.HTTP_200_OK)


@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def get_users_admin(request):
    perfil=Perfil.objects.get(usuario=request.user)
    data = []
    if verificar_permiso(perfil,'UsersAdmin','leer'):
        if perfil:
            perfiles=Perfil.objects.all()
            for dato in perfiles:
                permisos_usuario=  Permiso.objects.filter(perfil=dato)
                permisitos = []
                for permix in permisos_usuario:
                    permisitos.append({
                        'modulo':permix.modulo.nombre,
                        'id':permix.id,
                        'leer':permix.leer,
                        'escribir':permix.escribir,
                        'borrar':permix.borrar,
                        'actualizar':permix.actualizar
                    })
                data.append({
                    'username':dato.usuario.username,
                    'email':dato.usuario.email,
                    'tipo':dato.tipo,
                    'id':dato.id,
                    'activo': dato.activo,
                    'permisos': permisitos
                })
            return Response(data,status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(["POST"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def get_transaction_history(request):
    perfil=Perfil.objects.get(usuario=request.user)
    if verificar_permiso(perfil,'Transacciones','leer'):
        if perfil:
            data=request.data
            #engine = pg.connect("dbname='defix3' user='gf' host='157.230.2.213' port='5432' password='uPKsp22tBeBC506WRBv21d7kniWiELwg'")
            engine = create_engine('postgresql+psycopg2://gf:uPKsp22tBeBC506WRBv21d7kniWiELwg@157.230.2.213/defix3')
            query = "select * from transactions where \
                                                ((from_defix = '" + data['defixId'] + "' or to_defix = '" + data['defixId'] + "') or ('%%' = '" + data['defixId'] + "' or '%%' = '" + data['defixId'] + "'))\
                                                and (coin = '" + data['coin'] + "' or '%%' = '" + data['coin'] + "')\
                                                and (date_year = '" + data['date_year'] + "' or '%%' = '" + data['date_year'] + "')\
                                                and (date_month = '" + data['date_month'] + "' or '%%' = '" + data['date_month'] + "')"
            df = pd.read_sql_query(query, con=engine)
            return JsonResponse(json.loads(df.to_json(orient='records')), safe = False,status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def get_balance_defix(request):
    perfil=Perfil.objects.get(usuario=request.user)
    if verificar_permiso(perfil,'Balance','leer'):
        if perfil:
            #engine = pg.connect("dbname='defix3' user='gf' host='157.230.2.213' port='5432' password='uPKsp22tBeBC506WRBv21d7kniWiELwg'")
            engine = create_engine('postgresql+psycopg2://gf:uPKsp22tBeBC506WRBv21d7kniWiELwg@157.230.2.213/defix3')
            query = "select * from balance"
            df = pd.read_sql_query(query, con=engine)
            jsondf = json.loads(df.to_json(orient='records'))
            data = []
            contadorBTC = 0.0
            contadorETH = 0.0
            contadorNEAR = 0.0
            contadorUSDT = 0.0
            contadorUSDC = 0.0
            contadorDAI = 0.0
            for user in jsondf:
                contadorBTC = contadorBTC + (user['btc'] or 0)
                contadorETH = contadorETH + (user['eth'] or 0)
                contadorNEAR = contadorNEAR + (user['near'] or 0)
                contadorUSDT = contadorUSDT + (user['usdt'] or 0)
                contadorUSDC = contadorUSDC + (user['usdc'] or 0)
                contadorDAI = contadorDAI + (user['dai'] or 0)

            data.append({"coin": "BTC", "balance": contadorBTC})
            data.append({"coin": "ETH", "balance": contadorETH})
            data.append({"coin": "NEAR", "balance": contadorNEAR})
            data.append({"coin": "USDT", "balance": contadorUSDT})
            data.append({"coin": "USDC", "balance": contadorUSDC})
            data.append({"coin": "DAI", "balance": contadorDAI})
          
            return JsonResponse(data, safe = False,status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(["PUT"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def actualizar_usuario_admin(request):
    perfil=Perfil.objects.get(usuario=request.user)
    if verificar_permiso(perfil,'UsersAdmin','actualizar'):
        if perfil:
            datos = request.data['datos']
            user=User.objects.get(id=datos['id'])
            user.username = datos['username']
            user.email = datos['email']
            user.save()

            perfil_up=Perfil.objects.get(usuario=user)
            perfil_up.activo = datos['activo']
            perfil_up.tipo = datos['tipo']
            perfil_up.save()

            for permisos in datos['permisos']:
                permiso=Permiso.objects.get(id=permisos['id'])
                permiso.leer = permisos['leer']
                permiso.escribir = permisos['escribir']
                permiso.actualizar = permisos['actualizar']
                permiso.borrar = permisos['borrar']
                permiso.save()
            return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

# Lista los paises y sus KYC para ser mostrados en el opcion de KYC en el dApp
@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
#def get_paises(request,observacion):
def get_paises(request):
    data = []
    print(request.user)
    Paises=tPais.objects.filter(habilitado=True)
    for dato in Paises:
        pais=dato.id
        KYC=tkycCabecera.objects.filter(pais_id=dato.id,observacion=request.user)
        if(KYC.filter(estatus='A').count() >=1):
            KYC = KYC.filter(estatus='A')
        elif(KYC.filter(estatus='C').count() >1):
            KYC = KYC.filter(estatus='C').order_by('-id')[:1]
        if KYC.count() != 0:
            for datoKYC in KYC:
                try:
                    kycCabecera=tkycCabecera.objects.get(pais_id=dato.id,observacion=request.user,id=datoKYC.id)
                    estatus=kycCabecera.estatus
                    kycCabeceraId=kycCabecera.id
                except tkycCabecera.DoesNotExist:
                    kycCabecera = None
                    estatus='X'
                    kycCabeceraId=' '
                item = {
                    'id':dato.id,
                    'nombre':dato.nombre,
                    'imagen':settings.RUTA_MEDIA+settings.MEDIA_URL+dato.imagen.name,
                    'coin':dato.coin,
                    'habilitado': dato.habilitado,
                    'estatus': estatus,
                    'kycCabeceraId': kycCabeceraId,
                    'tasa': dato.tasa,
                    'montoventa': dato.montoventa,
                    'montocompra': dato.montocompra,
                    'kyccompra': dato.kyccompra,
                    'kycventa': dato.kycventa,                    
                }
                data.append(item)
                
        else:
            item = {
                'id':dato.id,
                'nombre':dato.nombre,
                'imagen':settings.RUTA_MEDIA+settings.MEDIA_URL+dato.imagen.name,
                'coin':dato.coin,
                'habilitado': dato.habilitado,
                'estatus': 'X',
                'kycCabeceraId': ' ',
                'tasa': dato.tasa,
                'montoventa': dato.montoventa,
                'montocompra': dato.montocompra,
                'kyccompra': dato.kyccompra,
                'kycventa': dato.kycventa,  
            }
            data.append(item)
        
    new_data = sorted(data, key=lambda d: d['estatus'])
    return Response(new_data,status=status.HTTP_200_OK)


@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def get_paisesdoc(request,pais_id):
    data = []
    PaisesDoc=tPaisDocumento.objects.filter(habilitado=True,pais_id=pais_id)
    for dato in PaisesDoc:
        item = {
             'id':dato.id,
             'nombre':dato.nombre,
             'tipo':dato.tipo,
             'habilitado': dato.habilitado,
             'detalle':dato.detalle,
             'opcional':dato.opcional,
             'juridico':dato.juridico,
             'pais_id':dato.pais_id,
             'imagen':'',
             'texto':'',
             'usuario':'',
        }
        data.append(item)
        new_data = sorted(data, reverse=True, key=lambda d: d['id'])
    return Response(new_data,status=status.HTTP_200_OK)

@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def get_paisbancotasa(request,pais_id):
    data = []
    BancoTasa=tPaisBanco.objects.filter(habilitado=True,pais_id=pais_id)
    for dato in BancoTasa:
        item = {
             'id':dato.id,
             'nombre':dato.nombre,
             'tasa':dato.tasa,
             'monto':dato.monto,
             'montomin':dato.montomin,
             'tasaaltomonto':dato.tasaaltomonto,
             'tasav':dato.tasav,
             'montov':dato.montov,
             'montominv':dato.montominv,
             'tasaaltomontov':dato.tasaaltomontov,
             'comision':dato.comision,
             'comisionv':dato.comisionv,
             'pais_id':dato.pais.id,
             'pais_nombre':dato.pais.nombre,
             'pais_coin':dato.pais.coin,
        }
        data.append(item)
        new_data = sorted(data, reverse=True, key=lambda d: d['id'])
    return Response(new_data,status=status.HTTP_200_OK)    

@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def get_tcuenta(request,observacion):
    data = []
    Cuentas=tkycCuenta.objects.filter(kyccabecera=observacion)
    for dato in Cuentas:
        estatus='X'
        item = {
             'id':dato.id,
             'bancoId':dato.banco.id,
             'banco':dato.banco.nombre,
             'tipopagoId':dato.tipopago.id,
             'tipopago':dato.tipopago.nombre,
             'titular':dato.titular,
             'cedula':dato.cedula,
             'telefono':dato.telefono,
             'numerocuenta':dato.numerocuenta,
             'tipocuenta':dato.tipocuenta,
             'habilitado': dato.habilitado,
             'estatus': estatus,
             'kyccabecera':dato.kyccabecera.id,
             'tasa':dato.banco.tasa,
             'monto':dato.banco.monto,
             'montomin':dato.banco.montomin,
             'tasaaltomonto':dato.banco.tasaaltomonto,
             'tasav':dato.banco.tasav,
             'montov':dato.banco.montov,
             'montominv':dato.banco.montominv,
             'tasaaltomontov':dato.banco.tasaaltomontov,
             'comision':dato.banco.comision,
             'comisionv':dato.banco.comisionv,
        }
        data.append(item)
    return Response(data,status=status.HTTP_200_OK)

@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def get_tcuenta_defix(request,observacion):
    data = []
    Cuentas=tkycCuentaDefix.objects.filter(pais=observacion)
    for dato in Cuentas:
        estatus='X'
        item = {
             'id':dato.id,
             'bancoId':dato.banco.id,
             'banco':dato.banco.nombre,
             'tipopagoId':dato.tipopago.id,
             'tipopago':dato.tipopago.nombre,
             'titular':dato.titular,
             'cedula':dato.cedula,
             'telefono':dato.telefono,
             'numerocuenta':dato.numerocuenta,
             'tipocuenta':dato.tipocuenta,
             'habilitado': dato.habilitado,
             'estatus': estatus,
             'pais':dato.pais.id,
             'tasa':dato.banco.tasa,
             'monto':dato.banco.monto,
             'montomin':dato.banco.montomin,
             'tasaaltomonto':dato.banco.tasaaltomonto,
             'tasav':dato.banco.tasav,
             'montov':dato.banco.montov,
             'montominv':dato.banco.montominv,
             'tasaaltomontov':dato.banco.tasaaltomontov,
             'comision':dato.banco.comision,
             'comisionv':dato.banco.comisionv,
        }
        data.append(item)
    return Response(data,status=status.HTTP_200_OK)  

@api_view(["POST"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def crear_fiat(request):     
    datos = request.data
    user = User.objects.get(username=request.user)
    Cuenta=tkycCuentaDefix.objects.get(id=datos['idCuenta']) if datos['accion'] == 'C' else tkycCuenta.objects.get(id=datos['idCuenta']) 
    Cuentas=Cuenta
    tbanco=tPaisBanco.objects.get(id=Cuentas.banco.id)
    fpais = tPais.objects.get(id=tbanco.pais.id)
    nbanco=tbanco.nombre
    ttipopago=tTipoPago.objects.get(id=Cuentas.tipopago.id)
    ntipopago=ttipopago.nombre
    nreferencia=random.randint(10000000000, 99999999999)
    nmonto=Decimal(datos['cantidad'])/ Cuentas.banco.tasa if datos['accion'] == 'C' else Decimal(datos['cantidad'])*Cuentas.banco.tasav
    FiatTransaccionNew=FiatTransaccion(
        referencia=nreferencia,
        accion= 'C' if datos['accion'] == 'C' else 'V',
        cantidad=Decimal(datos['cantidad']),
        banco=tbanco,
        banco_nombre=nbanco,
        tasa=Cuentas.banco.tasa if datos['accion'] == 'C' else Cuentas.banco.tasav,
        monto= nmonto,
        tipopago=ttipopago,
        tipopago_nombre=ntipopago,
        titular=Cuentas.titular,
        cedula=Cuentas.cedula,
        telefono=Cuentas.telefono,
        numerocuenta=Cuentas.numerocuenta,
        tipocuenta=Cuentas.tipocuenta,
        pais = fpais,
        comision= Cuentas.banco.comision if datos['accion'] == 'C' else Cuentas.banco.comisionv,
        cripto=datos['cripto'],
        observacion=request.user,
        usuario=request.user,
        email=user.email,
        wallet=datos['wallet'])
    FiatTransaccionNew.save()
    SendEmailFiat(datos['accion'],datos['cantidad'],nmonto,request.user,nreferencia,user.email,datos['cripto'])
    SendEmailFiatUser(datos['accion'],datos['cantidad'],nmonto,request.user,nreferencia,user.email,datos['cripto'],datos['idioma'])
    return Response(status=status.HTTP_200_OK)

@api_view(["POST"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@csrf_exempt
def crear_kyc(request):     
    datos = request.data
    user = User.objects.get(username=request.user)
    pais = tPais.objects.get(id=datos['cabecera-id_pais'])
    cabecera=tkycCabecera(pais=pais,
                          juridico=datos['cabecera-juridico'],
                          usuario=request.user,
                          observacion=request.user,
                          email=user.email)
    cabecera.save()
    for detalle in datos:
        if 'cuerpo-' in detalle: 
            if '-I-' in detalle:
                #print('err dato de leiner',datos[detalle])
                detalle = tkycDetalle(kyccabecera=cabecera,documento=detalle.replace('cuerpo-I-',''),imagen=datos[detalle],tipo='I')
            else:
                detalle = tkycDetalle(kyccabecera=cabecera,documento=detalle.replace('cuerpo-T-',''),texto=datos[detalle],tipo='T')
            detalle.save()
    print('email1')
    SendEmailKYC(datos['cabecera-id_pais'],request.user,user.email)
    SendEmailKYCUser(datos['cabecera-id_pais'],request.user,user.email,datos['idioma'])
    print('email2',datos['cabecera-id_pais'],request.user,user.email)
    return Response(status=status.HTTP_200_OK)

# lista los registros de KYC en el Administrador
@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def get_kyccabecera(request):
    data = []
    kycCabecera=tkycCabecera.objects.all()
    for dato in kycCabecera:
        pais = tPais.objects.get(id=dato.pais_id)
        item = {
            'id':dato.id,
            'imagen':settings.RUTA_MEDIA+settings.MEDIA_URL+pais.imagen.name,
            'usuario_id':dato.usuario_id,
            'juridico':dato.juridico,
            'fecha_registro':dato.fecha_registro,
            'banco_cuenta':dato.banco_cuenta,
            'estatus':dato.estatus,
            'observacion':dato.observacion,
            'email':dato.email,
        }
        data.append(item)
        new_data = sorted(data, reverse=True, key=lambda d: d['id'])
    return Response(new_data,status=status.HTTP_200_OK)

@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def get_fiat(request):
    data = []
    kycCabecera=FiatTransaccion.objects.all()
    for dato in kycCabecera:
        pais = tPais.objects.get(id=dato.pais_id)
        if dato.adjuntofiat:
            adjuntofiat=settings.RUTA_MEDIA+settings.MEDIA_URL+dato.adjuntofiat.name
        else:
            adjuntofiat='vacio'
        item = {
            'id':dato.id,
            'imagen':settings.RUTA_MEDIA+settings.MEDIA_URL+pais.imagen.name,
            'estatus':dato.estatus,
            'observacion':dato.observacion,
            'accion':dato.accion,
            'referencia':dato.referencia,
            'pais':dato.pais_id,
            'cripto':dato.cripto,
            'tasa':dato.tasa,
            'comision':dato.comision,
            'cantidad':dato.cantidad,
            'monto':dato.monto,
            'banco':dato.banco_id,
            'banco_nombre':dato.banco_nombre,
            'tipopago':dato.tipopago_id,
            'tipopago_nombre':dato.tipopago_nombre,
            'titular':dato.titular,
            'cedula':dato.cedula,
            'telefono':dato.telefono,
            'numerocuenta':dato.numerocuenta,
            'tipocuenta':dato.tipocuenta,
            'usuario':dato.usuario_id,
            'fecha_creado':dato.fecha_creado,
            'fecha_asignado':dato.fecha_asignado,
            'usuario_asignado':dato.usuario_asignado,
            'fecha_procesado':dato.fecha_procesado,
            'fecha_completado':dato.fecha_completado,
            'fecha_anulado':dato.fecha_anulado,  
            'coin':pais.coin,  
            'adjuntofiat':adjuntofiat,   
            'email':dato.email, 
            'wallet':dato.wallet, 
        }
        data.append(item)
    new_data = sorted(data, reverse=True, key=lambda d: d['id'])
    return Response(new_data,status=status.HTTP_200_OK)

@api_view(["POST"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def get_fiat_user(request):
    data = []
    if request.data['allfiat']: 
        kycCabecera=FiatTransaccion.objects.filter(observacion=request.user)
    else:
        
        kycCabecera=FiatTransaccion.objects.filter(observacion=request.user,estatus__in=[1,2,3])
    for dato in kycCabecera:
        pais = tPais.objects.get(id=dato.pais_id)
        adjuntofiat='vacio'
        if dato.adjuntofiat:
            adjuntofiat=settings.RUTA_MEDIA+settings.MEDIA_URL+dato.adjuntofiat.name
        else:
            adjuntofiat='vacio'    
        item = {
            'id':dato.id,
            'imagen':settings.RUTA_MEDIA+settings.MEDIA_URL+pais.imagen.name,
            'estatus':dato.estatus,
            'observacion':dato.observacion,
            'accion':dato.accion,
            'referencia':dato.referencia,
            'pais':dato.pais_id,
            'cripto':dato.cripto,
            'tasa':dato.tasa,
            'comision':dato.comision,
            'cantidad':dato.cantidad,
            'monto':dato.monto,
            'banco':dato.banco_id,
            'banco_nombre':dato.banco_nombre,
            'tipopago':dato.tipopago_id,
            'tipopago_nombre':dato.tipopago_nombre,
            'titular':dato.titular,
            'cedula':dato.cedula,
            'telefono':dato.telefono,
            'numerocuenta':dato.numerocuenta,
            'tipocuenta':dato.tipocuenta,
            'usuario':dato.usuario_id,
            'fecha_creado':dato.fecha_creado,
            'fecha_asignado':dato.fecha_asignado,
            'usuario_asignado':dato.usuario_asignado,
            'fecha_procesado':dato.fecha_procesado,
            'fecha_completado':dato.fecha_completado,
            'fecha_anulado':dato.fecha_anulado,  
            'coin':pais.coin,  
            'adjuntofiat':adjuntofiat,
            'email':dato.email,
            'wallet':dato.wallet,
        }
        data.append(item)
    new_data = sorted(data, reverse=True, key=lambda d: d['id'])
    return Response(new_data,status=status.HTTP_200_OK)



@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def get_fiat_estatus(request,observacion):
    data = []
    fiat=FiatTransaccion.objects.get(id=observacion)
    dato=fiat
    adjuntofiat='vacio'
    if dato.adjuntofiat:
        adjuntofiat=settings.RUTA_MEDIA+settings.MEDIA_URL+dato.adjuntofiat.name
    else:
        adjuntofiat='vacio'    
    item = {
        'id':dato.id,
        'estatus':dato.estatus,
        'fecha_creado':dato.fecha_creado,
        'fecha_asignado':dato.fecha_asignado,
        'usuario_asignado':dato.usuario_asignado,
        'fecha_procesado':dato.fecha_procesado,
        'fecha_completado':dato.fecha_completado,
        'fecha_anulado':dato.fecha_anulado,  
        'adjuntofiat':adjuntofiat,
    }
    data.append(item)
    new_data = sorted(data, reverse=True, key=lambda d: d['id'])
    return Response(new_data,status=status.HTTP_200_OK)





@api_view(["PUT"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def put_fecha_fiat(request):
    datos = request.data['datos']
    estatus=str(datos['estatus'])
    fiat=FiatTransaccion.objects.get(id=datos['id'],observacion= datos['observacion'])
    fiat.estatus = datos['estatus']
    if '2' == estatus:
        fiat.fecha_asignado = str(datetime.now())
    if '3' == estatus:
        fiat.fecha_procesado = str(datetime.now())
    if '4' == estatus:
        fiat.fecha_completado = str(datetime.now())
    if '5' == estatus:
        fiat.fecha_anulado = str(datetime.now())                        
    fiat.save()
    return Response(status=status.HTTP_200_OK)

@api_view(["PUT"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def confirm_sell(request):
    datos = request.data['datos']
    fiat=FiatTransaccion.objects.get(id=datos['id'],observacion=request.user)
    fiat.estatus = 4
    fiat.fecha_completado = str(datetime.now())                       
    fiat.save()
    return Response(status=status.HTTP_200_OK)

@api_view(["PUT"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def cancel_buy(request):
    datos = request.data['datos']
    fiat=FiatTransaccion.objects.get(id=datos['id'],observacion=request.user)
    fiat.estatus = 5
    fiat.fecha_anulado = str(datetime.now())                         
    fiat.save()
    return Response(status=status.HTTP_200_OK)

@api_view(["GET"])
@csrf_exempt
def get_kycdetalle(request,kyccabecera_id):
    data = []
    kycdetalle=tkycDetalle.objects.filter(kyccabecera_id=kyccabecera_id)
    for dato in kycdetalle:
        #print(dato)
        item = {
             'id':dato.id,
             'estatus':dato.estatus,
             'kyccabecera_id':dato.kyccabecera_id,
             'texto': dato.texto,
             'documento': dato.documento,
             'imagen':settings.RUTA_MEDIA+settings.MEDIA_URL+dato.imagen.name,
             'paisdocumento_id':dato.paisdocumento_id,
             'observacion':dato.observacion,
             'tipo':dato.tipo,
        }
        data.append(item)
    return Response(data,status=status.HTTP_200_OK)

#@api_view(["PUT"])
#@csrf_exempt
#@authentication_classes([TokenAuthentication])
def SendEmailFiat(accion,cantidad,monto,user,referencia,email,cripto):
        #datos=request.data
        #user = User.objects.get(username=request.user)
        operacion = ' '
        if accion=='V':
            operacion = 'VENTA'
            valor=cantidad
        else:
            operacion = 'COMPRA'  
            valor=monto  
        html_message = render_to_string('fiat.html', 
            { 'user_defix': 'ADMINISTRADOR DEFIX',
            'user_fiat': user,
            'operacion' : operacion,
            'referencia':  referencia,
            'monto':valor,
            'moneda':cripto,}
            )
        to ,from_email = 'noreply@defix3.com', email
        text_content = 'This is an important message.'
        msg = EmailMultiAlternatives(operacion, text_content, from_email, [to])
        msg.attach_alternative(html_message, "text/html")
        msg.send()
        return Response({"mensaje": "OK"},status=status.HTTP_200_OK) 

#@api_view(["PUT"])
#@csrf_exempt
#@authentication_classes([TokenAuthentication])
def SendEmailFiatUser(accion,cantidad,monto,user,referencia,email,cripto,idioma):
        operacion = ' '
        valor=0
        if accion=='V':
            operacion = 'VENTA'
            valor=cantidad
        else:
            operacion = 'COMPRA'  
            valor=monto

        html_message = render_to_string('fiatuser.html' if idioma=='en' else 'fiatuser_es.html', 
            { 'user_defix': 'ADMINISTRADOR DEFIX',
            'user_fiat': user,
            'operacion' : operacion,
            'referencia':  referencia,
            'monto':valor,
            'moneda':cripto,}
            )
        from_email,to = 'noreply@defix3.com', email
        text_content = 'This is an important message.'
        msg = EmailMultiAlternatives(operacion, text_content, from_email, [to])
        msg.attach_alternative(html_message, "text/html")
        msg.send()
        return Response({"mensaje": "OK"},status=status.HTTP_200_OK) 

#@api_view(["PUT"])
#@csrf_exempt
#@authentication_classes([TokenAuthentication])
def SendEmailFiatUserCode(UserName):
    try:
        user = User.objects.get(username=UserName)
        Email= user.email
        vigente = tUserFiat.objects.get(usuario=user)
        TokenEmail=vigente.tokenemail

        operacion = 'Código de verificación de FIAT'
      
        html_message = render_to_string('fiatusercode.html', 
            { 'user_defix': 'ADMINISTRADOR DEFIX',
            'user_fiat': UserName,
            'tokenemail':  TokenEmail,}
            )
        from_email,to = 'noreply@defix3.com', Email
        text_content = 'This is an important message.'
        msg = EmailMultiAlternatives(operacion, text_content, from_email, [to])
        msg.attach_alternative(html_message, "text/html")
        msg.send()
        return Response({"mensaje": "OK"},status=status.HTTP_200_OK) 
    except:
        return Response({"mensaje": "NOT OK"},status=status.HTTP_400_BAD_REQUEST)

def SendEmailFiatUserToken(UserName,idioma):
    try:
        print('3')
        user = User.objects.get(username=UserName)
        Email= user.email
        vigente = tUserFiat.objects.get(usuario=user)
        TokenEmail=list(vigente.tokenemail)
        print(TokenEmail)
        print (TokenEmail[0])
        operacion = 'Código de verificación de FIAT'
      
        html_message = render_to_string('fiatusercode.html'  if idioma=='en' else 'fiatusercode_es.html', 
            { 'user_defix': 'ADMINISTRADOR DEFIX',
            'user_fiat': UserName,
            't1':TokenEmail[0],
            't2':TokenEmail[1],
            't3':TokenEmail[2],
            't4':TokenEmail[3],
            't5':TokenEmail[4]
            }
            )
        print('3')
        from_email,to = 'noreply@defix3.com', Email
        text_content = 'This is an important message.'
        msg = EmailMultiAlternatives(operacion, text_content, from_email, [to])
        msg.attach_alternative(html_message, "text/html")
        msg.send()
        return Response({"mensaje": "OK"},status=status.HTTP_200_OK)
    except:
        return Response({"mensaje": "NOT OK"},status=status.HTTP_400_BAD_REQUEST)

@api_view(["PUT"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def SendEmailEstatusFIAT(request):
        datos = request.data['datos']
        estado=' '
        if datos['estatus']=='2':
            estado='Asignado'
        if datos['estatus']=='3':
            estado='En Proceso'
        if datos['estatus']=='4':
            estado='Completado'
        if datos['estatus']=='5':
            estado='Anulado'
        if datos['accion']=='V':
            operacion = 'Operacion VENTA Nro.'+str(datos['referencia'])
            operaciont = 'VENTA'
        else:
            operacion = 'Operacion COMPRA Nro.'+str(datos['referencia'])
            operaciont = 'COMPRA'
        html_message = render_to_string('cambioestatus_es.html', 
            {'user_fiat': datos['observacion'],
            'operacion' : operacion,
            'operaciont' : operaciont,
            'numero':datos['referencia'],
            'estatus':estado,}
            )
        from_email,to = 'noreply@defix3.com', datos['email']
        text_content = 'This is an important message.'
        msg = EmailMultiAlternatives(operacion, text_content, from_email, [to])
        msg.attach_alternative(html_message, "text/html")
        msg.send()
        return Response({"mensaje": "OK"},status=status.HTTP_200_OK) 

@api_view(["PUT"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
def SendEmailEstatusKYC(request):
    datos = request.data
    estado=' '
    if datos['estatus']=='R':
        estado='En Revisión'
    if datos['estatus']=='A':
        estado='Aprobado'
    if datos['estatus']=='C':
        estado='Cancelado'
    operacion = 'KYC Nro.'+str(datos['numero'])
    html_message = render_to_string('cambioestatusKYC_es.html', 
        {'user_kyc' : datos['user_kyc'],
         'operacion' : operacion,
         'numero' : datos['numero'],
         'estatus' : estado,}
            )
    from_email,to = 'noreply@defix3.com', datos['email']
    text_content = 'This is an important message.'
    msg = EmailMultiAlternatives(operacion, text_content, from_email, [to])
    msg.attach_alternative(html_message, "text/html")
    msg.send()
    return Response({"mensaje": "OK"},status=status.HTTP_200_OK)

#@api_view(["PUT"])
#@csrf_exempt
#@authentication_classes([TokenAuthentication])
def SendEmailKYC(idpais,user,email):
    try:
        pais=tPais.objects.get(id=idpais)
        operacion = 'REGISTRO DE KYC en ' + pais.nombre
        html_message = render_to_string('kyc.html' , 
            { 'user_defix': 'ADMINISTRADOR DEFIX',
            'user_fiat': user,
            'operacion' : operacion,
            }
            )
        to ,from_email = 'noreply@defix3.com', email
        #to ,from_email = email, email
        text_content = 'This is an important message.'
        msg = EmailMultiAlternatives(operacion, text_content, from_email, [to])
        msg.attach_alternative(html_message, "text/html")
        msg.send()
        return Response({"mensaje": "OK"},status=status.HTTP_200_OK)     
    except:
        return Response({"mensaje": "NOT OK"},status=status.HTTP_400_BAD_REQUEST)

#@api_view(["PUT"])
#@csrf_exempt
#@authentication_classes([TokenAuthentication])
def SendEmailKYCUser(idpais,user,email,idioma):
    try:
        pais=tPais.objects.get(id=idpais)
        operacion = 'REGISTRO DE KYC en ' + pais.nombre
        html_message = render_to_string('kycuser.html'  if idioma=='en' else 'kycuser_es.html', 
            { 'user_defix': 'ADMINISTRADOR DEFIX',
            'user_fiat': user,
            'operacion' : operacion,
            'pais' : pais.nombre,
            }
            )
        from_email,to = 'noreply@defix3.com', email
        #to ,from_email = email, email
        text_content = 'This is an important message.'
        msg = EmailMultiAlternatives(operacion, text_content, from_email, [to])
        msg.attach_alternative(html_message, "text/html")
        msg.send()
        return Response({"mensaje": "OK"},status=status.HTTP_200_OK)     
    except:
        return Response({"mensaje": "NOT OK"},status=status.HTTP_400_BAD_REQUEST)






# Funcion tipo vista para generar Excel con el historico de proformas
@api_view(["POST", "GET"])
@csrf_exempt
def generar_historico_fiat(request,fecha_inicio,fecha_fin):

    params=request.query_params.copy()
    user = True
    if user:
        perfil=Perfil.objects.get(usuario=user)
        try:
            if verificar_permiso(perfil, 'Paises', 'leer'):
                """ Data inicial """
                # Obtner el rango de fechas para el filtro

                ## Filtrar transacciones
                transacciones=FiatTransaccion.objects.filter(fecha_creado__range=[fecha_inicio, fecha_fin])
                # Excel
                i=0
                response=HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition']='attachment;filename="Transacciones FIAT %s&%s.xls"' % ('fecha_inicio', 'fecha_fin')
                excel_wb=Workbook(encoding='utf-8')
                excel_ws=excel_wb.add_sheet('Libro1') # ws es Work Sheet
                # Añadiendo estiloeasyxf5000
                excel_ws.col(3).width = 2500
                excel_ws.col(4).width = 5000
                excel_ws.col(5).width = 5000
                excel_ws.col(6).width = 5000
                excel_ws.col(7).width = 3500
                excel_ws.col(8).width = 3500
                estilo=easyxf('font: bold 1')
                ## Primera fila del excel
                excel_ws.write(i, 0, 'Fecha Creación', estilo)
                excel_ws.write(i, 1, 'Estatus', estilo)
                excel_ws.write(i, 2, 'Usuario Defix', estilo)
                excel_ws.write(i, 3, 'Acción', estilo)
                excel_ws.write(i, 4, 'Referencia', estilo)
                excel_ws.write(i, 5, 'País', estilo)
                excel_ws.write(i, 6, 'Cripto', estilo)
                excel_ws.write(i, 7, 'Tasa', estilo)
                excel_ws.write(i, 8, 'Cantidad', estilo)
                excel_ws.write(i, 9,' Comisión', estilo)
                excel_ws.write(i, 10,'Monto', estilo)
                excel_ws.write(i, 11,'Banco', estilo)
                excel_ws.write(i, 12,'Tipo de Pago', estilo)
                excel_ws.write(i, 13,'Titular', estilo)
                excel_ws.write(i, 14,'Cédula', estilo)
                excel_ws.write(i, 15,'Teléfono', estilo)
                excel_ws.write(i, 16,'Número Cuenta', estilo)
                excel_ws.write(i, 17,'Usuario', estilo)
                excel_ws.write(i, 18,'Fecha Asignacion', estilo)
                excel_ws.write(i, 19,'Usuario Asignado', estilo)
                excel_ws.write(i, 20,'Fecha Procesado', estilo)
                excel_ws.write(i, 21,'Fecha Completado', estilo)
                excel_ws.write(i, 22,'Fecha Anulado', estilo)
                excel_ws.write(i, 23,'Email', estilo)
                excel_ws.write(i, 24,'Wallet', estilo)
                i=i + 1
                # Creador de filas
                taccion=''
                for f in transacciones:
                    if f.accion=='V':
                        taccion='VENTA'
                    else:
                        taccion='COMPRA'
                    excel_ws.write(i, 0, '%s' % (f.fecha_creado.strftime('%Y-%m-%d')))
                    excel_ws.write(i, 1, '%s' % (f.get_estatus_display()))
                    excel_ws.write(i, 2, '%s' % (f.observacion))
                    excel_ws.write(i, 3, '%s' % (taccion))
                    excel_ws.write(i, 4, '%s' % (f.referencia))
                    excel_ws.write(i, 5, '%s' % (f.pais.nombre))
                    excel_ws.write(i, 6, '%s' % (f.cripto))
                    excel_ws.write(i, 7, '%s' % (f.tasa))
                    excel_ws.write(i, 8, '%s' % (f.cantidad))
                    excel_ws.write(i, 9, '%s' % (f.comision))
                    excel_ws.write(i, 10, '%s' % (round((float(f.tasa)*float(f.cantidad))+float(f.comision),2)))
                    excel_ws.write(i, 11, '%s' % (f.banco_nombre))
                    excel_ws.write(i, 12, '%s' % (f.tipopago_nombre))
                    excel_ws.write(i, 13, '%s' % (f.titular))
                    excel_ws.write(i, 14, '%s' % (f.cedula))
                    excel_ws.write(i, 15, '%s' % (f.telefono))
                    excel_ws.write(i, 16, '%s' % (f.numerocuenta))
                    excel_ws.write(i, 17, '%s' % (f.usuario))
                    excel_ws.write(i, 18, '%s' % (f.fecha_asignado))
                    excel_ws.write(i, 19, '%s' % (f.usuario_asignado))
                    excel_ws.write(i, 20, '%s' % (f.fecha_procesado))
                    excel_ws.write(i, 21, '%s' % (f.fecha_completado))
                    excel_ws.write(i, 22, '%s' % (f.fecha_anulado))
                    excel_ws.write(i, 23, '%s' % (f.email))
                    excel_ws.write(i, 24, '%s' % (f.wallet))
                    i=i + 1
                excel_wb.save(response)
                return response
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            #print(e)
            return Response('%s' % (e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)        