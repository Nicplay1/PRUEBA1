from django.urls import path
from . import views


urlpatterns = [
    
    path("panel/", views.panel_general_vigilante, name="panel_vigilante"),
    
    path('parqueadero/registrar/', views.registrar_parqueadero, name='registrar_detalle_parqueadero'),
    path('parqueadero/salida/<int:id_detalle>/', views.poner_hora_salida, name='poner_hora_salida'),
    path('parqueadero/pago/<int:id_detalle>/', views.realizar_pago, name='realizar_pago'),
    
    
    path('correspondencia/', views.registro_correspondencia_view, name='registro_correspondencia'),
    path('registrar-entrega/', views.registrar_entrega_view, name='registrar_entrega'),
    
    path('paquetes', views.correspondencia, name="correspondencia"),
    path('registrar_paquete/', views.registrar_paquete, name="registrar_paquete"),
    path('entregar_paquete/', views.entregar_paquete, name="entregar_paquete"),
    path('buscar-paquete/', views.buscar_paquete, name='buscar_paquete'),
    
    path('novedades/', views.novedades_view, name='novedades'),

    path("reporte_visitantes/", views.reporte_visitantes_pdf, name="reporte_visitantes"),
    path("menu-reporte-parqueadero/", views.menu_reporte_parqueadero, name="menu_reporte_parqueadero"),
    
]


