from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import date

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('homebase.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def inicio():
    conn = get_db()
    eventos = conn.execute('SELECT fecha, categoria FROM agenda').fetchall()
    conn.close()
    eventos_dict = {}
    for e in eventos:
        fecha = e['fecha']
        cat = e['categoria']
        if fecha not in eventos_dict:
            eventos_dict[fecha] = []
        eventos_dict[fecha].append(cat)
    import json
    return render_template('index.html', eventos_json=json.dumps(eventos_dict))
@app.route('/gastos', methods=['GET', 'POST'])
def gastos():
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        importe = (request.form['importe'])
        categoria = request.form['categoria']
        fecha= str(date.today())
        conn = get_db()
        conn.execute('INSERT INTO gastos(descripcion, importe, categoria, fecha) VALUES (?, ?, ?, ?)',
                     (descripcion, importe, categoria, fecha))
        conn.commit()
        conn.close()
        return redirect(url_for('gastos'))
    conn = get_db()
    lista_gastos = conn.execute('SELECT * FROM gastos ORDER BY fecha DESC').fetchall()
    conn.close()
    return render_template('gastos.html', gastos=lista_gastos)

@app.route('/gastos/borrar/<int:id>')
def borrar_gasto(id):
    conn = get_db()
    conn.execute('DELETE FROM gastos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('gastos')) 

@app.route('/ingresos', methods=['GET', 'POST'])
def ingresos():
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        importe = (request.form['importe'])
        categoria = request.form['categoria']
        fecha= str(date.today())
        conn = get_db()
        conn.execute('INSERT INTO ingresos(descripcion, importe, categoria, fecha) VALUES (?, ?, ?, ?)',
                     (descripcion, importe, categoria, fecha))
        conn.commit()
        conn.close()
        return redirect(url_for('ingresos'))
    conn = get_db()
    lista_ingresos = conn.execute('SELECT * FROM ingresos ORDER BY fecha DESC').fetchall()
    conn.close()
    return render_template('ingresos.html', ingresos=lista_ingresos)

@app.route('/ingresos/borrar/<int:id>')
def borrar_ingreso(id):
    conn = get_db()
    conn.execute('DELETE FROM ingresos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('ingresos'))

@app.route('/agenda', methods=['GET', 'POST'])
def agenda():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        fecha = request.form['fecha']
        hora = request.form['hora']
        categoria = request.form['categoria']
        conn = get_db()
        conn.execute('INSERT INTO agenda(titulo, descripcion, fecha,hora, categoria) VALUES (?, ?, ?, ?, ?)',
                     (titulo, descripcion, fecha, hora, categoria, ))
        conn.commit()
        conn.close()
        return redirect(url_for('agenda'))
    conn = get_db()
    lista_agenda = conn.execute('SELECT * FROM agenda ORDER BY fecha DESC').fetchall()
    conn.close()
    return render_template('agenda.html', eventos=lista_agenda)

@app.route('/agenda/borrar/<int:id>')
def borrar_evento(id):
    conn = get_db()
    conn.execute('DELETE FROM agenda WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('agenda'))

@app.route('/objetivos', methods=['GET', 'POST'])
def objetivos():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        importe_total = float(request.form['importe_total'])
        fecha_limite = request.form['fecha_limite']
        emoji = request.form['emoji']
        conn = get_db()
        conn.execute('INSERT INTO objetivos(nombre, descripcion, importe_total, fecha_limite, emoji) VALUES (?, ?, ?, ?, ?)',
                     (nombre, descripcion, importe_total, fecha_limite, emoji))
        conn.commit()
        conn.close()
        return redirect(url_for('objetivos'))
    conn = get_db()
    lista_objetivos = conn.execute('SELECT * FROM objetivos ORDER BY fecha_limite DESC').fetchall()
    conn.close()
    return render_template('objetivos.html', objetivos=lista_objetivos)

@app.route('/objetivos/borrar/<int:id>')
def borrar_objetivo(id):
    conn = get_db()
    conn.execute('DELETE FROM objetivos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('objetivos'))

@app.route('/objetivos/abonar/<int:id>', methods=['POST'])
def abonar_objetivo(id):
    importe = float(request.form['importe'])
    conn = get_db()
    conn.execute('UPDATE objetivos SET importe_actual = importe_actual + ? WHERE id = ?', (importe, id))
    conn.commit()
    conn.close()
    return redirect(url_for('objetivos'))
if __name__ == '__main__':
    app.run(debug=True)