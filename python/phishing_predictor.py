import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.utils import resample
import os

# Load dataset
data = pd.read_csv("../python/data/dataset.csv")

# Drop 'index' column if present
if 'index' in data.columns:
    data.drop("index", axis=1, inplace=True)

# Separate features and target
X = data.drop("Result", axis=1)
y = data["Result"]

# Map labels: -1 (phishing) -> 1, 1 (safe) -> 0
y = y.map({-1: 1, 1: 0})

# Combine for resampling
df_combined = pd.concat([X, y.rename("Result")], axis=1)

# Balance classes by upsampling phishing (1)
phishing = df_combined[df_combined["Result"] == 1]
safe = df_combined[df_combined["Result"] == 0]

phishing_upsampled = resample(phishing, 
                              replace=True,
                              n_samples=len(safe),
                              random_state=42)

df_balanced = pd.concat([safe, phishing_upsampled])

# Final features and labels
X_balanced = df_balanced.drop("Result", axis=1)
y_balanced = df_balanced["Result"]

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X_balanced, y_balanced, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate the model
accuracy = accuracy_score(y_test, model.predict(X_test))
print(f"✅ Model trained! Accuracy: {accuracy:.2f}")

# Create model directory if not exists
os.makedirs("model", exist_ok=True)

# Save the model and features
joblib.dump(model, "model/phishing_model.pkl")
joblib.dump(list(X.columns), "model/feature_names.pkl")
