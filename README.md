🛒 PROYECTO A BAZAR - GUÍA DE INSTALACIÓN
=========================================

Este proyecto es una aplicación web desarrollada en Django con base de datos MySQL.

📋 REQUISITOS PREVIOS
---------------------
* Python (3.10 o superior)
* MySQL Server (XAMPP, Workbench o servicio local)
* Visual Studio Code

------------------------------------------------------------------

🚀 PASOS PARA INSTALAR Y CORRER EL PROYECTO
-------------------------------------------

PASO 1: CLONAR EL REPOSITORIO
Abre una terminal o usa VS Code para descargar el código.

   git clone [Proyecto Bazar](https://github.com/ceal2013/PROYECTO_INTEGRACION.git)


PASO 2: CREAR EL ENTORNO VIRTUAL
Para aislar las librerías, ejecuta en la terminal:

   En Windows:    python -m venv venv
   En Mac/Linux:  python3 -m venv venv

(Nota: Si VS Code te pregunta si quieres usar el entorno nuevo, elige "Yes").


PASO 3: INSTALAR DEPENDENCIAS
Con el entorno activado (debe decir 'venv' al inicio de la línea de comandos), instala todo lo necesario:

   pip install -r requirements.txt


PASO 4: CONFIGURAR VARIABLES PRIVADAS (.env) 🔐
El archivo con las contraseñas no se descarga por seguridad.
Debes crear un archivo nuevo llamado ".env" (punto env) en la carpeta principal y pegar esto dentro:

   SECRET_KEY=django-insecure--g640qaq388=kpro4g96kj=ug7kfp@!+xwjb+lh(*qcj8^ddo%
   DEBUG=True

   # Configuración de Base de Datos
   DB_NAME=bazar
   DB_USER=root
   DB_PASSWORD=
   DB_HOST=localhost
   DB_PORT=3306

(⚠️ OJO: Si tu MySQL tiene contraseña, escríbela en DB_PASSWORD sin dejar espacios).


PASO 5: PREPARAR LA BASE DE DATOS 🗄️
1. Abre tu programa de MySQL (Workbench, phpMyAdmin).
2. Crea una base de datos vacía llamada: bazar


PASO 6: EJECUTAR MIGRACIONES Y SERVIDOR
Regresa a la terminal de VS Code y ejecuta estos dos comandos:

   python manage.py migrate
   python manage.py runserver

✅ ¡Listo! Entra a http://127.0.0.1:8000/ para ver tu proyecto funcionando.