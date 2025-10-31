from django.urls import path
from . import views
urlpatterns = [

path("panel/", views.panel_general_admin, name="panel_administrador"),

path("gestionar_usuarios/", views.gestionar_usuarios, name="gestionar_usuarios"),


path("reservas/gestionar/", views.gestionar_reservas, name="gestionar_reservas"),
path("noticias/", views.listar_noticias, name="listar_noticias"),

path("noticias/eliminar/<int:id_noticia>/", views.eliminar_noticia, name="eliminar_noticia"),

path('vehiculos/', views.lista_vehiculos, name='lista_vehiculos'),
path('vehiculo/<int:pk>/', views.detalle_vehiculo, name='detalle_vehiculo'),
path('activar_validacion/', views.activar_validacion, name='activar_validacion'),
    path('finalizar_validacion/', views.finalizar_validacion, name='finalizar_validacion'),
    
path('sorteos/', views.sorteos_list_create, name='sorteos_list_create'),

path('sorteo/<int:sorteo_id>/vehiculos/', views.sorteo_vehiculos, name='sorteo_vehiculos'),

path("reserva/<int:id_reserva>/detalle-pagos/", views.detalle_reserva_con_pagos, name="detalle_reserva_con_pagos"),
path("pago/<int:pago_id>/eliminar/", views.eliminar_pago, name="eliminar_pago"),

path('administrador/menu_reporte/<int:sorteo_id>/', views.menu_reporte_sorteo, name='menu_reporte_sorteo'),
path("reporte_ganadores/<int:sorteo_id>/", views.reporte_sorteo_pdf, name="reporte_sorteo_pdf"),


path('filtro-reservas/', views.filtro_reservas, name='filtro_reservas'),
path('reporte-reservas-pdf/', views.reporte_reservas_pdf, name='reporte_reservas_pdf'),

path("novedades/", views.listar_novedades, name="listar_novedades"),

]