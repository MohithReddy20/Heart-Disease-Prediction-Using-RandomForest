import pandas as pd
import numpy as np
import pickle
import warnings
warnings.filterwarnings("ignore")
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, recall_score, roc_auc_score, classification_report, confusion_matrix

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve

# Optional: XGBoost (install if needed)
try:
    from xgboost import XGBClassifier
    xgb_available = True
except:
    xgb_available = False   


# ---------------- LOAD DATA ----------------
data = pd.read_csv("/home/mohithreddy/Desktop/heart-disease-prediction-using-machine-learning-with-flask-main/Heart_Disease_Prediction.csv")

# ---------------- BASE FEATURES ----------------
base_features = [
    "Age",
    "Chest pain type",
    "BP",
    "Cholesterol",
    "Max HR",
    "ST depression",
    "Number of vessels fluro",
    "Thallium"
]

X = data[base_features]

# ---------------- FEATURE ENGINEERING ----------------
X["Chol_Age_Ratio"] = X["Cholesterol"] / X["Age"]
X["Heart_Stress"] = X["ST depression"] * X["BP"]

# ---------------- FINAL FEATURE LIST ----------------
feature_columns = base_features + [
    "Chol_Age_Ratio",
    "Heart_Stress"
]

y = data["Heart Disease"].map({
    "Absence": 0,
    "Presence": 1
})

# ---------------- TRAIN TEST SPLIT ----------------
x_train, x_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ---------------- DEFINE MODELS ----------------
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    
    "Random Forest": RandomForestClassifier(
        n_estimators=600,
        max_depth=10,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42
    )
}

if xgb_available:
    models["XGBoost"] = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric='logloss',
        random_state=42
    )


# ---------------- TRAIN & EVALUATE ----------------
results = []

print("\n========== MODEL COMPARISON ==========\n")

for name, model in models.items():
    print(f"Training {name}...")

    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)
    y_prob = model.predict_proba(x_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)

    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Recall": recall,
        "ROC-AUC": roc_auc,
        "Model_Object": model
    })

    print(f"\n{name} Results:")
    print("Accuracy:", round(accuracy, 4))
    print("Recall:", round(recall, 4))
    print("ROC-AUC:", round(roc_auc, 4))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    print("-" * 40)


# ---------------- SELECT BEST MODEL ----------------
# Priority: Recall → ROC-AUC → Accuracy

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by=["Recall", "ROC-AUC", "Accuracy"],
    ascending=False
)

best_model_row = results_df.iloc[0]
best_model = best_model_row["Model_Object"]

print("\n========== FINAL MODEL SELECTION ==========\n")
print(results_df[["Model", "Accuracy", "Recall", "ROC-AUC"]])

print(f"\nBest Model Selected: {best_model_row['Model']}")
print(f"Reason: Highest Recall prioritized (medical safety)")

# ---------------- FINAL MODEL EVALUATION VISUALS ----------------

print("\n========== FINAL MODEL EVALUATION ==========\n")

# Re-predict using best model
y_pred = best_model.predict(x_test)
y_prob = best_model.predict_proba(x_test)[:, 1]

# ---- CONFUSION MATRIX PLOT ----
cm = confusion_matrix(y_test, y_pred)

plt.figure()
plt.imshow(cm)
plt.title("Confusion Matrix")
plt.xlabel("Predicted (0=No Disease, 1=Disease)")
plt.ylabel("Actual (0=No Disease, 1=Disease)")

for i in range(len(cm)):
    for j in range(len(cm[0])):
        plt.text(j, i, cm[i, j], ha='center', va='center')

plt.colorbar()
plt.tight_layout()
plt.savefig("confusion_matrix.png")
plt.show()


# ---- ROC CURVE PLOT ----
fpr, tpr, _ = roc_curve(y_test, y_prob)

plt.figure()
plt.plot(fpr, tpr, label=f"AUC = {roc_auc_score(y_test, y_prob):.3f}")
plt.plot([0, 1], [0, 1], linestyle='--')
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend()
plt.tight_layout()
plt.savefig("roc_curve.png")
plt.show()


# ---- FINAL METRICS PRINT ----
print("Final Model Metrics:")
print("Recall:", round(recall_score(y_test, y_pred), 4))
print("ROC-AUC:", round(roc_auc_score(y_test, y_prob), 4))

# ---------------- FEATURE IMPORTANCE (INTERPRETABILITY) ----------------

print("\n========== FEATURE IMPORTANCE ==========\n")

# Only works meaningfully for Logistic Regression
if best_model_row["Model"] == "Logistic Regression":
    
    feature_names = X.columns
    importance = best_model.coef_[0]

    feature_importance = pd.DataFrame({
        "Feature": feature_names,
        "Importance": importance
    })

    # Sort by absolute impact
    feature_importance["Abs_Importance"] = feature_importance["Importance"].abs()
    feature_importance = feature_importance.sort_values(
        by="Abs_Importance",
        ascending=False
    )

    print("Top Influential Features:\n")

    for i, row in feature_importance.head(5).iterrows():
        direction = "increases risk" if row["Importance"] > 0 else "decreases risk"
        print(f"{row['Feature']} → {direction}")

else:
    print("Feature importance available only for Logistic Regression model.")

# ---------------- SAVE BEST MODEL ----------------
with open("heartdiseaseprediction.model", "wb") as f:
    pickle.dump(best_model, f)

print("\nBest model saved successfully.")