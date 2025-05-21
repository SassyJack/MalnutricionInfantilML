import pandas as pd
import joblib
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

# Cargar datos y preparar el modelo
file_path = "dataset_arbol_decision.csv"
df = pd.read_csv(file_path)

# Calcular el IMC
df["IMC"] = df["Peso"] / (df["Altura"] / 100) ** 2

# Clasificar estado nutricional
def clasificar_estado(imc):
    if imc < 18.5:
        return "Posible caso de Malnutrición"
    elif imc < 25:
        return "Caso Normal"
    else:
        return "Posible caso de Sobrepeso"

df["EstadoNutricional"] = df["IMC"].apply(clasificar_estado)

# Codificación de variables categóricas
df_encoded = pd.get_dummies(df[["Lugar", "Sexo"]])
df_model = pd.concat([df_encoded, df[["Edad", "IMC"]]], axis=1)
X = df_model

y = df["EstadoNutricional"]

# Entrenar el modelo
model = DecisionTreeClassifier()
model.fit(X, y)

# Guardar modelo
joblib.dump(model, "modelo_arbol.pkl")


