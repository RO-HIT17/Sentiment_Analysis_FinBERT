import os

model_path = r"C:\Rohit\Projects\Fintech\sentiment_analysis_for_business\fine_tuned_bert"
try:
    if os.access(model_path, os.R_OK):
        print(f"Directory is readable: {model_path}")
        print("Files:", os.listdir(model_path))
    else:
        print(f"Cannot read directory: {model_path}")
except PermissionError as e:
    print(f"PermissionError: {e}")
