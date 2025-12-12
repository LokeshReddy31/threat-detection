from flask import Flask, request, jsonify
import xgboost as xgb
import pandas as pd

app = Flask(__name__)

# Load model
model = xgb.XGBClassifier()
model.load_model("baseline_xgb_model.json")

# Load feature names from processed dataset
df = pd.read_csv("preprocessed_data_baseline.csv")
feature_columns = [c for c in df.columns if c != "label"]

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        features = data["features"]

        # Create input row exactly matching training columns
        df_input = pd.DataFrame([features], columns=feature_columns)

        pred = int(model.predict(df_input)[0])
        prob = float(model.predict_proba(df_input)[0][1])

        return jsonify({
            "prediction": pred,
            "probability": prob
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
