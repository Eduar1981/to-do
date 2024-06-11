from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from forms import RegistrationForm, LoginForm, TaskForm
from config import Config
from flask_dance.contrib.google import make_google_blueprint, google
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.config.from_object(Config)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    refresh_token_params=None,
    endpoint_url='https://www.googleapis.com/oauth2/v1/userinfo',
    client_kwargs={'scope': 'openid profile email'},
)

google_bp = make_google_blueprint(client_id=app.config['GOOGLE_CLIENT_ID'])
app.register_blueprint(google_bp, url_prefix='/login')

mysql = MySQL(app)
mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')


""" @app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (form.username.data, form.email.data, form.password.data))
        mysql.connection.commit()
        cursor.close()

        msg = Message('Confirmación de Registro', sender='hernangrisalez97@gmail.com', recipients=[form.email.data])
        msg.body = 'Gracias por registrarte en nuestra aplicación To Do.'
        mail.send(msg)

        flash('Te has registrado con éxito. Revisa tu correo para confirmar el registro.', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form) """

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Verificar si el usuario ya está registrado
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (form.email.data,))
        existing_user = cursor.fetchone()
        cursor.close()

        if existing_user:
            flash('Ya existe un usuario con esta dirección de correo electrónico. Por favor, utiliza otra.', 'error')
            return redirect(url_for('register'))  # Redireccionar de nuevo al formulario de registro

        # Si el usuario no está registrado, proceder con el registro
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (form.username.data, form.email.data, form.password.data))
        mysql.connection.commit()
        cursor.close()

        msg = Message('Confirmación de Registro', sender='hernangrisalez97@gmail.com', recipients=[form.email.data])
        msg.body = 'Gracias por registrarte en nuestra aplicación To Do.'
        mail.send(msg)

        flash('Te has registrado con éxito. Revisa tu correo para confirmar el registro.', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (form.email.data, form.password.data))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['user_id'] = user[0]
            flash('Inicio de sesión éxitoso', 'succes')
            return redirect(url_for('dashboard'))
        else:
            flash('Inicio de sesión fallido. Varifica tus credenciales', 'danger')
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    form = TaskForm()
    if form.validate_on_submit():
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO tasks (user_id, task, completed) VALUES (%s, %s, %s)', (session['user_id'], form.task.data, False))
        mysql.connection.commit()
        cursor.close()
        flash('Tarea agregada con éxito', 'success')
        return redirect(url_for('dashboard'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tasks WHERE user_id = %s', [session['user_id']])
    tasks = cursor.fetchall()
    cursor.close()

    return render_template('dashboard.html', form=form, tasks=tasks)

@app.route('/complete_task/<int:task_id>')
def complete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE tasks SET completed = %s WHERE id = %s AND user_id = %s', (True, task_id, session['user_id']))
    mysql.connection.commit()
    cursor.close()
    flash('Tarea marcada como completada', 'success')
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Has cerrado sesión', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
    