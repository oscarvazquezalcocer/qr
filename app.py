from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import sqlite3
import qrcode
import os
import smbclient

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necesario para usar flash()

# Información de conexión SMB
server_ip = '172.16.1.38'  # IP del servidor Windows 10
username = 'sdcano'  # Usuario con permisos para escribir en el recurso
password = 'sextavez-16'  # Contraseña del usuario
share_name = 'rqalumno'  # Nombre del recurso compartido en Windows

# Configurar la autenticación para SMB
smbclient.ClientConfig(username=username, password=password)

# Función para generar y guardar el código QR
def generar_qr(data, nombre_qr):
    # Crear el código QR
    qr = qrcode.make(data)
    # Convertir la imagen a RGB (elimina la transparencia)
    qr = qr.convert("RGB")
    # Guardar la imagen en la carpeta qr
    if not os.path.exists('static/qr'):
        os.makedirs('static/qr')
    qr.save(f'static/qr/{nombre_qr}.jpg', 'JPEG')

    qr_filename = f"{nombre_qr}.jpg"
    qr_path = os.path.join('static', 'qr', qr_filename)

    # Subir la firma a la carpeta compartida en el servidor SMB
    remote_file_path = f'\\\\{server_ip}\\\\{share_name}\\\\{qr_filename}'

    # Subir el archivo a la ruta SMB
    with smbclient.open_file(remote_file_path, mode='wb') as remote_file:
        with open(qr_path, 'rb') as local_file:
            remote_file.write(local_file.read())

# Función para guardar datos en la base de datos
def guardar_en_base_de_datos(dataframe):
    try:
        # Conectar a la base de datos SQLite (se crea si no existe)
        conn = sqlite3.connect('base_de_datos.db')
        cursor = conn.cursor()
        
        # Crear tabla si no existe
        cursor.execute('''CREATE TABLE IF NOT EXISTS datos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nss TEXT,
                            nombres TEXT,
                            apellidos TEXT,
                            semestre TEXT,
                            tipo_sangre TEXT,
                            telefono_emergencia TEXT)''')
        
        # Insertar datos en la tabla
        for _, row in dataframe.iterrows():
            cursor.execute("INSERT INTO datos (nss, nombres, apellidos, semestre, tipo_sangre, telefono_emergencia) VALUES (?, ?, ?, ?, ?, ?)",
                           (row['nss'], row['nombres'], row['apellidos'], row['semestre'], row['tipo_sangre'], row['telefono_emergencia']))
        
        # Guardar los cambios y cerrar la conexión
        conn.commit()
        conn.close()
        print("Datos guardados en la base de datos correctamente.")
    except Exception as e:
        print(f"Error al guardar en la base de datos: {e}")

# Página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para subir el archivo CSV
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    if file and file.filename.endswith('.csv'):
        # Leer el archivo CSV, forzando la columna 'nss' a ser tratada como texto
        df = pd.read_csv(file, dtype={'nss': str, 'telefono_de_emergencia': str})  # Forzamos 'nss' a tipo string

        # Convertir la columna 'nss' a tipo string (esto asegura que sea tratado como texto)
        df['nss'] = df['nss'].astype(str)

        # Reemplazar todos los valores NaN por una cadena vacía en el DataFrame
        df = df.fillna('')

        # Asegurarse de que las columnas necesarias existan en el CSV
        required_columns = ['matricula', 'nss', 'nombres', 'apellido_paterno', 'apellido_materno', 'tipo_de_sangre', 'telefono_de_emergencia', 'contacto_de_emergencia']
        if not all(col in df.columns for col in required_columns):
            flash(f"El archivo CSV debe contener las columnas {', '.join(required_columns)}")
            return redirect(url_for('index'))
        
        # Filtrar las columnas que nos interesan para la base de datos y para el QR
        columnas_para_base_de_datos = df[required_columns]
        
        # Guardar los datos en la base de datos
        #guardar_en_base_de_datos(columnas_para_base_de_datos)
        
        # Generar y guardar los códigos QR para cada fila
        for i, row in columnas_para_base_de_datos.iterrows():
            # Generar el contenido para el QR (concatenando las columnas relevantes)
            data_qr = (f"Nombre: {row['apellido_paterno']} {row['apellido_materno']} {row['nombres']} | "
                       f"Tipo de sangre: {row['tipo_de_sangre']} | "
                       f"NSS: {row['nss']} | "
                       f"Contacto de Emergencia: {row['contacto_de_emergencia']} | "
                       f"Telefono de Emergencia: {row['telefono_de_emergencia']} | ")
            
            # Nombre del archivo QR será el NSS de la fila
            nombre_qr = str(row['matricula'])  # Aseguramos que el nombre sea una cadena
            
            # Crear el código QR y guardarlo
            generar_qr(data_qr, nombre_qr)
        
        flash('Archivo procesado correctamente. Los códigos QR fueron generados.')
        return redirect(url_for('index'))
    else:
        flash('Solo se permiten archivos CSV')
        return redirect(url_for('index'))

if __name__ == '__main__':

  app.run(debug=True, host='0.0.0.0', port="5001", use_reloader=False)
  
  
  
  
