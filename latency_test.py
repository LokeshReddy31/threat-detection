import requests
import time
import pandas as pd

# Load real sample
df = pd.read_csv("preprocessed_data_baseline.csv")
X = df.drop(columns=["label"])
sample = X.iloc[0].tolist()

def measure_latency():
    payload = {"features": sample}
    start = time.time()

    r = requests.post(
        "http://127.0.0.1:5000/predict",
        json=payload,
        timeout=5
    )

    end = time.time()

    if r.status_code != 200:
        print("Server Error:", r.status_code, r.text)

    return end - start

latencies = []

for i in range(30):
    lat = measure_latency()
    latencies.append(lat)
    print(f"Request {i+1}: {lat:.4f} seconds")

print("\nAverage Latency:", sum(latencies)/len(latencies))
