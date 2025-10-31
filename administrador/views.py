from django.shortcuts import render, redirect, get_object_or_404
from usuario.models import *
from usuario.decorators import *
from django.contrib import messages
from .forms import *
import random
from django.core.mail import send_mail
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date


@rol_requerido([3])
@login_requerido
def panel_general_admin(request):
    return render(request, "administrador/panel.html")

@rol_requerido([3])
@login_requerido
def gestionar_usuarios(request):
    query = request.GET.get("q", "")
    usuarios = Usuario.objects.select_related("id_rol").all()

    # Si es POST → actualizar rol vía AJAX
    if request.method == "POST":
        usuario_id = request.POST.get("usuario_id")
        usuario = get_object_or_404(Usuario, pk=usuario_id)
        form = CambiarRolForm(request.POST, instance=usuario)

        if form.is_valid():
            form.save()
            mensaje = f"Rol de {usuario.nombres} actualizado correctamente."
            status = "success"
        else:
            mensaje = "Error al actualizar el rol. Verifica los datos."
            status = "error"

        # Recargar la tabla después de actualizar
        html = render_to_string("administrador/usuario/tabla_usuarios.html", {
            "usuarios": Usuario.objects.select_related("id_rol").all(),
            "roles": Rol.objects.all()
        })
        return JsonResponse({"html": html, "mensaje": mensaje, "status": status})

    # Si es GET → búsqueda AJAX o carga normal
    if query:
        palabras = query.split()
        for palabra in palabras:
            usuarios = usuarios.filter(
                Q(nombres__icontains=palabra) |
                Q(apellidos__icontains=palabra) |
                Q(correo__icontains=palabra)
            )

    # Si la petición es AJAX → solo retornamos la tabla
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string("administrador/usuario/tabla_usuarios.html", {
            "usuarios": usuarios,
            "roles": Rol.objects.all()
        })
        return JsonResponse({"html": html})

    # Carga normal con todo el template
    return render(request, "administrador/usuario/gestionar_usuarios.html", {
        "usuarios": usuarios,
        "roles": Rol.objects.all(),
        "query": query
    })

    

@rol_requerido([3])
@login_requerido
def gestionar_reservas(request):
    reservas = Reserva.objects.select_related("cod_usuario", "cod_zona").all().order_by("-fecha_reserva")

    if request.method == "POST":
        reserva_id = request.POST.get("reserva_id")
        reserva = get_object_or_404(Reserva, pk=reserva_id)
        form = EditarReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, f" Reserva {reserva.id_reserva} actualizada correctamente.")
            return redirect("gestionar_reservas")
    else:
        form = EditarReservaForm()

    return render(request, "administrador/reservas/gestionar_reservas.html", {
        "reservas": reservas,
        "form": form
    })
    
@rol_requerido([3])
@login_requerido
def detalle_reserva_con_pagos(request, id_reserva):
    reserva = get_object_or_404(Reserva, pk=id_reserva)
    pagos = PagosReserva.objects.filter(id_reserva=reserva)

    form_reserva = EditarReservaForm(instance=reserva)

    if request.method == "POST":
        if "reserva_id" in request.POST:  # Guardar toda la reserva
            form_reserva = EditarReservaForm(request.POST, instance=reserva)
            if form_reserva.is_valid():
                form_reserva.save()
                messages.success(request, f"Reserva {reserva.id_reserva} actualizada correctamente.")
                return redirect("detalle_reserva_con_pagos", id_reserva=id_reserva)
        elif "pago_id" in request.POST:  # Editar estado de pago
            pago_id = request.POST.get("pago_id")
            pago = get_object_or_404(PagosReserva, pk=pago_id)
            form_pago = EstadoPagoForm(request.POST, instance=pago)
            if form_pago.is_valid():
                form_pago.save()
                messages.success(request, f"Pago {pago.id_pago} actualizado correctamente.")
                return redirect("detalle_reserva_con_pagos", id_reserva=id_reserva)

    # Adjuntar form_estado a cada pago
    for pago in pagos:
        pago.form_estado = EstadoPagoForm(instance=pago)

    return render(
        request,
        "administrador/reservas/detalle_reserva_pagos.html",
        {
            "reserva": reserva,
            "pagos": pagos,
            "form_reserva": form_reserva
        },
    )

@rol_requerido([3])
@login_requerido
def eliminar_pago(request, pago_id):
    pago = get_object_or_404(PagosReserva, pk=pago_id)
    reserva_id = pago.id_reserva.id_reserva
    if request.method == "POST":
        pago.delete()
        messages.success(request, f"Pago {pago_id} eliminado correctamente.")
        return redirect("detalle_reserva_con_pagos", id_reserva=reserva_id)


@rol_requerido([3])
@login_requerido
def listar_noticias(request):
    noticias = Noticias.objects.all().order_by("-fecha_publicacion")

    # Crear Noticia
    if request.method == "POST" and "crear" in request.POST:
        form = NoticiasForm(request.POST)
        if form.is_valid():
            noticia = form.save(commit=False)
            noticia.cod_usuario = request.usuario
            noticia.save()
            messages.success(request, "Noticia creada exitosamente ")
            return redirect("listar_noticias")
    # Editar Noticia
    elif request.method == "POST" and "editar" in request.POST:
        noticia = get_object_or_404(Noticias, id_noticia=request.POST.get("id_noticia"))
        form = NoticiasForm(request.POST, instance=noticia)
        if form.is_valid():
            form.save()
            messages.success(request, "Noticia actualizada correctamente ")
            return redirect("listar_noticias")

    else:
        form = NoticiasForm()

    return render(request, "administrador/noticias/listar.html", {
        "noticias": noticias,
        "form": form,
    })



@rol_requerido([3])
@login_requerido
def eliminar_noticia(request, id_noticia):
    noticia = get_object_or_404(Noticias, id_noticia=id_noticia)
    noticia.delete()
    messages.success(request, "Noticia eliminada ")
    return redirect("listar_noticias")


@rol_requerido([3])
@login_requerido
def lista_vehiculos(request):
    vehiculos = VehiculoResidente.objects.all()
    proceso = ProcesoValidacion.objects.first()
    proceso_activo = proceso.activo if proceso else False

    context = {
        'vehiculos': vehiculos,
        'proceso_activo': proceso_activo
    }
    return render(request, 'administrador/vehiculos/lista_vehiculos.html', context)

# Vista de detalle de un vehículo y edición de 'documentos'



@rol_requerido([3])
@login_requerido
def detalle_vehiculo(request, pk):
    vehiculo = get_object_or_404(VehiculoResidente, pk=pk)
    archivos = ArchivoVehiculo.objects.filter(idVehiculo=vehiculo)

    documentos_requeridos = ['SOAT', 'Tarjeta de propiedad', 'Técnico-mecánica', 'Licencia', 'Identidad']
    documentos_subidos = ArchivoVehiculo.objects.filter(
        idVehiculo=vehiculo,
        idTipoArchivo__tipo_documento__in=documentos_requeridos
    ).values_list('idTipoArchivo__tipo_documento', flat=True).distinct()
    tiene_todos = set(documentos_requeridos).issubset(set(documentos_subidos))

    proceso = ProcesoValidacion.objects.first()
    proceso_activo = proceso.activo if proceso else False

    # 🔹 IMPORTANTE: Eliminar la actualización automática aquí
    # Ya no forzamos documentos = True automáticamente
    # Esto permite que el administrador mantenga su elección manual

    if request.method == 'POST':
        form = VehiculoResidenteForm(request.POST, instance=vehiculo)
        if form.is_valid():
            form.save()
            messages.success(request, "Estado de documentos actualizado correctamente.")
            return redirect('detalle_vehiculo', pk=vehiculo.pk)
        else:
            messages.error(request, "Error al actualizar el estado de documentos.")
    else:
        form = VehiculoResidenteForm(instance=vehiculo)

    context = {
        'vehiculo': vehiculo,
        'archivos': archivos,
        'form': form,
        'proceso_activo': proceso_activo,
        'tiene_todos_documentos': tiene_todos,
        'documentos_subidos': documentos_subidos,
        'documentos_requeridos': documentos_requeridos,
    }
    return render(request, 'administrador/vehiculos/detalles_vehiculo.html', context)





@rol_requerido([3])
@login_requerido
def activar_validacion(request):
    proceso, created = ProcesoValidacion.objects.get_or_create(id=1)
    proceso.activo = True
    proceso.save()

    # 🔹 Actualizar SOLO vehículos que no han sido modificados manualmente
    # Podemos asumir que si un vehículo tiene documentos=False pero tiene todos los docs,
    # es porque el admin lo estableció manualmente y no queremos sobrescribirlo
    documentos_requeridos = ['SOAT', 'Tarjeta de propiedad', 'Técnico-mecánica', 'Licencia', 'Identidad']
    
    # Obtener todos los vehículos
    vehiculos = VehiculoResidente.objects.all()
    vehiculos_actualizados = 0

    for vehiculo in vehiculos:
        documentos_subidos = ArchivoVehiculo.objects.filter(
            idVehiculo=vehiculo,
            idTipoArchivo__tipo_documento__in=documentos_requeridos
        ).values_list('idTipoArchivo__tipo_documento', flat=True).distinct()
        
        tiene_todos = set(documentos_requeridos).issubset(set(documentos_subidos))
        
        # Solo actualizar si tiene todos los documentos Y actualmente está en False
        # Esto respeta la decisión manual del administrador si estableció en False
        if tiene_todos and not vehiculo.documentos:
            vehiculo.documentos = True
            vehiculo.save()
            vehiculos_actualizados += 1

    messages.success(request, f"Proceso de validación activado. {vehiculos_actualizados} vehículos actualizados automáticamente.")
    return redirect('lista_vehiculos')




@rol_requerido([3])
@login_requerido
def finalizar_validacion(request):
    proceso, created = ProcesoValidacion.objects.get_or_create(id=1)
    proceso.activo = False
    proceso.save()
    messages.success(request, "Proceso de validación finalizado.")
    return redirect('lista_vehiculos')



@rol_requerido([3])
@login_requerido
def sorteos_list_create(request):
    sorteos = Sorteo.objects.all().order_by('-fecha_creado')

    if request.method == 'POST':
        # Crear sorteo
        if 'crear_sorteo' in request.POST:
            form = SorteoForm(request.POST)
            if form.is_valid():
                fecha_sorteo = form.cleaned_data['fecha_inicio']
                if fecha_sorteo < timezone.now().date():
                    messages.error(request, "No puedes crear un sorteo en una fecha pasada.")
                else:
                    sorteo = form.save()
                    messages.success(request, "Sorteo fue creado correctamente.")
                    return redirect('sorteos_list_create')

        # Liberar parqueaderos propietarios
        elif 'liberar_propietarios' in request.POST:
            parqueaderos = Parqueadero.objects.filter(comunal=True, estado=True)
            parqueaderos.update(estado=False)
            messages.success(request, "Se liberaron todos los parqueaderos de propietarios.")

        # Liberar parqueaderos arrendatarios
        elif 'liberar_arrendatarios' in request.POST:
            parqueaderos = Parqueadero.objects.filter(comunal=False, estado=True)
            parqueaderos.update(estado=False)
            messages.success(request, "Se liberaron todos los parqueaderos de arrendatarios.")

        return redirect('sorteos_list_create')

    else:
        form = SorteoForm()

    context = {
        'sorteos': sorteos,
        'form': form,
    }
    return render(request, 'administrador/sorteo/sorteos.html', context)



@rol_requerido([3])
@login_requerido
def sorteo_vehiculos(request, sorteo_id):
    # Obtener el sorteo
    sorteo = get_object_or_404(Sorteo, id_sorteo=sorteo_id)

    # Filtrar residentes según tipo de sorteo
    if sorteo.tipo_residente_propietario is True:
        residentes = DetalleResidente.objects.filter(propietario=True)
        parqueaderos = Parqueadero.objects.filter(comunal=True, estado=False)
    elif sorteo.tipo_residente_propietario is False:
        residentes = DetalleResidente.objects.filter(propietario=False)
        parqueaderos = Parqueadero.objects.filter(comunal=False, estado=False)
    else:
        residentes = DetalleResidente.objects.all()
        parqueaderos = Parqueadero.objects.filter(estado=False)

    # 🔹 Filtrar usuarios con vehículos válidos
    usuarios_con_vehiculo = VehiculoResidente.objects.filter(documentos=True).values_list('cod_usuario', flat=True)
    residentes = residentes.filter(cod_usuario__in=usuarios_con_vehiculo)

    # 🔹 Crear lista de tuplas (residente, vehículo)
    residentes_con_vehiculo = [
        (residente, VehiculoResidente.objects.filter(cod_usuario=residente.cod_usuario, documentos=True).first())
        for residente in residentes
    ]

    # 🔹 Realizar sorteo (solo si no está realizado)
    if request.method == 'POST' and 'realizar_sorteo' in request.POST:
        if sorteo.estado:
            messages.warning(request, " Este sorteo ya fue realizado. No se puede volver a ejecutar.")
        elif not residentes.exists():
            messages.error(request, "No hay residentes con vehículo válido para participar en el sorteo.")
        elif not parqueaderos.exists():
            messages.error(request, "No hay parqueaderos disponibles para el sorteo.")
        else:
            ganador_residente = random.choice(list(residentes))
            parqueadero = random.choice(list(parqueaderos))

            if GanadorSorteo.objects.filter(id_sorteo=sorteo, id_detalle_residente=ganador_residente).exists():
                messages.warning(request, f"El residente {ganador_residente.cod_usuario.nombres} ya ganó en este sorteo.")
            else:
                ganador = GanadorSorteo.objects.create(
                    id_sorteo=sorteo,
                    id_detalle_residente=ganador_residente,
                    id_parqueadero=parqueadero
                )
                parqueadero.estado = True
                parqueadero.save()

                # 🔹 Actualizar el estado del sorteo a True
                sorteo.estado = True
                sorteo.save()

                vehiculo = VehiculoResidente.objects.filter(
                    cod_usuario=ganador_residente.cod_usuario, documentos=True
                ).first()

                # Enviar correo al ganador
                if ganador_residente.cod_usuario.correo:
                    try:
                        send_mail(
                            subject="Ganador de sorteo - Altos de Fontibón",
                            message=(
                                f"Estimado(a) {ganador_residente.cod_usuario.nombres} {ganador_residente.cod_usuario.apellidos},\n\n"
                                f"¡Felicitaciones! Has resultado ganador en el sorteo de parqueaderos.\n"
                                f"Parqueadero asignado: {parqueadero.numero_parqueadero}\n"
                                f"Vehículo: {vehiculo.placa if vehiculo else 'No registrado'}\n\n"
                                "Atentamente,\nAdministración Altos de Fontibón"
                            ),
                            from_email="altosdefontibon.cr@gmail.com",
                            recipient_list=[ganador_residente.cod_usuario.correo],
                            fail_silently=False,
                        )
                    except Exception as e:
                        print(f"Error enviando correo: {e}")

                # 📩 Enviar correo a los que no ganaron
                perdedores = residentes.exclude(id_detalle_residente=ganador_residente.id_detalle_residente)
                for perdedor in perdedores:
                    correo_perdedor = perdedor.cod_usuario.correo
                    if correo_perdedor:
                        try:
                            send_mail(
                                subject="Sorteo de parqueaderos - Altos de Fontibón",
                                message=(
                                    f"Estimado(a) {perdedor.cod_usuario.nombres} {perdedor.cod_usuario.apellidos},\n\n"
                                    "Gracias por participar en el sorteo de parqueaderos.\n"
                                    "Lamentablemente en esta ocasión no fuiste ganador.\n\n"
                                    "Te invitamos a participar en futuros sorteos.\n\n"
                                    "Atentamente,\nAdministración Altos de Fontibón"
                                ),
                                from_email="altosdefontibon.cr@gmail.com",
                                recipient_list=[correo_perdedor],
                                fail_silently=True,
                            )
                        except Exception as e:
                            print(f"Error enviando correo a perdedor: {e}")

                messages.success(request, " ¡Sorteo realizado! Los participantes han sido notificados por correo.")
                return redirect('sorteo_vehiculos', sorteo_id=sorteo.id_sorteo)

    # =======================
    # 🔹 Mostrar ganadores y perdedores si el sorteo ya se realizó
    # =======================
    ganadores_con_vehiculo, perdedores_con_vehiculo = [], []

    if sorteo.estado:
        ganadores_qs = GanadorSorteo.objects.filter(id_sorteo=sorteo).select_related('id_detalle_residente', 'id_parqueadero')
        ganadores_con_vehiculo = [
            (g, VehiculoResidente.objects.filter(cod_usuario=g.id_detalle_residente.cod_usuario, documentos=True).first())
            for g in ganadores_qs
        ]

        ganadores_ids = ganadores_qs.values_list('id_detalle_residente', flat=True)
        perdedores = residentes.exclude(id_detalle_residente__in=ganadores_ids)
        perdedores_con_vehiculo = [
            (p, VehiculoResidente.objects.filter(cod_usuario=p.cod_usuario, documentos=True).first())
            for p in perdedores
        ]

    context = {
        'sorteo': sorteo,
        'residentes_con_vehiculo': residentes_con_vehiculo,  # siempre disponible
        'parqueaderos': parqueaderos,
        'ganadores_con_vehiculo': ganadores_con_vehiculo,
        'perdedores_con_vehiculo': perdedores_con_vehiculo,
    }
    return render(request, 'administrador/sorteo/sorteo_vehiculos.html', context)



@rol_requerido([3])
@login_requerido
def listar_novedades(request):
    filtro = request.GET.get("filtro", "todos")  # Valor por defecto "todos"
    
    # Filtrar según tipo
    if filtro == "visitante":
        novedades = Novedades.objects.filter(id_visitante__isnull=False).order_by("-fecha")
    elif filtro == "paquete":
        novedades = Novedades.objects.filter(id_paquete__isnull=False).order_by("-fecha")
    else:
        novedades = Novedades.objects.all().order_by("-fecha")

    context = {
        "novedades": novedades,
        "filtro_actual": filtro,
    }
    return render(request, "administrador/novedades/listar_novedades.html", context)



@rol_requerido([3])
@login_requerido
def menu_reporte_sorteo(request, sorteo_id):
    """
    Muestra un menú con botones para generar PDF de Ganadores, Perdedores o Participantes.
    """
    sorteo = get_object_or_404(Sorteo, id_sorteo=sorteo_id)
    context = {
        "sorteo": sorteo
    }
    return render(request, "administrador/sorteo/menu_reporte_sorteo.html", context)


@rol_requerido([3])
@login_requerido
def reporte_sorteo_pdf(request, sorteo_id):
    filtro = request.GET.get("filtro", "ganadores")  # ganadores, perdedores, participantes
    sorteo = get_object_or_404(Sorteo, id_sorteo=sorteo_id)

    # 🔹 Filtrar residentes según tipo de sorteo
    if sorteo.tipo_residente_propietario is True:
        residentes = DetalleResidente.objects.filter(propietario=True)
        parqueaderos = Parqueadero.objects.filter(comunal=True, estado=False)
    elif sorteo.tipo_residente_propietario is False:
        residentes = DetalleResidente.objects.filter(propietario=False)
        parqueaderos = Parqueadero.objects.filter(comunal=False, estado=False)
    else:
        residentes = DetalleResidente.objects.all()
        parqueaderos = Parqueadero.objects.filter(estado=False)

    usuarios_con_vehiculo = VehiculoResidente.objects.filter(documentos=True).values_list('cod_usuario', flat=True)
    residentes = residentes.filter(cod_usuario__in=usuarios_con_vehiculo)

    # Obtener ganadores
    ganadores_qs = GanadorSorteo.objects.filter(id_sorteo=sorteo).select_related('id_detalle_residente', 'id_parqueadero')
    ganadores_ids = ganadores_qs.values_list('id_detalle_residente', flat=True)

    # Dependiendo del filtro
    if filtro == "ganadores":
        queryset = ganadores_qs
        mostrar_vehiculo = True
        titulo = f"Ganadores del sorteo {sorteo}"
    elif filtro == "perdedores":
        perdedores = residentes.exclude(id_detalle_residente__in=ganadores_ids)  # 🔹 CORRECCIÓN
        queryset = [
            (p, VehiculoResidente.objects.filter(cod_usuario=p.cod_usuario, documentos=True).first())
            for p in perdedores
        ]
        mostrar_vehiculo = True
        titulo = f"Perdedores del sorteo {sorteo}"
    else:  # participantes
        queryset = [
            (r, VehiculoResidente.objects.filter(cod_usuario=r.cod_usuario, documentos=True).first())
            for r in residentes
        ]
        mostrar_vehiculo = True
        titulo = f"Participantes del sorteo {sorteo}"

    # ======= Crear PDF ========
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="reporte_sorteo.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        leftMargin=50, rightMargin=50,
        topMargin=70, bottomMargin=70
    )
    elementos = []

    # ======= Colores y estilos ========
    COLOR_PRIMARIO = colors.HexColor('#065F46')
    COLOR_SECUNDARIO = colors.HexColor('#059669')
    COLOR_FONDO_CLARO = colors.HexColor('#F0FDF4')

    styles = getSampleStyleSheet()
    estilo_titulo_principal = ParagraphStyle(
        'TituloPrincipal', parent=styles['Heading1'],
        fontSize=18, spaceAfter=25, spaceBefore=10,
        alignment=TA_CENTER, textColor=colors.black,
        fontName='Helvetica-Bold', letterSpacing=1
    )
    estilo_subtitulo = ParagraphStyle(
        'Subtitulo', parent=styles['Normal'],
        fontSize=12, alignment=TA_CENTER,
        textColor=colors.black, fontName='Helvetica',
        spaceAfter=20
    )
    estilo_encabezado_tabla = ParagraphStyle(
        'EncabezadoTabla', parent=styles['Normal'],
        fontSize=11, textColor=colors.white,
        alignment=TA_CENTER, fontName='Helvetica-Bold',
        leading=14
    )
    estilo_celda_tabla = ParagraphStyle(
        'CeldaTabla', parent=styles['Normal'],
        fontSize=10, alignment=TA_CENTER,
        textColor=colors.black, fontName='Helvetica',
        leading=12
    )
    estilo_info_fecha = ParagraphStyle(
        'InfoFecha', parent=styles['Normal'],
        fontSize=9, textColor=colors.black,
        fontName='Helvetica', alignment=TA_RIGHT
    )

    # ======= Logo e info del encabezado ========
    logo_path = "static/img/Logo Fontibon.png"
    try:
        logo = Image(logo_path, width=140, height=60)
        logo.hAlign = 'LEFT'
    except:
        logo = None

    fecha_reporte = datetime.now().strftime("%d/%m/%Y")
    hora_reporte = datetime.now().strftime("%H:%M")
    info_fecha = Paragraph(
        f"<b>Generado:</b><br/>{fecha_reporte}<br/>{hora_reporte}", 
        estilo_info_fecha
    )
    titulo_principal = Paragraph("REPORTE DE SORTEOS", estilo_titulo_principal)
    subtitulo = Paragraph("Sistema de Reservas", estilo_subtitulo)

    if logo:
        header_data = [[logo, [titulo_principal, subtitulo], info_fecha]]
    else:
        header_data = [["", [titulo_principal, subtitulo], info_fecha]]

    header_table = Table(header_data, colWidths=[120, 300, 130])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    elementos.append(header_table)

    # ======= Línea decorativa ========
    line_table = Table([['']], colWidths=[500])
    line_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 3, COLOR_SECUNDARIO),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elementos.append(line_table)
    elementos.append(Spacer(1, 25))

    # ======= Título específico del reporte ========
    elementos.append(Paragraph(titulo, estilo_titulo_principal))
    elementos.append(Spacer(1, 20))

    # ======= Tabla de datos ========
    encabezados = ["Residente", "Placa", "Torre", "Apto", "Parq", "Sorteo", "Fecha Ganado"]
    data = [[Paragraph(encab, estilo_encabezado_tabla) for encab in encabezados]]

    total = 0
    if filtro == "ganadores":
        for g in queryset:
            vehiculo = VehiculoResidente.objects.filter(cod_usuario=g.id_detalle_residente.cod_usuario).first()
            placa_texto = vehiculo.placa if vehiculo else "N/A"
            data.append([
                Paragraph(f"{g.id_detalle_residente.cod_usuario.nombres} {g.id_detalle_residente.cod_usuario.apellidos}", estilo_celda_tabla),
                Paragraph(placa_texto, estilo_celda_tabla),
                Paragraph(str(g.id_detalle_residente.torre), estilo_celda_tabla),
                Paragraph(str(g.id_detalle_residente.apartamento), estilo_celda_tabla),
                Paragraph(g.id_parqueadero.numero_parqueadero if g.id_parqueadero else "N/A", estilo_celda_tabla),
                Paragraph(f"Sorteo #{g.id_sorteo.id_sorteo}", estilo_celda_tabla),
                Paragraph(g.fecha_ganado.strftime("%d/%m/%Y %H:%M"), estilo_celda_tabla)
            ])
            total += 1
    else:
        for r, vehiculo in queryset:
            placa_texto = vehiculo.placa if vehiculo else "N/A"
            data.append([
                Paragraph(f"{r.cod_usuario.nombres} {r.cod_usuario.apellidos}", estilo_celda_tabla),
                Paragraph(placa_texto, estilo_celda_tabla),
                Paragraph(str(r.torre), estilo_celda_tabla),
                Paragraph(str(r.apartamento), estilo_celda_tabla),
                Paragraph("-", estilo_celda_tabla),
                Paragraph("-", estilo_celda_tabla),
                Paragraph("-", estilo_celda_tabla)
            ])
            total += 1

    col_widths = [130, 70, 50, 50, 80, 80, 100]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARIO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 15),
        ("TOPPADDING", (0, 0), (-1, 0), 15),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("TOPPADDING", (0, 1), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor('#D1FAE5')),
        ("LINEABOVE", (0, 0), (-1, 0), 2, COLOR_PRIMARIO),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_FONDO_CLARO]),
    ]))
    elementos.append(table)
    elementos.append(Spacer(1, 25))

    # ======= Resumen ========
    resumen_data = [
        [" RESUMEN DEL REPORTE", ""],
        [f"Total de registros:", f"{total}"]
    ]
    resumen_table = Table(resumen_data, colWidths=[200, 100])
    resumen_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_SECUNDARIO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("SPAN", (0, 0), (-1, 0)),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("ALIGN", (0, 1), (0, -1), "LEFT"),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
        ("LEFTPADDING", (0, 1), (-1, -1), 12),
        ("RIGHTPADDING", (0, 1), (-1, -1), 12),
        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor('#D1FAE5')),
        ("LINEABOVE", (0, 0), (-1, 0), 2, COLOR_SECUNDARIO),
    ]))
    elementos.append(resumen_table)
    elementos.append(Spacer(1, 30))

    # ======= Pie de página ========
    footer_style = ParagraphStyle(
        'Footer', fontSize=8, textColor=colors.black,
        alignment=TA_CENTER, fontName='Helvetica'
    )
    footer_text = f"Sistema de Reservas • Reporte generado el {fecha_reporte} a las {hora_reporte} • Página 1 de 1"
    elementos.append(Paragraph(footer_text, footer_style))

    doc.build(elementos)
    return response


@rol_requerido([3])
@login_requerido
def filtro_reservas(request):
    return render(request, 'administrador/reservas/filtro_reservas.html')



@rol_requerido([3])
@login_requerido
def reporte_reservas_pdf(request):
    # ======= Inicializar queryset ========
    reservas = Reserva.objects.all().select_related('cod_usuario', 'cod_zona')

    # ======= Obtener filtros desde parámetros GET ========
    fecha = request.GET.get("fecha")  # YYYY-MM-DD
    mes = request.GET.get("mes")
    anio = request.GET.get("anio")
    estado = request.GET.get("estado")

    # ======= Aplicar filtros ========
    if fecha:
        fecha_obj = parse_date(fecha)
        if fecha_obj:
            reservas = reservas.filter(fecha_uso=fecha_obj)
    if mes and anio:
        reservas = reservas.filter(fecha_uso__month=mes, fecha_uso__year=anio)
    elif mes:
        reservas = reservas.filter(fecha_uso__month=mes)
    elif anio:
        reservas = reservas.filter(fecha_uso__year=anio)

    if estado:
        reservas = reservas.filter(estado=estado)

    # ======= Respuesta PDF ========
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="reporte_reservas.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        leftMargin=50, rightMargin=50,
        topMargin=70, bottomMargin=70
    )
    elementos = []

    # ======= Colores y estilos ========
    COLOR_PRIMARIO = colors.HexColor('#065F46')
    COLOR_SECUNDARIO = colors.HexColor('#059669')
    COLOR_FONDO_CLARO = colors.HexColor('#F0FDF4')

    styles = getSampleStyleSheet()
    estilo_titulo_principal = ParagraphStyle(
        'TituloPrincipal', parent=styles['Heading1'],
        fontSize=18, spaceAfter=25, spaceBefore=10,
        alignment=TA_CENTER, textColor=colors.black,
        fontName='Helvetica-Bold', letterSpacing=1
    )
    estilo_subtitulo = ParagraphStyle(
        'Subtitulo', parent=styles['Normal'],
        fontSize=12, alignment=TA_CENTER,
        textColor=colors.black, fontName='Helvetica',
        spaceAfter=20
    )
    estilo_encabezado_tabla = ParagraphStyle(
        'EncabezadoTabla', parent=styles['Normal'],
        fontSize=11, textColor=colors.white,
        alignment=TA_CENTER, fontName='Helvetica-Bold',
        leading=14
    )
    estilo_celda_tabla = ParagraphStyle(
        'CeldaTabla', parent=styles['Normal'],
        fontSize=10, alignment=TA_CENTER,
        textColor=colors.black, fontName='Helvetica',
        leading=12
    )
    estilo_info_fecha = ParagraphStyle(
        'InfoFecha', parent=styles['Normal'],
        fontSize=9, textColor=colors.black,
        fontName='Helvetica', alignment=TA_RIGHT
    )

    # ======= Logo e info del encabezado ========
    logo_path = "static/img/Logo Fontibon.png"
    try:
        logo = Image(logo_path, width=140, height=60)
        logo.hAlign = 'LEFT'
    except:
        logo = None

    fecha_reporte = datetime.now().strftime("%d/%m/%Y")
    hora_reporte = datetime.now().strftime("%H:%M")
    info_fecha = Paragraph(
        f"<b>Generado:</b><br/>{fecha_reporte}<br/>{hora_reporte}", 
        estilo_info_fecha
    )
    titulo_principal = Paragraph("REPORTE DE RESERVAS", estilo_titulo_principal)
    subtitulo = Paragraph("Sistema de Reservas", estilo_subtitulo)

    if logo:
        header_data = [[logo, [titulo_principal, subtitulo], info_fecha]]
    else:
        header_data = [["", [titulo_principal, subtitulo], info_fecha]]

    header_table = Table(header_data, colWidths=[120, 300, 130])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    elementos.append(header_table)

    # ======= Línea decorativa ========
    line_table = Table([['']], colWidths=[500])
    line_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 3, COLOR_SECUNDARIO),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elementos.append(line_table)
    elementos.append(Spacer(1, 25))

    # ======= Tabla de reservas ========
    encabezados = ["Usuario", "Zona", "Fecha Uso", "Hora Inicio", "Hora Fin", "Estado", "Valor Pago"]
    data = [[Paragraph(encab, estilo_encabezado_tabla) for encab in encabezados]]

    total_reservas = 0
    total_valor_pago = 0
    for r in reservas:
        data.append([
            Paragraph(r.cod_usuario.nombres, estilo_celda_tabla),
            Paragraph(r.cod_zona.nombre_zona, estilo_celda_tabla),
            Paragraph(r.fecha_uso.strftime('%Y-%m-%d'), estilo_celda_tabla),
            Paragraph(r.hora_inicio.strftime('%H:%M'), estilo_celda_tabla),
            Paragraph(r.hora_fin.strftime('%H:%M'), estilo_celda_tabla),
            Paragraph(r.estado, estilo_celda_tabla),
            Paragraph(f"${r.valor_pago:.2f}" if r.valor_pago else "-", estilo_celda_tabla)
        ])
        total_reservas += 1
        if r.valor_pago:
            total_valor_pago += r.valor_pago

    table = Table(data, colWidths=[60, 80, 90, 80, 70, 70, 70], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARIO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 15),
        ("TOPPADDING", (0, 0), (-1, 0), 15),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("TOPPADDING", (0, 1), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor('#D1FAE5')),
        ("LINEABOVE", (0, 0), (-1, 0), 2, COLOR_PRIMARIO),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_FONDO_CLARO]),
    ]))
    elementos.append(table)
    elementos.append(Spacer(1, 25))

    # ======= Resumen ========
    resumen_data = [
        [" RESUMEN DEL REPORTE", ""],
        [f"Total de reservas:", f"{total_reservas}"],
        [f"Valor total recaudado:", f"${total_valor_pago:.2f}"]
    ]
    resumen_table = Table(resumen_data, colWidths=[200, 100])
    resumen_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_SECUNDARIO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("SPAN", (0, 0), (-1, 0)),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("ALIGN", (0, 1), (0, -1), "LEFT"),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
        ("LEFTPADDING", (0, 1), (-1, -1), 12),
        ("RIGHTPADDING", (0, 1), (-1, -1), 12),
        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor('#D1FAE5')),
        ("LINEABOVE", (0, 0), (-1, 0), 2, COLOR_SECUNDARIO),
    ]))
    elementos.append(resumen_table)
    elementos.append(Spacer(1, 30))

    # ======= Pie de página ========
    footer_style = ParagraphStyle(
        'Footer', fontSize=8, textColor=colors.black,
        alignment=TA_CENTER, fontName='Helvetica'
    )
    footer_text = f"Sistema de Reservas • Reporte generado el {fecha_reporte} a las {hora_reporte} • Página 1 de 1"
    elementos.append(Paragraph(footer_text, footer_style))

    # ======= Construir PDF ========
    doc.build(elementos)
    return response
