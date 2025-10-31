from django.shortcuts import render, redirect,get_object_or_404
from usuario.models import *
from usuario.decorators import *
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
import datetime
from datetime import date, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now


@rol_requerido([2])
@login_requerido
def panel_general_residente(request):
    return render(request, "residente/panel.html")


@login_requerido
@rol_requerido([2])
def noticias(request):
    """
    Vista para mostrar las noticias del panel de residente.
    """
    noticias = Noticias.objects.all().order_by('-fecha_publicacion')  # Más recientes primero

    context = {
        'detalle': True,  # Esto habilita la sección de noticias en tu template
        'noticias': noticias
    }

    return render(request, 'residente/detalles_residente/noticias.html', context)  # Reemplaza 'nombre_template.html' por el nombre real de tu template

@rol_requerido([2])
@login_requerido
def detalle_residente(request):
    usuario = request.usuario
    detalle = DetalleResidente.objects.filter(cod_usuario=usuario).first()

    if detalle:
        return redirect("panel_residente")

    if request.method == "POST":
        form = DetalleResidenteForm(request.POST)
        if form.is_valid():
            detalle = form.save(commit=False)
            detalle.cod_usuario = usuario
            detalle.save()
            messages.success(request, "Detalles de residente registrados correctamente.")
            return redirect("panel_residente")
        else:
            # Mostrar errores del formulario en mensajes
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = DetalleResidenteForm()

    return render(
        request,
        "residente/detalles_residente/registrar_detalle_residente.html",
        {"form": form}
    )
    



@rol_requerido([2])
@login_requerido
def listar_zonas(request):
    zonas = ZonaComun.objects.all()
    return render(request, "residente/zonas_comunes/listar_zonas.html", {"zonas": zonas})


# Crear reserva
@rol_requerido([2])
@login_requerido
def crear_reserva(request, id_zona):
    zona = get_object_or_404(ZonaComun, pk=id_zona)

    if request.method == "POST":
        form = ReservaForm(request.POST)

        if form.is_valid():
            fecha_uso = form.cleaned_data['fecha_uso']
            hora_inicio = form.cleaned_data['hora_inicio']
            hora_fin = form.cleaned_data['hora_fin']

            # 🔹 1. Validación de fecha pasada
            if fecha_uso < datetime.date.today():
                messages.error(request, "No puedes seleccionar una fecha que ya pasó.")
                return render(request, "residente/zonas_comunes/crear_reserva.html", {
                    "form": form,
                    "zona": zona
                })

            # 🔹 2. Validación de fecha ocupada solo para zonas 6, 12 y 13
            if zona.id_zona in [6, 12, 13] and Reserva.objects.filter(cod_zona=zona, fecha_uso=fecha_uso).exists():
                messages.error(request, "Ya existe una reserva para esta fecha en la zona seleccionada.")
            else:
                reserva = form.save(commit=False)
                reserva.cod_usuario = request.usuario
                reserva.cod_zona = zona
                reserva.estado = "En espera"
                reserva.forma_pago = "Efectivo"

                # ----------------------------
                # 🔹 CÁLCULO DEL PAGO
                # ----------------------------
                total_a_pagar = 0

                if hora_inicio and hora_fin:
                    dummy_date = datetime.date(2000, 1, 1)
                    inicio_dt = datetime.datetime.combine(dummy_date, hora_inicio)
                    fin_dt = datetime.datetime.combine(dummy_date, hora_fin)

                    if fin_dt < inicio_dt:
                        fin_dt += datetime.timedelta(days=1)

                    duracion_minutos = (fin_dt - inicio_dt).total_seconds() / 60

                    if zona.tipo_pago == "Por hora":
                        total_a_pagar = (duracion_minutos / 60) * float(zona.tarifa_base)

                    elif zona.tipo_pago == "Franja horaria":
                        franja_minutos = 60
                        if zona.nombre_zona == "Lavandería":
                            franja_minutos = 90
                        total_a_pagar = (duracion_minutos / franja_minutos) * float(zona.tarifa_base)

                    elif zona.tipo_pago == "Evento":
                        total_a_pagar = float(zona.tarifa_base)

                reserva.valor_pago = total_a_pagar
                reserva.save()

                messages.success(request, f"Reserva creada correctamente. Total a pagar: ${total_a_pagar:,.0f}")
                request.session["mostrar_alerta_pago"] = True
                return redirect("mis_reservas")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == "__all__":
                        messages.error(request, error)  # Mostrar solo el texto limpio


    else:
        form = ReservaForm()

    return render(request, "residente/zonas_comunes/crear_reserva.html", {
        "form": form,
        "zona": zona
    })

@rol_requerido([2])
@login_requerido
def fechas_ocupadas(request, id_zona):
    zona = get_object_or_404(ZonaComun, pk=id_zona)

    # Solo marcar "ocupado" si la zona pertenece a los ids 6, 12 o 13
    if zona.id_zona in [6, 12, 13]:
        reservas = Reserva.objects.filter(cod_zona=zona).values_list("fecha_uso", flat=True)
    else:
        reservas = []  # las demás zonas siempre aparecen libres

    return JsonResponse({"fechas": list(reservas)})


@rol_requerido([2])
@login_requerido
def mis_reservas(request):
    # 🔹 Obtener el usuario autenticado desde el decorador
    usuario = request.usuario

    # 🔹 Obtener todas las reservas del usuario y ordenarlas por fecha de creación
    reservas = Reserva.objects.filter(cod_usuario=usuario)\
                              .select_related("cod_zona")\
                              .order_by("-fecha_reserva")

    # 🔹 Revisar si hay que mostrar alerta de pago
    mostrar_alerta = request.session.pop("mostrar_alerta_pago", False)

    # 🔹 Calcular mañana
    manana = date.today() + timedelta(days=1)

    # 🔹 Filtrar reservas que sean para mañana
    reservas_manana = reservas.filter(fecha_uso=manana)

    # 🔹 Enviar correo de recordatorio solo si hay reservas para mañana
    if reservas_manana.exists():
        clave_sesion_correo = f"correo_enviado_{manana.isoformat()}"
        if not request.session.get(clave_sesion_correo, False):
            # Construir cuerpo del correo
            cuerpo = "Hola,\n\nRecuerda que mañana tienes las siguientes reservas:\n\n"
            for r in reservas_manana:
                cuerpo += (
                    f"- Zona: {r.cod_zona.nombre_zona}, "
                    f"Hora: {r.hora_inicio.strftime('%H:%M')} a {r.hora_fin.strftime('%H:%M')}\n"
                )
            cuerpo += "\n¡Gracias por usar nuestro sistema!\n"

            # Enviar correo
            send_mail(
                subject="Recordatorio de reservas para mañana",
                message=cuerpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.correo],
                fail_silently=True,  # ⚠️ Cambiar a False en desarrollo si quieres depurar
            )

            # Marcar en la sesión que ya se envió
            request.session[clave_sesion_correo] = True

    # 🔹 Renderizar plantilla con todas las reservas del usuario
    return render(
        request,
        "residente/zonas_comunes/detalle_reserva.html",
        {
            "reservas": reservas,
            "mostrar_alerta": mostrar_alerta,
        }
    )
  

@rol_requerido([2])
@login_requerido
def eliminar_reserva(request, id_reserva):
    reserva = get_object_or_404(Reserva, pk=id_reserva)

    # Validar permisos: si es residente, solo puede eliminar sus propias reservas
    if request.usuario.id_rol.id_rol == 2 and reserva.cod_usuario != request.usuario:
        messages.error(request, "No puedes eliminar esta reserva.")
        return redirect("mis_reservas")

    # 🚫 No permitir eliminar si ya está actualizada (aprobada o rechazada)
    if reserva.estado != "En espera":
        messages.error(request, f"No puedes eliminar la reserva {id_reserva} porque ya fue {reserva.estado.lower()}.")
        if request.usuario.id_rol.id_rol == 3:
            return redirect("gestionar_reservas")
        return redirect("mis_reservas")

    if request.method == "POST":
        reserva.delete()
        messages.success(request, f"Reserva {id_reserva} eliminada correctamente.")

        if request.usuario.id_rol.id_rol == 3:  # Admin
            return redirect("gestionar_reservas")
        return redirect("mis_reservas")

    # Si alguien intenta entrar por GET
    messages.error(request, "Operación no permitida.")
    if request.usuario.id_rol.id_rol == 3:
        return redirect("gestionar_reservas")
    return redirect("mis_reservas")

    

@rol_requerido([2])
@login_requerido
def detalles(request, vehiculo_id):
    # Obtener el vehículo y sus archivos
    vehiculo = get_object_or_404(VehiculoResidente, pk=vehiculo_id)
    archivos = ArchivoVehiculo.objects.filter(idVehiculo=vehiculo)
    
    # IDs de archivos existentes (para deshabilitar opciones en el select si quieres)
    archivos_ids = [archivo.idTipoArchivo.pk for archivo in archivos]

    if request.method == 'POST':
        tipo_archivo_id = request.POST.get('idTipoArchivo')
        archivo_existente = archivos.filter(idTipoArchivo_id=tipo_archivo_id).first()

        # Usar instancia para actualizar si existe, o crear nuevo
        form = ArchivoVehiculoForm(request.POST, request.FILES, instance=archivo_existente)

        if form.is_valid():
            archivo_obj = form.save(commit=False)
            archivo_obj.idVehiculo = vehiculo

            # Validar fecha de vencimiento
            fecha_venc = form.cleaned_data.get('fechaVencimiento')
            if fecha_venc and fecha_venc < now().date():
                messages.error(request, "La fecha de vencimiento no puede ser anterior a hoy.")
            else:
                archivo_obj.save()
                accion = "actualizado" if archivo_existente else "registrado"
                messages.success(request, f"Archivo '{archivo_obj.idTipoArchivo}' {accion} correctamente.")
                return redirect('detalles', vehiculo_id=vehiculo.id_vehiculo_residente)
    else:
        form = ArchivoVehiculoForm()

    context = {
        'vehiculo': vehiculo,
        'archivos': archivos,
        'form': form,
        'archivos_ids_json': archivos_ids
    }
    return render(request, 'residente/vehiculos/detalles.html', context)
  
  
    
@rol_requerido([2])
@login_requerido
def agregar_pago(request, id_reserva):
    reserva = get_object_or_404(Reserva, pk=id_reserva)
    pago_actual = PagosReserva.objects.filter(id_reserva=reserva).order_by("-id_pago").first()

    form = None
    editar_pago_id = request.GET.get("editar_pago")

    if editar_pago_id:
        pago_editar = get_object_or_404(PagosReserva, pk=editar_pago_id, id_reserva=reserva)
    else:
        pago_editar = None

    # Guardar edición desde el modal
    if request.method == "POST" and "guardar_edicion" in request.POST:
        pago_editar = get_object_or_404(PagosReserva, pk=request.POST.get("pago_id"), id_reserva=reserva)
        form = PagosReservaForm(request.POST, request.FILES, instance=pago_editar)
        if form.is_valid():
            form.save()
            messages.success(request, "El comprobante se actualizó correctamente.")
            return redirect("agregar_pago", id_reserva=reserva.id_reserva)
        else:
            messages.error(request, "Ocurrió un error al actualizar el comprobante.")

    # Crear nuevo pago
    elif request.method == "POST":
        if pago_actual and not pago_actual.estado and not pago_actual.archivo_2:
            form = PagosReservaForm(request.POST, request.FILES, instance=pago_actual)
            if form.is_valid():
                pago = form.save(commit=False)
                pago.estado = False
                pago.save()
                request.session["mostrar_alerta"] = "validando_pago"
                return redirect("agregar_pago", id_reserva=reserva.id_reserva)
        else:
            form = PagosReservaForm(request.POST, request.FILES)
            if form.is_valid():
                pago = form.save(commit=False)
                pago.id_reserva = reserva
                pago.estado = False
                pago.save()
                request.session["mostrar_alerta"] = "primer_pago"
                return redirect("agregar_pago", id_reserva=reserva.id_reserva)

    else:
        if pago_editar:
            form = PagosReservaForm(instance=pago_editar)
        elif pago_actual and not pago_actual.estado and not pago_actual.archivo_2:
            form = PagosReservaForm(instance=pago_actual)
            form.fields["archivo_1"].widget = forms.HiddenInput()
            form.fields["estado"].widget = forms.HiddenInput()
            form.fields["id_reserva"].widget = forms.HiddenInput()
            form.fields["archivo_2"].widget = forms.FileInput(attrs={"class": "form-control"})
        elif pago_actual and not pago_actual.estado and pago_actual.archivo_2:
            form = None
        elif pago_actual and pago_actual.estado:
            form = None
        else:
            form = PagosReservaForm(initial={"id_reserva": reserva.id_reserva})
            form.fields["archivo_2"].widget = forms.HiddenInput()
            form.fields["estado"].widget = forms.HiddenInput()
            form.fields["id_reserva"].widget = forms.HiddenInput()

    # 👇 Solo pagos de la reserva actual
    pagos = PagosReserva.objects.filter(id_reserva=reserva).order_by("-id_pago")

    mostrar_alerta = request.session.pop("mostrar_alerta", None)

    return render(
        request,
        "residente/zonas_comunes/pago_reserva.html",
        {
            "form": form,
            "reserva": reserva,
            "pagos": pagos,
            "pago_actual": pago_actual,
            "pago_editar": pago_editar,
            "mostrar_alerta": mostrar_alerta,
        },
    )


@rol_requerido([2])
@login_requerido
def lista_sorteos(request):
    usuario_logueado = getattr(request, 'usuario', None)

    if not usuario_logueado:
        messages.error(request, "Debes iniciar sesión para ver tus sorteos.")
        return redirect('login')

    # Verificar si el usuario es propietario o arrendatario
    detalle_residente = DetalleResidente.objects.filter(cod_usuario=usuario_logueado).first()

    if not detalle_residente:
        messages.error(request, "No tienes un detalle de residente registrado.")
        return redirect('detalle_residente')

    # 🔹 Filtrar sorteos según el tipo de residente
    if detalle_residente.propietario is True:
        sorteos = Sorteo.objects.filter(tipo_residente_propietario=True).order_by('-fecha_inicio')
    elif detalle_residente.propietario is False:
        sorteos = Sorteo.objects.filter(tipo_residente_propietario=False).order_by('-fecha_inicio')
    else:
        sorteos = Sorteo.objects.all().order_by('-fecha_inicio')

    # 🔹 Verificar participación y si ganó en cada sorteo
    sorteos_info = []
    for sorteo in sorteos:
        participa = VehiculoResidente.objects.filter(
            cod_usuario=usuario_logueado, documentos=True
        ).exists()

        gano = False
        if participa:
            gano = GanadorSorteo.objects.filter(
                id_sorteo=sorteo,
                id_detalle_residente__cod_usuario=usuario_logueado
            ).exists()

        sorteos_info.append({
            "sorteo": sorteo,
            "participa": participa,
            "gano": gano
        })

    context = {
        "sorteos_info": sorteos_info,
        "detalle_residente": detalle_residente
    }
    return render(request, "residente/sorteo/lista_sorteos.html", context)


@rol_requerido([2])
@login_requerido
def detalle_sorteo(request, sorteo_id):
    # Obtener el sorteo
    sorteo = get_object_or_404(Sorteo, id_sorteo=sorteo_id)

    # Usuario logueado desde el decorador
    usuario_logueado = getattr(request, 'usuario', None)

    # Verificar si el usuario tiene vehículo válido
    vehiculo = VehiculoResidente.objects.filter(
        cod_usuario=usuario_logueado,
        documentos=True
    ).first()
    tiene_vehiculo = vehiculo is not None

    # Verificar si el usuario participó en este sorteo
    participo = DetalleResidente.objects.filter(
        cod_usuario=usuario_logueado
    ).exists() and tiene_vehiculo

    gano = False
    parqueadero = None

    if sorteo.estado:  # 🔹 Solo verificar ganador si el sorteo ya se realizó
        ganador = GanadorSorteo.objects.filter(
            id_sorteo=sorteo,
            id_detalle_residente__cod_usuario=usuario_logueado
        ).select_related("id_parqueadero").first()

        gano = ganador is not None
        parqueadero = ganador.id_parqueadero if ganador else None

    # Determinar mensaje según estado y participación
    if not participo:
        mensaje = " No participaste en este sorteo porque no tienes un vehículo válido."
    elif not sorteo.estado:
        mensaje = " Este sorteo aún no se ha realizado."
    elif gano:
        mensaje = " ¡Felicidades! Ganaste en este sorteo."
    else:
        mensaje = " Participaste, pero no ganaste en este sorteo."

    context = {
        "sorteo": sorteo,
        "usuario": usuario_logueado,
        "vehiculo": vehiculo,
        "parqueadero": parqueadero,
        "participo": participo,
        "gano": gano,
        "mensaje": mensaje
    }
    return render(request, "residente/sorteo/detalle_sorteo.html", context)

