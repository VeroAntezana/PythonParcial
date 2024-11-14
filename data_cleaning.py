import pandas as pd
import json

def clean_monetary_value(value):
    """Limpia valores monetarios eliminando separadores de miles y convirtiéndolos a float"""
    if isinstance(value, str):
        # Eliminar separadores de miles (.)
        value = value.replace('.', '').replace(',', '').replace('$', '').replace(' ', '').replace('-', '0')
        try:
            return float(value) if value else 0
        except ValueError:
            print(f"Error al convertir el valor: {value}")
            return 0
    return float(value) if pd.notnull(value) else 0



def load_and_clean_data(file_path):
    """Carga, limpia y valida los datos del archivo JSON"""
    try:
        # Abrir y cargar el archivo JSON
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Depuración: mostrar contenido inicial del JSON
        print("--- Contenido inicial del JSON ---")
        print(json.dumps(data, indent=4))  # Muestra el contenido del JSON

        # Validar que la clave 'DatosTransporte' existe y no está vacía
        if 'DatosTransporte' not in data or not data['DatosTransporte']:
            print("Error: La clave 'DatosTransporte' no existe o está vacía en el JSON.")
            return None

        # Crear un DataFrame desde la clave 'DatosTransporte'
        df = pd.DataFrame(data['DatosTransporte'])

        # Mostrar información inicial
        print("--- Información inicial ---")
        print(df.info())
        print("\nPrimeras filas:\n", df.head())

        # Limpieza de columnas monetarias
        monetary_columns = ['COSTO_MANO_DE_OBRA', 'COSTO_ACPM', 'VALOR_PEAJES', 'ALOJAM', 'DIVERSOS', 'FLETE']
        for col in monetary_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: clean_monetary_value(x) if pd.notnull(x) else 0)
        print(f"Valores limpios en la columna {col}:")
        print(df[col].head())


        # Limpieza de columnas de tiempo
        time_columns = ['TIEMPO_EN_EL_VIAJE', 'HORAS_MOTOR', 'TIEMPO_DE_CARGUE', 'TIEMPO_MUERTO']
        for col in time_columns:
            if col in df.columns:
                # Reemplazar valores no válidos con 0 antes de convertir
                df[col] = df[col].fillna(0)  # Reemplazar NaN con 0
                df[col] = pd.to_timedelta(df[col], unit='ms', errors='coerce').fillna(pd.Timedelta(seconds=0))
                print(f"Valores limpios en {col}:")
                print(df[col].head())
            

        # Convertir fechas en formato adecuado
        if 'FECHA' in df.columns:
            df['MES'] = pd.to_datetime(df['FECHA'] + '-2024', format='%d-%b-%Y', errors='coerce').dt.strftime('%Y-%m')
            print("Valores procesados para MES:")
            print(df['MES'].head())

        print("\n--- Datos nulos por columna ---")
        print(df.isnull().sum())

        # Convertir CANTIDAD_CARGADA y CANTIDAD_DESCARGADA a valores numéricos
        if 'CANTIDAD_CARGADA' in df.columns and 'CANTIDAD_DESCARGADA' in df.columns:
            df['CANTIDAD_CARGADA'] = pd.to_numeric(df['CANTIDAD_CARGADA'], errors='coerce').fillna(0)
            df['CANTIDAD_DESCARGADA'] = pd.to_numeric(df['CANTIDAD_DESCARGADA'], errors='coerce').fillna(0)

        # Eliminar filas con valores nulos en columnas clave
        key_columns = ['CONSUMO_ACPM', 'DISTANCIA_RECORRIDA']
        for col in key_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df.dropna(subset=key_columns)

        # Verificar valores negativos en columnas clave
        print("\n--- Valores negativos en columnas clave ---")
        for col in key_columns:
            negativos = df[df[col] < 0]
            if not negativos.empty:
                print(f"Valores negativos encontrados en {col}:")
                print(negativos)

        # Eliminar valores negativos
        print("\n--- Eliminando valores negativos ---")
        df = df[(df['CONSUMO_ACPM'] >= 0) & (df['DISTANCIA_RECORRIDA'] >= 0)]
        print(f"Filas después de eliminar valores negativos: {len(df)}")

        # Verificar duplicados
        print("\n--- Duplicados ---")
        duplicados = df[df.duplicated()]
        if not duplicados.empty:
            print("Duplicados encontrados:")
            print(duplicados)
        df = df.drop_duplicates()

        # Mostrar información final
        print("\n--- Información final ---")
        print(df.info())
        print("\nPrimeras filas después de limpieza:\n", df.head())

        return df
    except Exception as e:
        print(f"Error al cargar y limpiar los datos: {str(e)}")
        return None

# Guardar los datos limpios

def save_clean_data(df, output_path):
    """Guarda el DataFrame limpio en un archivo JSON"""
    try:
        df.to_json(output_path, orient='records', indent=4)
        print(f"Datos limpios guardados en: {output_path}")
    except Exception as e:
        print(f"Error al guardar los datos limpios: {str(e)}")

# Ruta al archivo JSON de entrada
input_file = r"C:\Veronica\2-2024\sw2\2Parcial\Parcial-2\dataset.json"
# Ruta al archivo JSON de salida
output_file = r"C:\Veronica\2-2024\sw2\2Parcial\Parcial-2\dataset_limpio.json"

# Cargar, limpiar y guardar los datos
dataframe = load_and_clean_data(input_file)
if dataframe is not None:
    save_clean_data(dataframe, output_file)
