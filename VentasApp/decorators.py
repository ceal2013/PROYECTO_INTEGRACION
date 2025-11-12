from django.shortcuts import redirect
from functools import wraps


def custom_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(allowed_roles=None):
    """Decorator que verifica que el rol del usuario esté en allowed_roles.

    Se evita usar una lista mutable como valor por defecto.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            roles = allowed_roles or []
            rol = request.session.get('rol')
            if rol not in roles:
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
