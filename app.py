from flask import Flask, render_template, request
import joblib
import pandas as pd
from arboldedescisiones import df_encoded

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/datos')
def datos():
    return render_template('datos.html')
@app.route('/modelo')
def modelo():
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
