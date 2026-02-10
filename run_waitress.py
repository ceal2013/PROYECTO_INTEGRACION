from waitress import serve
from BAZAR.wsgi import application

if __name__ == '__main__':
    print("--------------------------------------------------------------")
    print("Servidor Waitress corriendo en http://localhost:8000")
    print("--------------------------------------------------------------")
    serve(application, host='0.0.0.0', port=8000)