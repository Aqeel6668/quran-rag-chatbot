from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).parent / "data" / "quran.csv"
REQUIRED_COLUMNS = {
    "surah", "ayah", "arabic_text", "english_translation", "footnotes"
}
EXPECTED_AYAHS = 6236


def load_quran(path=DATA_PATH):
    """Load and validate the complete Arabic + English Quran CSV."""
    if not Path(path).exists():
        raise FileNotFoundError(
            "Quran dataset not found. Run `python download_quran.py` first."
        )

    df = pd.read_csv(path, encoding="utf-8-sig")
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

    df = df.dropna(subset=["surah", "ayah", "arabic_text", "english_translation"])
    df["surah"] = df["surah"].astype(int)
    df["ayah"] = df["ayah"].astype(int)
    df["arabic_text"] = df["arabic_text"].astype(str)
    df["english_translation"] = df["english_translation"].astype(str)
    df["footnotes"] = df["footnotes"].fillna("").astype(str)

    keys = list(zip(df["surah"], df["ayah"]))
    if len(df) != EXPECTED_AYAHS or len(set(keys)) != EXPECTED_AYAHS:
        raise ValueError(
            f"Expected {EXPECTED_AYAHS} unique Quran ayahs; found {len(df)}. "
            "Run `python download_quran.py` to download the complete dataset."
        )

    return df.to_dict(orient="records")
