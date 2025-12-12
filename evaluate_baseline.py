import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report
from sklearn.model_selection import train_test_split

# Load data
df = pd.read_csv("preprocessed_data_baseline.csv")
X = df.drop(columns=["label"])
y = df["label"]

# Same split as training
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Load model
model = xgb.XGBClassifier()
model.load_model("baseline_xgb_model.json")

# Safety check
model_features = model.get_booster().feature_names
if model_features != X.columns.tolist():
    print("\n WARNING: Feature mismatch between model and dataset!\n")

# Predict
y_scores = model.predict_proba(X_test)[:, 1]
y_pred = (y_scores > 0.5).astype(int)

print("\n==== BASELINE MODEL PERFORMANCE ====")
print(f"Accuracy : {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall   : {recall_score(y_test, y_pred):.4f}")
print(f"F1-score : {f1_score(y_test, y_pred):.4f}")
print(f"ROC-AUC  : {roc_auc_score(y_test, y_scores):.4f}")
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))
