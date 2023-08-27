# Imports
from .serializers import *
from .models import *
from rest_framework import viewsets,status
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
from django.http import JsonResponse
import requests
import pandas as pd
import psycopg2 as pg
from sqlalchemy import create_engine
import json


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
                print(user)
            return Response(serializer,status=status.HTTP_200_OK)

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
@permission_classes([IsAuthenticated])
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
    authentication_classes=[BasicAuthentication]
    serializer_class=AuthTokenSerializer
    queryset=User.objects.none()
    # {"username":"super","password":"super"}
    def create(self,request,format=None):
        data = request.data
        try:
            print(data['username'])
            if '@' in data['username'] and '.' in data['username']:
                print('email')
                user = User.objects.get(email__exact=request.data['username'])
            else:
                print('username')
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

@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_users_defix(request):
    perfil=Perfil.objects.get(usuario=request.user)
    if verificar_permiso(perfil,'UsuariosDefix','leer'):
        if perfil:
            url = 'https://defix3.com:3071/api/v1/get-users-defix'
            response = requests.get(url, headers={'Authorization':'Token contr@sen@dj@ngo'})
            data = response.json()
            return Response(data,status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(["GET"])
@csrf_exempt
@authentication_classes([BasicAuthentication])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def get_transaction_history(request):
    perfil=Perfil.objects.get(usuario=request.user)
    if verificar_permiso(perfil,'Transacciones','leer'):
        if perfil:
            data=request.data
            #engine = pg.connect("dbname='defix3' user='gf' host='157.230.2.213' port='5432' password='uPKsp22tBeBC506WRBv21d7kniWiELwg'")
            engine = create_engine('postgresql+psycopg2://defix3:sg2sRpizi1zvb67CUPgmwd17Q4F5xhAg@127.0.0.1/defix3')
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
@permission_classes([IsAuthenticated])
def get_balance_defix(request):
    perfil=Perfil.objects.get(usuario=request.user)
    if verificar_permiso(perfil,'Balance','leer'):
        if perfil:
            #engine = pg.connect("dbname='defix3' user='gf' host='157.230.2.213' port='5432' password='uPKsp22tBeBC506WRBv21d7kniWiELwg'")
            engine = create_engine('postgresql+psycopg2://defix3:sg2sRpizi1zvb67CUPgmwd17Q4F5xhAg@127.0.0.1/defix3')
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
@permission_classes([IsAuthenticated])
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

