"""Download the complete Uthmani Arabic Quran and Sahih International English translation.

Sources:
- Arabic: AlQuran Cloud, edition quran-uthmani
- English: AlQuran Cloud, edition en.sahih (Saheeh International)
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = "https://api.alquran.cloud/v1/quran"
ARABIC_EDITION = "quran-uthmani"
ENGLISH_EDITION = "en.sahih"
OUTPUT_PATH = Path(__file__).parent / "data" / "quran.csv"
EXPECTED_AYAHS = 6236


def fetch_edition(edition: str) -> dict:
    url = f"{BASE_URL}/{edition}"
    request = Request(
        url,
        headers={"User-Agent": "Quran-RAG-Educational-Project/2.0", "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Could not download edition '{edition}' from {url}: {exc}") from exc

    if not isinstance(payload, dict) or payload.get("code") != 200:
        raise RuntimeError(f"API returned an unsuccessful response for edition '{edition}'.")
    data = payload.get("data")
    if not isinstance(data, dict) or not isinstance(data.get("surahs"), list):
        raise RuntimeError(f"Unexpected API response for edition '{edition}': missing data.surahs.")
    return data


def flatten_edition(data: dict, edition_name: str) -> dict[tuple[int, int], str]:
    result: dict[tuple[int, int], str] = {}
    for surah in data["surahs"]:
        surah_number = int(surah["number"])
        for ayah in surah.get("ayahs", []):
            key = (surah_number, int(ayah["numberInSurah"]))
            text = ayah.get("text")
            if not text:
                raise RuntimeError(f"Missing {edition_name} text at {key[0]}:{key[1]}.")
            if key in result:
                raise RuntimeError(f"Duplicate {edition_name} reference {key[0]}:{key[1]}.")
            result[key] = str(text)
    return result


def main() -> None:
    print("Downloading complete Uthmani Arabic Quran...")
    arabic_data = fetch_edition(ARABIC_EDITION)
    arabic = flatten_edition(arabic_data, "Arabic")

    print("Downloading complete Sahih International English translation...")
    english_data = fetch_edition(ENGLISH_EDITION)
    english = flatten_edition(english_data, "English")

    # Build the expected references from the ayah records themselves.
    # The API response does not guarantee a `numberOfAyahs` field in each surah.
    if len(arabic_data["surahs"]) != 114:
        raise RuntimeError(
            f"Expected 114 surahs in Arabic edition; found {len(arabic_data['surahs'])}."
        )
    expected_keys = set(arabic)
    if len(expected_keys) != EXPECTED_AYAHS:
        raise RuntimeError(
            f"Arabic edition has {len(expected_keys)} unique ayahs; "
            f"expected {EXPECTED_AYAHS}."
        )
    if set(arabic) != expected_keys:
        raise RuntimeError("Arabic edition is missing or has unexpected ayah references.")
    if set(english) != expected_keys:
        missing = sorted(expected_keys - set(english))[:5]
        extra = sorted(set(english) - expected_keys)[:5]
        raise RuntimeError(f"English edition does not match Arabic references. Missing: {missing}; extra: {extra}.")

    rows = []
    for surah_number, ayah_number in sorted(expected_keys):
        rows.append({
            "surah": surah_number,
            "ayah": ayah_number,
            "arabic_text": arabic[(surah_number, ayah_number)],
            "english_translation": english[(surah_number, ayah_number)],
            "footnotes": "",
            "translation_name": "Saheeh International",
            "translation_version": str(english_data.get("edition", {}).get("version") or "Not provided by API"),
            "arabic_source": "AlQuran Cloud (quran-uthmani)",
            "english_source": "AlQuran Cloud (en.sahih; Saheeh International)",
        })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = OUTPUT_PATH.with_suffix(".tmp")
    fieldnames = [
        "surah", "ayah", "arabic_text", "english_translation", "footnotes",
        "translation_name", "translation_version", "arabic_source", "english_source",
    ]
    with temp_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    temp_path.replace(OUTPUT_PATH)

    print(f"\nSUCCESS: saved {len(rows)} verified ayahs from all 114 surahs.")
    print(f"CSV: {OUTPUT_PATH}")
    print("Arabic: Uthmani script | English: Saheeh International")
    print("Check the source terms before redistributing this dataset.")


if __name__ == "__main__":
    main()
