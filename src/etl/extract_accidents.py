"""Download US Accidents data from Kaggle."""

from pathlib import Path

import kagglehub

DATASET_HANDLE = "sobhanmoosavi/us-accidents"
RAW_DIR = Path("data/raw/")

def download_accident_data():
    """Download the raw US Accidents dataset from Kaggle."""
    try:
        RAW_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print("Error:",e)

    download_path = kagglehub.dataset_download(
        DATASET_HANDLE,
        output_dir=str(RAW_DIR)
    )

    return Path(download_path)


if __name__ == "__main__":
    path = download_accident_data()
    print("Downloaded dataset to:", path)