import os
import joblib
import psycopg2
import pandas as pd

import torch
import torch.nn as nn
import torch.nn.functional as F

from flask import Flask, request, render_template

app = Flask(__name__)

db_parameters = {
    'database': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'port': os.environ.get('DB_PORT')
}

# Pripojenie k databáze
conn = psycopg2.connect(**db_parameters)


# Vytvorenie modelu na klasifikáciu
class Net(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


# Načítanie modelu
model = Net(input_size=6, hidden_size=16, output_size=2)
model.load_state_dict(torch.load('misc/model.pth'))
model.eval()

# Načítanie scaler-u pre normalizáciu dát
scaler = joblib.load('./misc/scaler.pkl')

actual_labels = []
predicted_labels = []
correct_predictions = []
incorrect_predictions = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/form', methods=['GET', 'POST'])
def predict_form():
    prediction_result = None

    if request.method == 'POST':
        form_result = request.form

        # Extrakcia hodnôt z formulára
        age = float(form_result['age'])
        bmi = float(form_result['bmi'])
        hba1c_level = float(form_result['HbA1c_level'])
        blood_glucose_level = float(form_result['blood_glucose_level'])

        # Keďže checkbox-y vracajú číselnú hodnotu, je potrebné ich pretypovať na bool
        hypertension = True if 'hypertension' in form_result else False
        heart_disease = True if 'heart_disease' in form_result else False

        # Vytvorenie dataframe-u zo získaných hodnôt
        features = pd.DataFrame({
            'age': [age],
            'hypertension': [hypertension],
            'heart_disease': [heart_disease],
            'bmi': [bmi],
            'HbA1c_level': [hba1c_level],
            'blood_glucose_level': [blood_glucose_level]
        })

        # Normalizácia dát
        scaled_features = scaler.transform(features)

        # Konvertovanie na tensor
        input_tensor = torch.tensor(scaled_features).float()

        # Predikcia
        with torch.no_grad():
            outputs = model(input_tensor)
            _, predicted = torch.max(outputs, 1)
            prediction_result = predicted.item()

        # Konvertovanie na bool
        prediction_result = True if prediction_result == 1 else False

        # Uloženie dát do databázy
        cur = conn.cursor()

        cur.execute("SELECT MAX(id) FROM user_data")
        max_id = cur.fetchone()[0]

        id = 1 if max_id is None else max_id + 1
        cur.execute(
            "INSERT INTO user_data (id, age, hypertension, heart_disease, bmi, hba1c, glucose_level, predict, submitted) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TO_CHAR(CURRENT_TIMESTAMP AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI'))",
            (id, age, hypertension, heart_disease, bmi, hba1c_level, blood_glucose_level, prediction_result))
        conn.commit()
        cur.close()

    return render_template('form.html', prediction_result=prediction_result)


@app.route('/data')
def display_data():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_data;")
    data = cursor.fetchall()
    return render_template('data.html', data=data)
