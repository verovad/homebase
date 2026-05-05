from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
import json
import functools

app = Flask(__name__)
app.secret_key = 'homebase_secret_2026'

def get_db():
    conn = sqlite3.connect('homebase.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        try:
            conn = get_db()
            conn.execute('INSERT INTO usuarios(nombre, email, password) VALUES (?, ?, ?)',
                        (nombre, email, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            return render_template('registro.html', error='El email ya está registrado')
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db()
        usuario = conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
        conn.close()
        if usuario and check_password_hash(usuario['password'], password):
            session['usuario_id'] = usuario['id']
            session['usuario_nombre'] = usuario['nombre']
            return redirect(url_for('inicio'))
        return render_template('login.html', error='Email o contraseña incorrectos')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def inicio():
    conn = get_db()
    uid = session['usuario_id']
    total_ingresos = conn.execute(
        "SELECT COALESCE(SUM(importe), 0) FROM ingresos WHERE usuario_id=? AND strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')", (uid,)
    ).fetchone()[0]
    total_gastos = conn.execute(
        "SELECT COALESCE(SUM(importe), 0) FROM gastos WHERE usuario_id=? AND strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')", (uid,)
    ).fetchone()[0]
    balance = total_ingresos - total_gastos
    total_objetivos = conn.execute("SELECT COUNT(*) FROM objetivos WHERE usuario_id=?", (uid,)).fetchone()[0]
    eventos = conn.execute('SELECT fecha, categoria FROM agenda WHERE usuario_id=?', (uid,)).fetchall()
    conn.close()
    eventos_dict = {}
    for e in eventos:
        fecha = e['fecha']
        cat = e['categoria']
        if fecha not in eventos_dict:
            eventos_dict[fecha] = []
        eventos_dict[fecha].append(cat)
    return render_template('index.html',
        eventos_json=json.dumps(eventos_dict),
        total_ingresos=round(total_ingresos, 2),
        total_gastos=round(total_gastos, 2),
        balance=round(balance, 2),
        total_objetivos=total_objetivos)

@app.route('/gastos', methods=['GET', 'POST'])
@login_required
def gastos():
    uid = session['usuario_id']
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        importe = request.form['importe']
        categoria = request.form['categoria']
        fecha = str(date.today())
        conn = get_db()
        conn.execute('INSERT INTO gastos(usuario_id, descripcion, importe, categoria, fecha) VALUES (?, ?, ?, ?, ?)',
                     (uid, descripcion, importe, categoria, fecha))
        conn.commit()
        conn.close()
        return redirect(url_for('gastos'))
    conn = get_db()
    lista_gastos = conn.execute('SELECT * FROM gastos WHERE usuario_id=? ORDER BY fecha DESC', (uid,)).fetchall()
    categorias = conn.execute('SELECT categoria, SUM(importe) as total FROM gastos WHERE usuario_id=? GROUP BY categoria', (uid,)).fetchall()
    conn.close()
    categorias_dict = {row['categoria']: row['total'] for row in categorias}
    return render_template('gastos.html', gastos=lista_gastos, categorias_json=json.dumps(categorias_dict))

@app.route('/gastos/borrar/<int:id>')
@login_required
def borrar_gasto(id):
    conn = get_db()
    conn.execute('DELETE FROM gastos WHERE id=? AND usuario_id=?', (id, session['usuario_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('gastos'))

@app.route('/ingresos', methods=['GET', 'POST'])
@login_required
def ingresos():
    uid = session['usuario_id']
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        importe = request.form['importe']
        categoria = request.form['categoria']
        fecha = str(date.today())
        conn = get_db()
        conn.execute('INSERT INTO ingresos(usuario_id, descripcion, importe, categoria, fecha) VALUES (?, ?, ?, ?, ?)',
                     (uid, descripcion, importe, categoria, fecha))
        conn.commit()
        conn.close()
        return redirect(url_for('ingresos'))
    conn = get_db()
    lista_ingresos = conn.execute('SELECT * FROM ingresos WHERE usuario_id=? ORDER BY fecha DESC', (uid,)).fetchall()
    conn.close()
    return render_template('ingresos.html', ingresos=lista_ingresos)

@app.route('/ingresos/borrar/<int:id>')
@login_required
def borrar_ingreso(id):
    conn = get_db()
    conn.execute('DELETE FROM ingresos WHERE id=? AND usuario_id=?', (id, session['usuario_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('ingresos'))

@app.route('/agenda', methods=['GET', 'POST'])
@login_required
def agenda():
    uid = session['usuario_id']
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        fecha = request.form['fecha']
        hora = request.form['hora']
        categoria = request.form['categoria']
        conn = get_db()
        conn.execute('INSERT INTO agenda(usuario_id, titulo, descripcion, fecha, hora, categoria) VALUES (?, ?, ?, ?, ?, ?)',
                     (uid, titulo, descripcion, fecha, hora, categoria))
        conn.commit()
        conn.close()
        return redirect(url_for('agenda'))
    conn = get_db()
    lista_agenda = conn.execute('SELECT * FROM agenda WHERE usuario_id=? ORDER BY fecha ASC', (uid,)).fetchall()
    conn.close()
    return render_template('agenda.html', eventos=lista_agenda)

@app.route('/agenda/borrar/<int:id>')
@login_required
def borrar_evento(id):
    conn = get_db()
    conn.execute('DELETE FROM agenda WHERE id=? AND usuario_id=?', (id, session['usuario_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('agenda'))

@app.route('/objetivos', methods=['GET', 'POST'])
@login_required
def objetivos():
    uid = session['usuario_id']
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        importe_total = float(request.form['importe_total'])
        fecha_limite = request.form['fecha_limite']
        emoji = request.form['emoji']
        conn = get_db()
        conn.execute('INSERT INTO objetivos(usuario_id, nombre, descripcion, importe_total, fecha_limite, emoji) VALUES (?, ?, ?, ?, ?, ?)',
                     (uid, nombre, descripcion, importe_total, fecha_limite, emoji))
        conn.commit()
        conn.close()
        return redirect(url_for('objetivos'))
    conn = get_db()
    lista_objetivos = conn.execute('SELECT * FROM objetivos WHERE usuario_id=? ORDER BY fecha_limite ASC', (uid,)).fetchall()
    conn.close()
    return render_template('objetivos.html', objetivos=lista_objetivos)

@app.route('/objetivos/borrar/<int:id>')
@login_required
def borrar_objetivo(id):
    conn = get_db()
    conn.execute('DELETE FROM objetivos WHERE id=? AND usuario_id=?', (id, session['usuario_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('objetivos'))

@app.route('/objetivos/abonar/<int:id>', methods=['POST'])
@login_required
def abonar_objetivo(id):
    importe = float(request.form['importe'])
    conn = get_db()
    conn.execute('UPDATE objetivos SET importe_actual = importe_actual + ? WHERE id=? AND usuario_id=?',
                 (importe, id, session['usuario_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('objetivos'))

@app.route('/familia', methods=['GET', 'POST'])
@login_required
def familia():
    uid = session['usuario_id']
    if request.method == 'POST':
        nombre = request.form['nombre']
        rol = request.form['rol']
        avatar = request.form['avatar']
        color = request.form['color']
        conn = get_db()
        conn.execute('INSERT INTO familia(usuario_id, nombre, rol, avatar, color) VALUES (?, ?, ?, ?, ?)',
                     (uid, nombre, rol, avatar, color))
        conn.commit()
        conn.close()
        return redirect(url_for('familia'))
    conn = get_db()
    miembros = conn.execute('SELECT * FROM familia WHERE usuario_id=?', (uid,)).fetchall()
    conn.close()
    return render_template('familia.html', miembros=miembros)

@app.route('/familia/borrar/<int:id>')
@login_required
def borrar_miembro(id):
    conn = get_db()
    conn.execute('DELETE FROM familia WHERE id=? AND usuario_id=?', (id, session['usuario_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('familia'))

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)