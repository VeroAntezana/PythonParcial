import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def clean_monetary_value(value):
    """Limpia valores monetarios removiendo símbolos y espacios"""
    if isinstance(value, str):
        return float(value.replace('$', '').replace(',', '').replace('.', '').strip())
    return float(value)

def load_data(file_path):
    """Carga y preprocesa los datos"""
    data = pd.read_json(file_path)
    
    # Limpiar columnas monetarias
    monetary_columns = ['COSTO_MANO_DE_OBRA', 'COSTO_ACPM', 'VALOR_PEAJES', 
                       'ALOJAM', 'DIVERSOS', 'FLETE']
    
    for col in monetary_columns:
        if col in data.columns:
            data[col] = data[col].apply(lambda x: clean_monetary_value(x) if pd.notnull(x) else 0)
    
    # Convertir columnas de tiempo
    time_columns = ['TIEMPO_EN_EL_VIAJE', 'HORAS_MOTOR', 'TIEMPO_DE_CARGUE', 'TIEMPO_MUERTO']
    for col in time_columns:
        if col in data.columns:
            data[col] = pd.to_timedelta(data[col])
    
    return data

def create_dashboard(data):
    st.title('Dashboard de Control de Flota de Transporte')
    
    # Sidebar con filtros
    st.sidebar.header('Filtros')
    
    # Filtro de fecha
    if 'FECHA' in data.columns:
        fechas = sorted(data['FECHA'].unique())
        fecha_seleccionada = st.sidebar.multiselect('Seleccionar Fechas', fechas, default=fechas)
        data_filtered = data[data['FECHA'].isin(fecha_seleccionada)]
    else:
        data_filtered = data
    
    # Filtro de rutas
    if 'ORIGEN' in data.columns and 'DESTINO' in data.columns:
        rutas = sorted(data['ORIGEN'].unique())
        ruta_seleccionada = st.sidebar.multiselect('Seleccionar Origen', rutas, default=rutas[0])
        data_filtered = data_filtered[data_filtered['ORIGEN'].isin(ruta_seleccionada)]

    # KPIs principales
    st.header('KPIs Principales')
    col1, col2, col3 = st.columns(3)
    
    # KPI 1: Consumo promedio de combustible
    with col1:
        if 'CONSUMO_ACPM' in data_filtered.columns and 'DISTANCIA_RECORRIDA' in data_filtered.columns:
            consumo_promedio = (data_filtered['CONSUMO_ACPM'] / data_filtered['DISTANCIA_RECORRIDA']).mean()
            st.metric(label="Consumo ACPM/Km", 
                     value=f"{consumo_promedio:.2f} L/Km")
    
    # KPI 2: Costo promedio por kilómetro
    with col2:
        if 'COSTO_ACPM' in data_filtered.columns and 'DISTANCIA_RECORRIDA' in data_filtered.columns:
            costo_km = (data_filtered['COSTO_ACPM'] / data_filtered['DISTANCIA_RECORRIDA']).mean()
            st.metric(label="Costo por Km", 
                     value=f"${costo_km:,.2f}")
    
    # KPI 3: Distancia promedio por viaje
    with col3:
        if 'DISTANCIA_RECORRIDA' in data_filtered.columns:
            dist_promedio = data_filtered['DISTANCIA_RECORRIDA'].mean()
            st.metric(label="Distancia Promedio/Viaje", 
                     value=f"{dist_promedio:,.0f} Km")

    # Gráficos
    st.header('Análisis Detallado')
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de consumo de combustible por ruta
        if 'CONSUMO_ACPM' in data_filtered.columns and 'ORIGEN' in data_filtered.columns:
            consumo_por_ruta = data_filtered.groupby('ORIGEN')['CONSUMO_ACPM'].mean()
            fig = px.bar(consumo_por_ruta, 
                        title='Consumo Promedio de ACPM por Origen',
                        labels={'value': 'Consumo ACPM (L)', 'ORIGEN': 'Origen'})
            st.plotly_chart(fig)
    
    with col2:
        # Gráfico de costos
        if 'COSTO_ACPM' in data_filtered.columns and 'ORIGEN' in data_filtered.columns:
            costos_por_ruta = data_filtered.groupby('ORIGEN')['COSTO_ACPM'].mean()
            fig = px.bar(costos_por_ruta,
                        title='Costo Promedio por Origen',
                        labels={'value': 'Costo ($)', 'ORIGEN': 'Origen'})
            st.plotly_chart(fig)
    
    # Tabla de detalles
    st.header('Detalles de Viajes')
    columns_to_show = ['FECHA', 'ORIGEN', 'DESTINO', 'DISTANCIA_RECORRIDA', 
                      'CONSUMO_ACPM', 'COSTO_ACPM']
    st.dataframe(data_filtered[columns_to_show])

# Función principal
def main():
    st.set_page_config(page_title='Control de Flota', layout='wide')
    
    file_path = r"C:\Veronica\2-2024\sw2\2Parcial\Parcial-2\dataset.json"
    try:
        data = load_data(file_path)
        create_dashboard(data)
    except Exception as e:
        st.error(f'Error al cargar los datos: {str(e)}')

if __name__ == "__main__":
    main()