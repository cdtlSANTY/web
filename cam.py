import cv2
from flask import Flask, render_template, Response, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'clave' # Cambia esto por algo aleatorio

# --- CONFIGURACIÓN DE CÁMARA EZVIZ ---
CAM_USER = "admin"
CAM_PASS = "FYUKPQ"  # Tu Verification Code de la etiqueta
CAM_IP = "192.168.1.100"
RTSP_URL = f"rtsp://{CAM_USER}:{CAM_PASS}@{CAM_IP}:554/H.264"

# --- SISTEMA DE USUARIOS Y PERMISOS ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Base de datos simulada: {usuario: {"password": "...", "puede_ver": True/False}}
USERS_DB = {
    "santi": {"password": "1234", "puede_ver": True},
    "pedro": {"password": "456", "puede_ver": False},
    "maria": {"password": "789", "puede_ver": True},
    "pedro": {"password": "456", "puede_ver": False},
    "pedro": {"password": "456", "puede_ver": False},
    "pedro": {"password": "456", "puede_ver": False},
    "pedro": {"password": "456", "puede_ver": False},
    "pedro": {"password": "456", "puede_ver": False},
    "pedro": {"password": "456", "puede_ver": False},
    "pedro": {"password": "456", "puede_ver": False},
    "pedro": {"password": "456", "puede_ver": False},
    "mr": {"password": "456", "puede_ver": True},
}



class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.puede_ver = USERS_DB[id]["puede_ver"]

@login_manager.user_loader
def load_user(user_id):
    if user_id not in USERS_DB: return None
    return User(user_id)

# --- LÓGICA DE VIDEO ---
def generar_frames():
    camera = cv2.VideoCapture(RTSP_URL)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Reducimos resolución para que el streaming sea fluido en la web
            frame = cv2.resize(frame, (800, 450))
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# --- RUTAS DE LA PÁGINA ---

@app.route('/')
@login_required
def index():
    if not current_user.puede_ver:
        return "<h1>Acceso Denegado</h1><p>No tienes permiso para ver la cámara.</p><a href='/logout'>Salir</a>", 403
    return f"""
    <h1>CRIADERO VIP EZVIZ - En Vivo</h1>
    <p>Usuario: {current_user.id} | <a href='/logout'>Cerrar Sesión</a></p>
    <img src="/video_feed" style="width: 80%; border: 10px solid black;">
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        if user in USERS_DB and USERS_DB[user]['password'] == pw:
            login_user(User(user))
            return redirect(url_for('index'))
        flash('Usuario o contraseña incorrectos')
    return '''
        <form method="post">
            Usuario: <input type="text" name="username"><br>
            Clave: <input type="password" name="password"><br>
            <input type="submit" value="Entrar">
        </form>
    '''



@app.route('/video_feed')
@login_required
def video_feed():
    if not current_user.puede_ver:
        return Response(status=403)
    return Response(generar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)