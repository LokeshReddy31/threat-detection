### Cloud-Based AI Threat Detection Pipeline on AWS (UNSW-NB15 + XGBoost)

This repository implements a fully reproducible, end-to-end cybersecurity threat detection system. It is split into two parts so graders can verify correctness locally first, then reproduce the full AWS cloud pipeline with logs, alarms, and email alerts.

Components

- Local baseline — Flask inference API with full ML evaluation and latency/load benchmarking
- AWS cloud pipeline — S3 → Lambda → SageMaker Endpoint → SNS Email + CloudWatch + Autoscaling
- Offline analysis — SHAP explainability and Isolation Forest anomaly detection

objective: clone the repo, run the local baseline immediately, then follow the AWS steps to reproduce CloudWatch logs, alarms, and SNS email notifications.

---

Repository Structure

Cloud_project/
├── README.md
│
├── local_baseline/
│ ├── app.py
│ ├── test_baseline.py
│ ├── latency_test.py
│ ├── load_test.py
│ ├── evaluate_baseline.py
│ ├── baseline_xgb_model.json
│ └── preprocessed_data_baseline.csv
│
└── aws_pipeline/
├── aws_preprocessing_training.ipynb
├── test_event.csv
└── predictions_part_0.txt

---

## Part A — Local Baseline (Immediate Reproducibility)

### Environment Setup

```bash
conda create -n cloud python=3.10 -y
conda activate cloud
pip install flask xgboost pandas numpy scikit-learn requests
```

### Run Flask inference API

```bash
cd local_baseline
python app.py
```

### Expected output

```bash
Running on http://127.0.0.1:5000
```

### Run evaluation & performance tests (new terminal)

```bash
cd local_baseline
python evaluate_baseline.py
python test_baseline.py
python latency_test.py
python load_test.py
```

### Outputs

- Accuracy, Precision, Recall, F1-score, ROC-AUC
- Latency statistics (average, p95, max)
- Throughput under load

---

## Part B — AWS Cloud Pipeline (Notebook + AWS Managed Services)

All AWS functionality for this project is implemented using a **single notebook**
(`aws_preprocessing_training.ipynb`) in combination with **AWS-managed services**
configured via the AWS Console and SDKs.

This reflects real-world AWS workflows, where infrastructure such as Lambda,
SNS, CloudWatch alarms, and autoscaling policies are managed services rather
than standalone code files.

---

### SageMaker Endpoint Verification

After deployment, the SageMaker real-time endpoint can be verified using:

```bash
aws sagemaker describe-endpoint --endpoint-name unsw-xgb-endpoint
```

This confirms the endpoint is InService and ready to receive inference requests.

### Lambda Configuration (S3 → SageMaker → SNS)

AWS Lambda is configured directly in the AWS Console and is triggered automatically by S3 upload events.

### Required IAM Permissions

The Lambda execution role includes:

- s3:GetObject
- sagemaker:InvokeEndpoint
- sns:Publish
- logs:CreateLogGroup
- logs:CreateLogStream
- logs:PutLogEvents

These permissions allow Lambda to read traffic data, invoke the model,
send alerts, and log execution details.

---

### Lambda Environment Variables

Configured in the AWS Console:

```bash
ENDPOINT_NAME=unsw-xgb-endpoint
SNS_TOPIC_ARN=arn:aws:sns:REGION:ACCOUNT_ID:threat-alerts-topic
THRESHOLD=50
AWS_REGION=us-east-1
```

- THRESHOLD=50 defines the alert boundary for malicious traffic
- Scores ≥ 50 trigger an SNS email alert

### S3 Trigger Configuration

The Lambda function is triggered automatically by S3 upload events:

- Bucket: msml650-project
- Prefix: incoming-events/
- Event type: PUT

Any CSV uploaded to this prefix initiates the inference pipeline.

### Triggering a Demo Prediction

A single unseen network traffic flow can be tested by uploading an unlabeled CSV file (no header, no index):

```python
import boto3

s3 = boto3.client("s3")
s3.upload_file(
    "test_event.csv",
    "msml650-project",
    "incoming-events/test_event.csv"
)
```

This upload automatically triggers:
S3 → Lambda → SageMaker Endpoint → SNS + CloudWatch

---

### Verification Checklist

#### CloudWatch Logs

- Lambda reads the S3 CSV file
- SageMaker endpoint is invoked
- Threat probability and normalized score (0–100) are logged

#### SNS Email Alerts

- Email notification received when threat score ≥ 50
- No alert sent for scores below threshold

#### SageMaker Endpoint Metrics

- Invocation count
- Latency metrics
- Error rates
- Visible in both SageMaker and CloudWatch

---

### Autoscaling (Configured via AWS APIs)

Autoscaling is enabled for the SageMaker real-time endpoint using Application Auto Scaling, configured either through SDK calls inside the notebook or the AWS Console.

#### Autoscaling Policy

- MinCapacity: 1
- MaxCapacity: 2
- Metric: SageMakerVariantInvocationsPerInstance
- Target value: 50

#### CloudWatch Alarms (Auto-Created)

- AlarmHigh: scales up when traffic exceeds target
- AlarmLow: scales down when traffic decreases

This ensures low latency under load and cost efficiency during idle periods.

---

### Explainability & Anomaly Detection (Offline Analysis)

These analyses are executed offline and documented in the report.

#### SHAP (Explainability)

- Global SHAP summary plot:
  - Identifies top features influencing predictions
- Local SHAP waterfall plots:
  - Explains why individual traffic flows are classified as malicious or benign

#### Isolation Forest (Anomaly Detection)

- Trained only on benign traffic
- Flags rare or unusual network patterns
- Designed to detect potential zero-day or unseen attacks

### Performance Summary

- Local baseline latency: ~39.5 ms
- AWS SageMaker latency: ~12.5 ms
- Observed speedup: ~3.16×

This performance gain is infrastructure-driven and reproducible.

Dataset: UNSW-NB15 Intrusion Detection Dataset
