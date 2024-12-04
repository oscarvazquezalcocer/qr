import pandas as pd

year = '2024'
# Cargar los archivos CSV asegurándonos de que 'matricula' y 'nss' son tratados como texto
credenciales = pd.read_csv(f"credenciales-{year}.csv", dtype=str)
nss = pd.read_csv(f"nss-{year}.csv", dtype=str)

# Realizamos el merge de ambos archivos utilizando 'matricula' como clave
merged_df = pd.merge(credenciales, nss[['matricula', 'nss']], on='matricula', how='left')

# Guardamos el archivo combinado en un nuevo CSV
merged_df.to_csv(f"credenciales_con_nss-{year}.csv", index=False)

print(f"El archivo 'credenciales_con_nss-{year}.csv' ha sido creado con la columna 'nss' y 'nombres' añadida.")
