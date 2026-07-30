from backend.datacollection.climate import get_climate_data
from preprocessing.feature_engineering import add_features
from models.drought_model import train_model

# Step 1: Get data
df = get_climate_data()

# Step 2: Add missing feature (IMPORTANT)
df['ndvi'] = 0.5

# Step 3: Feature engineering
df = add_features(df)

# Step 4: Train model
model, metrics = train_model(df)

print("Model trained successfully!")
print(metrics)