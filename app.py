from flask import Flask, render_template, request, send_from_directory
import joblib
import pandas as pd
from arboldedescisiones import df_encoded
import os
from datetime import datetime

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/datos')
def datos():
    return render_template('datos.html')
@app.route('/ingmodelo')
def ingmodelo():
    return render_template('ingenieriamodelo.html')
@app.route('/evmodelo')
def evmodelo():
    return render_template('modelo.html')

@app.route("/arboldescisiones", methods=["GET", "POST"])
def arboldesiciones():
    resultado = None
    if request.method == "POST":
        lugar = request.form["lugar"]
        sexo = request.form["sexo"]
        edad = int(request.form["edad"])
        peso = float(request.form["peso"])
        altura = float(request.form["altura"])
        imc = peso / (altura / 100) ** 2

        # Crear el mismo tipo de input que usó el modelo
        input_dict = {col: 0 for col in df_encoded.columns}
        input_dict[f"Lugar_{lugar}"] = 1
        input_dict[f"Sexo_{sexo}"] = 1

        input_df = pd.DataFrame([input_dict])
        input_df["Edad"] = edad
        input_df["IMC"] = imc

        model = joblib.load("modelo_arbol.pkl")
        resultado = model.predict(input_df)[0]

    return render_template("arboldescisiones.html", resultado=resultado)



@app.route("/analizar_archivo", methods=["POST"])
def analizar_archivo():
    archivo = request.files["archivo"]

    if not archivo:
        return render_template("arboldescisiones.html", resultado="No se cargó ningún archivo.")

    try:
        if archivo.filename.endswith(".csv"):
            df = pd.read_csv(archivo)
        elif archivo.filename.endswith(".xlsx"):
            df = pd.read_excel(archivo)
        else:
            return render_template("arboldescisiones.html", resultado="Formato no soportado.")

        required_columns = {"Lugar", "Sexo", "Edad", "Peso", "Altura"}
        if not required_columns.issubset(set(df.columns)):
            return render_template("arboldescisiones.html", resultado="El archivo debe tener las columnas: Lugar, Sexo, Edad, Peso, Altura.")

        df["IMC"] = df["Peso"] / (df["Altura"] / 100) ** 2

        input_df = pd.get_dummies(df[["Lugar", "Sexo"]])
        for col in df_encoded.columns:
            if col not in input_df.columns:
                input_df[col] = 0

        input_df = input_df[df_encoded.columns]
        input_df["Edad"] = df["Edad"]
        input_df["IMC"] = df["IMC"]

        model = joblib.load("modelo_arbol.pkl")
        resultados = model.predict(input_df)
        df["EstadoNutricional"] = resultados

        # Guardar archivo Excel con resultados
        nombre_archivo = f"resultado_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        ruta_guardado = os.path.join("resultados", nombre_archivo)
        os.makedirs("resultados", exist_ok=True)
        df.to_excel(ruta_guardado, index=False)

        resultado_html = df[["Lugar", "Sexo", "Edad", "Peso", "Altura", "EstadoNutricional"]].to_html(classes="table table-dark table-striped", index=False)

        return render_template("arboldescisiones.html", resultado_tabla=resultado_html, archivo_procesado=nombre_archivo)

    except Exception as e:
        return render_template("arboldescisiones.html", resultado=f"Ocurrió un error: {str(e)}")



@app.route('/descargar_resultado/<nombre_archivo>')
def descargar_resultado(nombre_archivo):
    return send_from_directory('resultados', nombre_archivo, as_attachment=True)

@app.route('/pcga')
def pcga():
    return render_template('pcga.html')
