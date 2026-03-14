import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import pickle

# Load dataset
data = pd.read_csv("Heart_Disease_Prediction.csv")

print("Missing values:\n", data.isnull().sum())

feature_columns = [
    "Age",
    "Chest pain type",
    "BP",
    "Cholesterol",
    "Max HR",
    "ST depression",
    "Number of vessels fluro",
    "Thallium"
]

X = data[feature_columns]
y = data["Heart Disease"]

# Check chest pain encoding
print("\nChest pain unique values:", data["Chest pain type"].unique())

# Split
x_train, x_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Model
model = RandomForestClassifier(
    n_estimators=600,
    max_depth=10,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42
)

model.fit(x_train, y_train)

# Evaluation
y_pred = model.predict(x_test)
y_prob = model.predict_proba(x_test)[:, 1]

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:\n")
print(confusion_matrix(y_test, y_pred))

print("\nROC AUC Score:", roc_auc_score(y_test, y_prob))

print("\nClasses:", model.classes_)
print(data.groupby("Chest pain type")["Heart Disease"].value_counts())
print(data.groupby("Thallium")["Heart Disease"].value_counts())

# Save ONLY the model
with open("heartdiseaseprediction.model", "wb") as f:
    pickle.dump(model, f)

print("\nModel saved successfully.")
