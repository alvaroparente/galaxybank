from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/cliente/', views.dashboard_cliente, name='dashboard_cliente'),
    path('dashboard/gerente/', views.dashboard_gerente, name='dashboard_gerente'),
    
    # URLs de registro
    path('registro/', views.registro_etapa1, name='registro'),
    path('registro/etapa1/', views.registro_etapa1, name='registro_etapa1'),
    path('registro/etapa2/', views.registro_etapa2, name='registro_etapa2'),
    path('registro/etapa3/', views.registro_etapa3, name='registro_etapa3'),
    path('registro/cancelar/', views.registro_cancelar, name='registro_cancelar'),
    
    path('', views.home_redirect, name='home_redirect'),
]
