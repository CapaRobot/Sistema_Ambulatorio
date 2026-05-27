from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__, 
            template_folder='..', 
            static_folder='..', 
            static_url_path='')
app.secret_key = 'mi_clave_secreta_biolab' # Activo para los mensajes Flash

DATABASE = os.path.join(os.path.dirname(__file__), "data", "Biolab_Usuarios.db")

def conexion_bbdd():
    """Establece conexión con SQLite y crea la tabla con los nuevos campos."""
    conexion = sqlite3.connect(DATABASE)
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ANALISTAS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            EMAIL VARCHAR(100) UNIQUE,
            NOMBRE VARCHAR(100),
            APELLIDO VARCHAR(100),
            NOMBRE_USUARIO VARCHAR(50),
            PASSWORD VARCHAR(50),
            PREGUNTA_SEGURIDAD VARCHAR(2),
            RESPUESTA_SEGURIDAD VARCHAR(100)
        )
    ''')
    conexion.commit()
    return conexion

# Inicializar la base de datos al arrancar el servidor
conexion_bbdd().close()


# ==========================================================
#   CONTROL DE RUTAS DE NAVEGACIÓN (VISTAS)
# ==========================================================

# MODIFICADO: Ahora la raíz '/' carga obligatoriamente el LOGIN
@app.route('/')
@app.route('/login')
def vista_login():
    """Muestra la interfaz física del login usando el archivo login.html."""
    return render_template('login.html')


@app.route('/registro')
def vista_registro():
    """Muestra la interfaz de registro de analistas."""
    return render_template('auth-register.html')


@app.route('/index')
def index():
    """Muestra el panel de control principal de BIO-LAB (Solo post-login)."""
    return render_template('index.html')


# ==========================================================
#   PROCESAMIENTO DE FORMULARIOS (LÓGICA)
# ==========================================================

@app.route('/registrar', methods=['POST'])
def registrar_usuario():
    if request.method == 'POST':
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        pregunta = request.form['pregunta_seguridad']
        respuesta = request.form['respuesta_seguridad']

        if password != confirm_password:
            flash("¡Error: Las contraseñas no coinciden!", "danger")
            return redirect(url_for('vista_registro'))

        try:
            conexion = sqlite3.connect(DATABASE)
            cursor = conexion.cursor()
            
            query = '''
                INSERT INTO ANALISTAS (EMAIL, NOMBRE, APELLIDO, NOMBRE_USUARIO, PASSWORD, PREGUNTA_SEGURIDAD, RESPUESTA_SEGURIDAD)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            datos = (email, firstname, lastname, username, password, pregunta, respuesta)
            
            cursor.execute(query, datos)
            conexion.commit()
            
            flash(f"¡Éxito: El analista {firstname} {lastname} ha sido registrado correctamente!", "success")
            
        except sqlite3.IntegrityError:
            flash("¡Error: El correo electrónico ya está registrado!", "danger")
        except Exception as e:
            flash(f"Error inesperado: {e}", "danger")
        finally:
            conexion.close()

        return redirect(url_for('vista_registro'))


@app.route('/procesar_login', methods=['POST'])
def login_usuario():
    """Recibe los datos del login.html y los valida contra la BBDD."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conexion = sqlite3.connect(DATABASE)
            cursor = conexion.cursor()
            
            query = "SELECT NOMBRE, APELLIDO, PASSWORD FROM ANALISTAS WHERE NOMBRE_USUARIO = ?"
            cursor.execute(query, (username,))
            usuario = cursor.fetchone()
            
        except Exception as e:
            flash(f"Error de base de datos: {e}", "danger")
            return redirect(url_for('vista_login'))
        finally:
            conexion.close()

        if usuario:
            db_password = usuario[2]
            nombre_real = usuario[0]
            apellido_real = usuario[1]
            
            if password == db_password:
                flash(f"¡Bienvenido de nuevo, {nombre_real} {apellido_real}!", "success")
                return redirect(url_for('index')) 
            else:
                flash("¡Error: Contraseña incorrecta. Inténtelo de nuevo!", "danger")
                return redirect(url_for('vista_login'))
        else:
            flash("¡Error: El nombre de usuario no se encuentra registrado!", "danger")
            return redirect(url_for('vista_login'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)