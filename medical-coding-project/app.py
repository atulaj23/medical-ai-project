from flask import Flask, render_template, request
import pandas as pd
import os
from fuzzywuzzy import process

app = Flask(__name__)

# -------------------------
# LOAD DATA SAFELY
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "icd_data.csv")

data = pd.read_csv(csv_path)

# clean data
data['symptom'] = data['symptom'].astype(str).str.lower().str.strip()

# -------------------------
# HOME PAGE
# -------------------------
@app.route('/')
def home():
    return render_template('index.html')

# -------------------------
# PREDICT (AI MULTI SYMPTOM)
# -------------------------
@app.route('/predict', methods=['POST'])
def predict():
    symptom_input = request.form.get('symptom', '').lower().strip()

    # 🔥 MULTI SYMPTOM SUPPORT
    symptoms = [s.strip() for s in symptom_input.split('+')]

    all_symptoms = data['symptom'].tolist()

    matched_rows = []

    # -------------------------
    # FUZZY MATCH EACH SYMPTOM
    # -------------------------
    for sym in symptoms:
        best_match = process.extractOne(sym, all_symptoms)

        if best_match and best_match[1] >= 70:
            match_symptom = best_match[0]

            row = data[data['symptom'] == match_symptom]

            if not row.empty:
                matched_rows.append(row.iloc[0])

    # -------------------------
    # RESULT PROCESSING
    # -------------------------
    if matched_rows:
        # take first best match (simple logic)
        result = matched_rows[0]

        disease = result['disease']
        icd = result['icd_code']
        cpt = result['cpt_code']

        # clean CPT
        if pd.isna(cpt) or str(cpt).strip() == "":
            cpt = "N/A"

    else:
        disease = "Not Found"
        icd = "N/A"
        cpt = "N/A"

    return render_template(
        'result.html',
        symptom=symptom_input,
        disease=disease,
        code=icd,
        cpt=cpt
    )

# -------------------------
# RUN SERVER
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)