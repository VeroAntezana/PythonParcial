from flask import Flask, render_template, jsonify, make_response
import io
import pandas as pd
import matplotlib.pyplot as plt
from kpi_calculations import load_data, calculate_kpis
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json;charset=utf-8'
# Ruta para mostrar los KPIs en un dashboard local
@app.route("/")
def index():
    try:
        file_path = r"C:\Veronica\2-2024\sw2\2Parcial\Parcial-2\dataset_limpio.json"
        data = load_data(file_path)
        if data is None:
            raise Exception("No se pudieron cargar los datos del archivo")
        kpis = calculate_kpis(data)
        if not kpis:
            raise Exception("Error al calcular los KPIs")
        kpis_json = json.dumps(kpis)
        return render_template("dashboard.html", kpis_json=kpis_json)
    except Exception as e:
        print(f"Error en index: {str(e)}")
    # Si los datos no se cargan, usa valores estáticos como respaldo

    kpis = {
            "consumo_acpm_km": 6.3,
            "costo_combustible_viaje": 1450.80,
            "productividad_flota": 310.2,
            "costo_total_km": 9.2,
            "tiempo_promedio_viaje": 7.4,
            "Porcentaje de entrega No entregada": 5.1,
            "tiempo_por_ruta": {
            "Ruta A-B": 7.5,
            "Ruta C-D": 8.0,
            "Ruta E-F": 6.8
            },
            "tendencia_costos": {
            "2024-01": 10000,
            "2024-02": 12000,
            "2024-03": 11000,
            "2024-04": 11500,
            "2024-05": 11800,
            "2024-06": 12500
            }
        }
    # Imprime los datos enviados al HTML
    print("Datos enviados al template:", json.dumps(kpis, indent=4))
    kpis_json = json.dumps(kpis)
    return render_template("dashboard.html", kpis_json=kpis_json)



# Ruta para exponer KPIs como una API REST para Power BI
@app.route("/api/kpis", methods=["GET"])
def get_kpis():
    file_path = r"C:\Veronica\2-2024\sw2\2Parcial\Parcial-2\dataset_limpio.json"
    print(f"Intentando cargar datos desde: {file_path}")
    data = load_data(file_path)

    if data is not None:
        kpis = calculate_kpis(data)
        return jsonify(kpis)  # Retorna los KPIs como JSON para Power BI
    else:
        return jsonify({"error": "No se pudieron cargar los datos"}), 500


if __name__ == "__main__":
    app.run(debug=True)
