from functools import wraps
from django.shortcuts import redirect
from .models import Usuario  
from django.contrib import messages



def login_requerido(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        usuario_id = request.session.get('usuario_id')

        if not usuario_id:
            return redirect('login')

        try:
            usuario = Usuario.objects.get(id_usuario=usuario_id)
            request.usuario = usuario
        except Usuario.DoesNotExist:
            request.session.flush()
            return redirect('login')

        return view_func(request, *args, **kwargs)
    return _wrapped_view



def rol_requerido(roles_permitidos):
    def decorator(view_func):
        @login_requerido
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            usuario = getattr(request, 'usuario', None)
            if not usuario:
                return redirect('login')

            rol_id = usuario.id_rol.id_rol

            if rol_id not in roles_permitidos:
                messages.error(request, "No tienes permisos para acceder.")
                if rol_id == 1:
                    return redirect('index')
                elif rol_id == 2:
                    return redirect('detalle_residente')
                elif rol_id == 3:
                    return redirect('panel_administrador')
                elif rol_id == 4:
                    return redirect('panel_vigilante')
                else:
                    return redirect('login')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator