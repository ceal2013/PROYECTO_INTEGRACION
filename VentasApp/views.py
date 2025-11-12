from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password

from .forms import LoginForm
from .models import Usuario
from .decorators import custom_login_required


def login_view(request):
	form = LoginForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		username = form.cleaned_data.get('username')
		password = form.cleaned_data.get('password')
		try:
			usuario = Usuario.objects.get(username=username)
		except Usuario.DoesNotExist:
			messages.error(request, 'Usuario no encontrado')
			return render(request, 'login.html', {'form': form})

		if check_password(password, usuario.password):
			# Guardar datos en sesión manualmente
			request.session['usuario_id'] = usuario.id_usuario
			request.session['username'] = usuario.username
			request.session['rol'] = usuario.rol
			return redirect('home')
		else:
			messages.error(request, 'Contraseña incorrecta')

	return render(request, 'login.html', {'form': form})


def user_logout(request):
	request.session.flush()
	return redirect('login')


@custom_login_required
def home(request):
	return render(request, 'home.html')
