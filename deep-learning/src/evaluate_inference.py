import os
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from src.inference import predict


# ---------------------------------------
# Paths
# ---------------------------------------

TEST_DIR = r"C:\Users\vu241\OneDrive\Desktop\Diabetic-Retinopathy-Screening\Disease Dataset\B. Disease Grading\1. Original Images\b. Testing Set"

LABEL_FILE = r"C:\Users\vu241\OneDrive\Desktop\Diabetic-Retinopathy-Screening\Disease Dataset\B. Disease Grading\2. Groundtruths\b. IDRiD_Disease Grading_Testing Labels.csv"


# ---------------------------------------
# Load labels
# ---------------------------------------

df = pd.read_csv(LABEL_FILE)

df.columns = df.columns.str.strip()


# ---------------------------------------
# Run inference
# ---------------------------------------

y_true = []
y_pred = []

results = []


for _, row in df.iterrows():

    image_name = row["Image name"]
    actual_grade = int(row["Retinopathy grade"])

    image_path = os.path.join(
        TEST_DIR,
        image_name + ".jpg"
    )

    result = predict(image_path)

    predicted_grade = result["predicted_grade"]

    y_true.append(actual_grade)
    y_pred.append(predicted_grade)

    results.append({
        "image": image_name,
        "actual": actual_grade,
        "predicted": predicted_grade,
        "confidence": result["confidence"],
        "risk": result["risk_level"],
        "doctor_review": result["doctor_review_required"]
    })


# ---------------------------------------
# Metrics
# ---------------------------------------

accuracy = accuracy_score(
    y_true,
    y_pred
)

print("\n======================================")
print("       RETINA-XAI FULL EVALUATION")
print("======================================")

print(
    f"\nAccuracy: {accuracy * 100:.2f}%"
)

print("\nClassification Report:")
print(
    classification_report(
        y_true,
        y_pred,
        target_names=[
            "No DR",
            "Mild",
            "Moderate",
            "Severe",
            "Proliferative"
        ],
        zero_division=0
    )
)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        y_true,
        y_pred
    )
)


# ---------------------------------------
# Save results
# ---------------------------------------

results_df = pd.DataFrame(results)

results_df.to_csv(
    "outputs/inference_results.csv",
    index=False
)

print(
    "\nResults saved to:"
    "\noutputs/inference_results.csv"
)