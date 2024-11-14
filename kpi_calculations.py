import pandas as pd
import numpy as np
from datetime import datetime
import json

def clean_monetary_value(value):
    """Limpia valores monetarios removiendo símbolos y espacios"""
    if isinstance(value, str):
        return float(value.replace('$', '').replace(',', '').replace(' ', '').replace('-', '0'))
    return float(value) if pd.notnull(value) else 0

def load_data(file_path):
    """Carga y preprocesa los datos del archivo JSON"""
    try:
        # Abrir y cargar el archivo JSON
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        # Verificar si los datos están en la estructura correcta
        if isinstance(data, dict) and 'DatosTransporte' in data:
            df = pd.DataFrame(data['DatosTransporte'])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            print("Formato de datos inesperado")
            print("Estructura de datos recibida:", type(data))
            print("Muestra de datos:", data[:2] if isinstance(data, list) else data)
            return None

        print("--- Datos cargados ---")
        print("Columnas disponibles:", df.columns.tolist())
        print("Primeras filas:", df.head())

        # Limpieza de columnas monetarias
        monetary_columns = ['COSTO_MANO_DE_OBRA', 'COSTO_ACPM', 'VALOR_PEAJES', 'ALOJAM', 'DIVERSOS', 'FLETE']
        for col in monetary_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: clean_monetary_value(x) if pd.notnull(x) else 0)

        # Limpieza de columnas de tiempo
        time_columns = ['TIEMPO_EN_EL_VIAJE', 'HORAS_MOTOR', 'TIEMPO_DE_CARGUE', 'TIEMPO_MUERTO']
        for col in time_columns:
            if col in df.columns:
                # Convierte de valores en milisegundos a timedelta
                df[col] = pd.to_timedelta(df[col], unit='ms', errors='coerce').fillna(pd.Timedelta(seconds=0))
            print(f"Valores procesados para {col}:")
        print(df[col].head())


        # Convertir fechas en formato adecuado
        if 'FECHA' in df.columns:
            df['MES'] = pd.to_datetime(df['FECHA'] + '-2024', format='%d-%b-%Y', errors='coerce').dt.strftime('%Y-%m')
            print("Valores procesados para MES:")
            print(df['MES'].head())


        return df
    except Exception as e:
        print(f"Error al cargar los datos: {str(e)}")
        return None

def calculate_kpis(df):
    """Calcula los KPIs a partir del DataFrame"""
    
    if df is None or not isinstance(df, pd.DataFrame):
        print("Error: Los datos no son un DataFrame válido")
        return {}

    print("Calculando KPIs con DataFrame de forma:", df.shape)
    print("Columnas disponibles:", df.columns.tolist())
    kpis = {}

    try:
        # 1. Consumo de Combustible por Kilómetro
        if 'CONSUMO_ACPM' in df.columns and 'DISTANCIA_RECORRIDA' in df.columns:
            consumo_km = df['CONSUMO_ACPM'].sum() / df['DISTANCIA_RECORRIDA'].sum()
            kpis['consumo_acpm_km'] = round(consumo_km, 2)

            # Consumo mensual para gráficas
            consumo_mensual = df.groupby('MES').apply(
                lambda x: x['CONSUMO_ACPM'].sum() / x['DISTANCIA_RECORRIDA'].sum()
            ).round(2).tail(6).to_dict()
            kpis['consumo_mensual'] = consumo_mensual

        # 2. Costo de Combustible por Viaje
        if 'COSTO_ACPM' in df.columns:
            kpis['costo_combustible_viaje'] = round(df['COSTO_ACPM'].mean(), 2)

            # Costo mensual
            costo_mensual = df.groupby('MES')['COSTO_ACPM'].mean().round(2).tail(6).to_dict()
            kpis['costo_combustible_viaje_mensual'] = costo_mensual

        # 3. Productividad de la Flota
        if 'DISTANCIA_RECORRIDA' in df.columns and 'DIAS_DE_VIAJE' in df.columns:
            productividad = df['DISTANCIA_RECORRIDA'].sum() / df['DIAS_DE_VIAJE'].sum()
            kpis['productividad_flota'] = round(productividad, 2)

            # Productividad mensual
            productividad_mensual = df.groupby('MES').apply(
                lambda x: x['DISTANCIA_RECORRIDA'].sum() / x['DIAS_DE_VIAJE'].sum()
            ).round(2).tail(6).to_dict()
            kpis['productividad_mensual'] = productividad_mensual

        # 4. Costo Total por Kilómetro
        cost_columns = ['COSTO_MANO_DE_OBRA', 'VALOR_PEAJES', 'COSTO_ACPM', 'ALOJAM', 'DIVERSOS']
        available_cost_columns = [col for col in cost_columns if col in df.columns]

        if available_cost_columns and 'DISTANCIA_RECORRIDA' in df.columns:
            df['COSTO_TOTAL'] = df[available_cost_columns].sum(axis=1)
            costo_km = df['COSTO_TOTAL'].sum() / df['DISTANCIA_RECORRIDA'].sum()
            kpis['costo_total_km'] = round(costo_km, 2)

            # Costos totales mensuales
            costo_total_mensual = df.groupby('MES').apply(
                lambda x: x['COSTO_TOTAL'].sum() / x['DISTANCIA_RECORRIDA'].sum()
            ).round(2).tail(6).to_dict()
            kpis['costo_total_mensual'] = costo_total_mensual

        # 5. Tiempo Promedio de Viaje
        if 'TIEMPO_EN_EL_VIAJE' in df.columns and 'ORIGEN' in df.columns and 'DESTINO' in df.columns:
            tiempo_ruta = df.groupby(['ORIGEN', 'DESTINO'])['TIEMPO_EN_EL_VIAJE'].mean()
            kpis['tiempo_por_ruta'] = {
                f"{o}-{d}": round(t.total_seconds() / 3600, 2)
                for (o, d), t in tiempo_ruta.items() if pd.notnull(t)
            }
        else:
            print("No hay datos válidos para calcular TIEMPO_EN_EL_VIAJE por ruta.")
            kpis['tiempo_por_ruta'] = {}

        #6. Porcentaje de carga no entregada

        

        # Tendencia de Costos
        if 'DISTANCIA_RECORRIDA' in df.columns and 'COSTO_TOTAL' in df.columns:
            costo_total_mensual = df.groupby('MES').apply(
                lambda x: x['COSTO_TOTAL'].sum() / x['DISTANCIA_RECORRIDA'].sum()
                if x['DISTANCIA_RECORRIDA'].sum() > 0 else 0
            ).round(2).tail(6).to_dict()
            kpis['tendencia_costos'] = costo_total_mensual

        # Tiempo por Ruta
        if 'TIEMPO_EN_EL_VIAJE' in df.columns and 'ORIGEN' in df.columns and 'DESTINO' in df.columns:
            tiempo_ruta = df.groupby(['ORIGEN', 'DESTINO'])['TIEMPO_EN_EL_VIAJE'].mean()
            kpis['tiempo_por_ruta'] = {
                f"{o}-{d}": round(t.total_seconds() / 3600, 2)
                for (o, d), t in tiempo_ruta.items() if pd.notnull(t)
            }
        # KPI: Porcentaje de Entrega no Entregada
        if 'CANTIDAD_CARGADA' in df.columns and 'CANTIDAD_DESCARGADA' in df.columns:
            df['CANTIDAD_CARGADA'] = pd.to_numeric(df['CANTIDAD_CARGADA'], errors='coerce')
            df['CANTIDAD_DESCARGADA'] = pd.to_numeric(df['CANTIDAD_DESCARGADA'], errors='coerce')
            df['NO_ENTREGADA'] = (df['CANTIDAD_CARGADA'] - df['CANTIDAD_DESCARGADA']).clip(lower=0)
            
            total_cargada = df['CANTIDAD_CARGADA'].sum()
            total_no_entregada = df['NO_ENTREGADA'].sum()
            
            if total_cargada > 0:
                porcentaje_no_entregado = (total_no_entregada / total_cargada) * 100
            else:
                porcentaje_no_entregado = 0
            
            kpis['porcentaje_no_entregado'] = round(porcentaje_no_entregado, 2)
        else:
            print("Las columnas CANTIDAD_CARGADA o CANTIDAD_DESCARGADA no están presentes.")
            kpis['porcentaje_no_entregado'] = 0

         
        return kpis
    except Exception as e:
        print(f"Error al calcular KPIs: {str(e)}")
        return {}
