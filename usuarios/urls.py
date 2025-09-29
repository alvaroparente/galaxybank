from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/cliente/', views.dashboard_cliente, name='dashboard_cliente'),
    path('dashboard/gerente/', views.dashboard_gerente, name='dashboard_gerente'),
    path('', views.home_redirect, name='home_redirect'),
]
