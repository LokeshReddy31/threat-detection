import requests
import time
import pandas as pd
import statistics as stats

# Load real sample
df = pd.read_csv("preprocessed_data_baseline.csv")
X = df.drop(columns=["label"])
sample = X.iloc[0].tolist()
payload = {"features": sample}

num_requests = 200
failures = 0
latencies = []

start_time = time.time()

for i in range(num_requests):
    try:
        t1 = time.time()

        r = requests.post(
            "http://127.0.0.1:5000/predict",
            json=payload,
            timeout=5
        )

        t2 = time.time()

        if r.status_code == 200:
            latencies.append(t2 - t1)
        else:
            failures += 1
            print(f"[ERROR] Status {r.status_code} → {r.text}")

    except Exception as e:
        failures += 1
        print(f"[EXCEPTION] {str(e)}")

total_time = time.time() - start_time

if len(latencies) == 0:
    print("\n❌ No successful requests.")
    print(f"Failures: {failures}/{num_requests}")
    exit()

avg_latency = sum(latencies) / len(latencies)
p95_latency = stats.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)

print(f"Total requests: {num_requests}")
print(f"Failures: {failures}")
print(f"Average latency: {avg_latency:.4f} sec")
print(f"P95 latency: {p95_latency:.4f} sec")
print(f"Max latency: {max(latencies):.4f} sec")
print(f"Total time: {total_time:.2f} sec")
print(f"Throughput: {num_requests/total_time:.2f} req/sec")
