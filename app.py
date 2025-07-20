import sqlite3
import functools
from flask import Flask, render_template, request, url_for, redirect, flash, session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi-clave-secreta-super-dificil'
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui' # Necesario para los mensajes 'flash'

proyectos_lista = [
    {
        'id': 1,
        'titulo': 'Generador de Calendarios de Contenido con IA',
        'descripcion': 'Una aplicación web construida con Streamlit y Pandas que utiliza la API de OpenAI para generar planes de contenido de marketing y exportarlos a CSV.'
    },
    {
        'id': 2,
        'titulo': 'Gestor de Ideas con IA y Base de Datos',
        'descripcion': 'Una herramienta de terminal para guardar y potenciar ideas creativas, con memoria persistente gracias a una base de datos SQLite.'
    }
]

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

@app.route('/')
def pagina_de_inicio():
    return render_template('index.html')

@app.route('/sobre-mi')
def sobre_mi():
    return render_template('sobre-mi.html')

@app.route('/proyectos')
def proyectos():
    return render_template('proyectos.html', proyectos=proyectos_lista)

# --- RUTAS DEL BLOG ---

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        password = request.form['password']
        # En una app real, esta contraseña estaría en una variable de entorno
        if password == '12345':
            session['logged_in'] = True
            return redirect(url_for('blog'))
        else:
            flash('Contraseña incorrecta.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('pagina_de_inicio'))

@app.route('/blog')
def blog():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY created DESC').fetchall()
    conn.close()
    return render_template('blog.html', posts=posts)

@app.route('/blog/<int:post_id>')
def post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    return render_template('post.html', post=post)

@app.route('/blog/create', methods=('GET', 'POST'))
@login_required
def create():
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('¡El título es obligatorio!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('blog'))

    return render_template('create.html')

if __name__ == '__main__':
    app.run(debug=True)