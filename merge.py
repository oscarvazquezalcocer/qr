import pandas as pd

# Cargar los archivos CSV asegurándonos de que 'matricula' y 'nss' son tratados como texto
credenciales = pd.read_csv('credenciales.csv', dtype=str)
nss = pd.read_csv('nss.csv', dtype=str)

# Realizamos el merge de ambos archivos utilizando 'matricula' como clave
merged_df = pd.merge(credenciales, nss[['matricula', 'nss']], on='matricula', how='left')

# Crear la columna 'apellidos' combinando 'apellido_paterno' y 'apellido_materno'
#merged_df['apellidos'] = merged_df['apellido_paterno'] + ' ' + merged_df['apellido_materno']

# Guardamos el archivo combinado en un nuevo CSV
merged_df.to_csv('credenciales_con_nss.csv', index=False)

print("El archivo 'credenciales_con_nss.csv' ha sido creado con la columna 'nss' y 'apellidos' añadida.")
