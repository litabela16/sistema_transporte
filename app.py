from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
app = Flask(__name__)
app.secret_key = "clave_secreta_trans_urus"

DATABASE = "transportes.db"

# =========================
# CREAR BASE DE DATOS
# =========================
def crear_bd():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # USUARIOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # CONDUCTORES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conductores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        carnet TEXT,
        edad INTEGER,
        categoria TEXT,
        seguro TEXT
    )
    """)

    # BUSES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS buses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        placa TEXT,
        modelo TEXT,
        capacidad INTEGER,
        anio INTEGER,
        estado TEXT
    )
    """)

    # RUTAS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rutas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        origen TEXT,
        destino TEXT,
        recorrido TEXT,
        horas_aprox TEXT,
        autorizacion TEXT
    )
    """)

    # VIAJES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS viajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    horario TEXT,
    conductor_id INTEGER,
    conductor_suplente_id INTEGER,
    bus_id INTEGER,
    ruta_id INTEGER,
    FOREIGN KEY(conductor_id) REFERENCES conductores(id),
    FOREIGN KEY(conductor_suplente_id) REFERENCES conductores(id),
    FOREIGN KEY(bus_id) REFERENCES buses(id),
    FOREIGN KEY(ruta_id) REFERENCES rutas(id)
    )
    """)

    conn.commit()
    conn.close()

# =========================
# CREAR ADMIN AUTOMATICO
# =========================
def crear_admin():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (username,password) VALUES('admin','1234')")
        conn.commit()
    conn.close()

# CREAR TABLAS Y ADMIN
crear_bd()
crear_admin()

# =========================
# LOGIN
# =========================
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username,password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['usuario'] = username
            return redirect(url_for('index'))
        else:
            flash("Datos incorrectos")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario',None)
    return redirect(url_for('login'))

# =========================
# INICIO
# =========================
@app.route('/')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# =========================
# =========================
# USUARIOS
# =========================
@app.route('/usuarios')
def usuarios():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM usuarios")
    lista = cursor.fetchall()
    conn.close()

    return render_template('usuarios.html', usuarios=lista)
# CONDUCTORES
# =========================
@app.route('/conductores')
def conductores():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conductores")
    datos = cursor.fetchall()
    conn.close()
    return render_template('conductores.html', conductores=datos)

@app.route('/agregar_conductor', methods=['POST'])
def agregar_conductor():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conductores(nombre,carnet,edad,categoria,seguro)
        VALUES(?,?,?,?,?)
    """, (
        request.form['nombre'],
        request.form['carnet'],
        request.form['edad'],
        request.form['categoria'],
        request.form['seguro']
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('conductores'))

# =========================
# BUSES
# =========================
@app.route('/buses')
def buses():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM buses")
    datos = cursor.fetchall()
    conn.close()
    return render_template('buses.html', buses=datos)

@app.route('/agregar_bus', methods=['POST'])
def agregar_bus():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO buses(placa,modelo,capacidad,anio,estado)
        VALUES(?,?,?,?,?)
    """, (
        request.form['placa'],
        request.form['modelo'],
        request.form['capacidad'],
        request.form['anio'],
        request.form['estado']
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('buses'))

# =========================
# RUTAS
# =========================
@app.route('/rutas')
def rutas():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rutas")
    datos = cursor.fetchall()
    conn.close()
    return render_template('rutas.html', rutas=datos)

@app.route('/agregar_ruta', methods=['POST'])
def agregar_ruta():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO rutas(origen,destino,recorrido,horas_aprox,autorizacion)
        VALUES(?,?,?,?,?)
    """, (
        request.form['origen'],
        request.form['destino'],
        request.form['recorrido'],
        request.form['horas_aprox'],
        request.form['autorizacion']
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('rutas'))

# =========================
# VIAJES
# =========================
@app.route('/viajes')
def viajes():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT viajes.id, fecha, horario,
       c1.nombre,
       c2.nombre,
       buses.placa,
       rutas.origen || ' - ' || rutas.destino
FROM viajes
JOIN conductores c1 ON viajes.conductor_id = c1.id
LEFT JOIN conductores c2 ON viajes.conductor_suplente_id = c2.id
JOIN buses ON viajes.bus_id = buses.id
JOIN rutas ON viajes.ruta_id = rutas.id
    """)
    datos = cursor.fetchall()

    cursor.execute("SELECT id,nombre FROM conductores")
    conductores = cursor.fetchall()

    cursor.execute("SELECT id,placa FROM buses")
    buses = cursor.fetchall()

    cursor.execute("SELECT id,origen || ' - ' || destino FROM rutas")
    rutas_lista = cursor.fetchall()

    conn.close()

    return render_template('viajes.html',
                           viajes=datos,
                           conductores=conductores,
                           buses=buses,
                           rutas=rutas_lista)

@app.route('/agregar_viaje', methods=['POST'])
def agregar_viaje():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    suplente = request.form['conductor_suplente_id']
    if suplente == "":
        suplente = None

    cursor.execute("""
        INSERT INTO viajes(fecha,horario,conductor_id,conductor_suplente_id,bus_id,ruta_id)
        VALUES(?,?,?,?,?,?)
    """, (
        request.form['fecha'],
        request.form['horario'],
        request.form['conductor_id'],
        suplente,
        request.form['bus_id'],
        request.form['ruta_id']
    ))

    conn.commit()
    conn.close()
    return redirect(url_for('viajes'))

if __name__ == '__main__':
    app.run(debug=True)