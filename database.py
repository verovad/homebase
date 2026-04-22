import sqlite3

def init_db():
    conn = sqlite3.connect('homebase.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS gastos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            importe REAL NOT NULL,
            categoria TEXT NOT NULL,
            fecha TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS ingresos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            importe REAL NOT NULL,
            categoria TEXT NOT NULL,
            fecha TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS agenda(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            fecha TEXT NOT NULL,
            hora TEXT,
            categoria TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS objetivos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            importe_total REAL NOT NULL,
            importe_actual REAL DEFAULT 0,
            fecha_limite TEXT,
            emoji TEXT)''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Base de datos inicializada correctamente.")
