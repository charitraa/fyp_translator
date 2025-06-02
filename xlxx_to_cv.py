import pandas as pd

# Load the Excel file
df = pd.read_excel("english-nepali.xlsx")

# Rename columns (adjust if needed)
df.columns = ['english', 'nepali']

# Drop rows with missing values
df = df.dropna()

# Save as CSV
df.to_csv("english-nepali.csv", index=False)
print("✅ Saved as english-nepali.csv")

