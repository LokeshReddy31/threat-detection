import requests
import pandas as pd

df = pd.read_csv("preprocessed_data_baseline.csv")
X = df.drop(columns=["label"])

sample = X.iloc[0].tolist()
payload = {"features": sample}

try:
    response = requests.post(
        "http://127.0.0.1:5000/predict",
        json=payload,
        timeout=5
    )

    print("Status:", response.status_code)

    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("❌ ERROR:", response.text)

except Exception as e:
    print("❌ Exception:", e)
