import pickle

with open("recommender_model.pkl", "rb") as f:
    model_data = pickle.load(f)

print("\n=== Model Data Type ===")
print(type(model_data))

print("\n=== Model Contents ===")
if isinstance(model_data, dict):
    print("Keys:", model_data.keys())
else:
    print(model_data)
