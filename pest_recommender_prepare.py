# pest_recommender_prepare.py
import pandas as pd
import os

# Path where MySQL exported the CSV
input_path = r"C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/recsys_interactions_with_headers.csv"

# Output directory inside your project
output_path = os.path.join(os.getcwd(), "trained_models", "recsys_interactions_cleaned.csv")

print("📂 Loading data from:", input_path)
df = pd.read_csv(input_path)

print("\n✅ Original data:")
print(df.head())

# Basic cleaning
df = df.drop_duplicates(subset=["user_id", "item_id"])
df = df.fillna({
    "rating": 5,
    "event_type": "purchase",
    "source": "taxinvoiceitem"
})

# Convert timestamp column to datetime if not already
df["ts"] = pd.to_datetime(df["ts"], errors="coerce")

# Sort and reset index
df = df.sort_values(by=["user_id", "ts"]).reset_index(drop=True)

print("\n🧹 Cleaned Data Info:")
print(df.info())

print("\n💾 Saving cleaned dataset to:", output_path)
df.to_csv(output_path, index=False)

print("\n✅ Data preparation complete! Cleaned file saved to:")
print(output_path)
