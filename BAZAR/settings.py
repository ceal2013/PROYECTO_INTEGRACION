"""
Django settings for Bazar "El Sol" project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

# SECURITY WARNING: keep the secret key used in production secret!
# Usa una variable de entorno o usa la clave por defecto para desarrollo
SECRET_KEY = os.getenv('SECRET_KEY', 'clave-segura-para-demo-aws-windows')

# SECURITY WARNING: don't run with debug turned on in production!
# Lo dejamos en True para que veas errores si fallan las pruebas, 
# pero idealmente en AWS productivo debería ser False.
DEBUG = True

# Permitimos cualquier host (necesario para Windows Server y AWS)
ALLOWED_HOSTS = ['*']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'VENTASAPP',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'BAZAR.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'BAZAR.wsgi.application'


# Database
# ---------------------------------------------------
# Lógica Inteligente:
# 1. Si detecta variables de AWS (DB_HOST), usa esa configuración.
# 2. Si NO las detecta (estás en Local o Windows Server), usa XAMPP por defecto.

if os.getenv('DB_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': '3306',
        }
    }
else:
    # CONFIGURACIÓN POR DEFECTO (XAMPP / LOCAL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'bazar',       # Nombre de tu BD en XAMPP
            'USER': 'root',        # Usuario por defecto XAMPP
            'PASSWORD': '',        # Sin contraseña por defecto
            'HOST': 'localhost',
            'PORT': '3306',
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'VENTASAPP.Usuario'

# Internationalization
LANGUAGE_CODE = 'es-ES'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
#STATIC_URL = 'static/'
STATIC_URL = '/static/'  # <--- Con la barra al inicio
STATICFILES_DIRS = [STATIC_DIR]

# Carpeta donde se guardarán los estáticos al usar "collectstatic" (Requerido para producción)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Habilita la compresión y el cacheo eficiente de WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'