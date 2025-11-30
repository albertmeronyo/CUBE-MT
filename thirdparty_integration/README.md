

# Integrating a Third-Party Dataset into the CUBE-MT Pipeline

This repository demonstrates how to integrate **third-party datasets** (e.g., Muse-IT) into the CUBE-MT pipeline.

---

## Overview

The integration process involves two main steps:

1. **Convert the raw third-party dataset** into a format compatible with the CUBE-MT template.
2. **Retrieve missing Wikidata Q-IDs** (for entities such as artworks or artists) to enrich the dataset.

---

## Step 1: Data Conversion

Convert the third-party dataset (e.g., *Muse-IT* raw data) into the CUBE-MT-compatible template format.

* Use `process_data.py` along with `constants.py`, which defines the expected template structure.
* Input: `raw_data` from the third-party source
* Output: JSON file formatted for CUBE-MT (e.g., `muse_no_qids_cube_mt.json`)

Example command:

```bash
python process_data.py
```

This will generate a structured JSON file compatible with the CUBE-MT pipeline.

---

## Step 2: Enrich Dataset with Wikidata Q-IDs

Use the **`get_q_ids.ipynb`** notebook (or its Python equivalent) to replace missing Q-IDs in your dataset by traversing **Wikidata**.

### 2.1. Configure the User Agent

Before running, open `get_q_ids.ipynb` and replace the placeholder email address in the following line:

```python
USER_AGENT = "WikidataImageDownloader/1.0 (mailto:<your_email@example.com>)"
```

with your own email:

```python
USER_AGENT = "WikidataImageDownloader/1.0 (mailto:your_email@example.com)"
```

> **Note:** A valid email is required by Wikidata API policy for responsible API usage.

### 2.2. Input Files

Ensure the following files exist in your working directory:

* `raw_muse_data.json` — The original raw data.
* `muse_no_qids_cube_mt.json` — The processed file from Step 1.

### 2.3. Run the Notebook
Run the notebook to get q-ids

```bash
jupyter notebook get_q_ids.ipynb
```

### 2.4. What the Script Does

The script:

* Reads your processed dataset (`muse_no_qids_cube_mt.json`)
* Generates search queries combining artwork titles and artist names
* Uses the **Wikidata API** to find entities and extract:

  * `QID` (unique Wikidata identifier)
  * `P31` – *Instance of*
  * `P495` – *Country of origin*
* Updates the dataset with the retrieved values (or `"nan"` if unavailable)

Example console output:

```
Searching for: "Mona Lisa by Leonardo da Vinci"
Found: Mona Lisa (Q12418)
Entity Information:
  QID: Q12418
  Instance of: painting (Q3305213)
  Country of origin: Italy (Q38)
Processed 1/100: Mona Lisa by Leonardo da Vinci -> Q12418
```

---

## Final Output

The enriched dataset will be saved as a JSON file (e.g., `muse_with_qids.json`) containing updated `id`, `P31`, and `P495` fields for each entity.

Example record:

```json
{
  "title": "Mona Lisa",
  "artistName": "Leonardo da Vinci",
  "id": "Q12418",
  "P31": "Q3305213",
  "P495": "Q38"
}
```

---

## Summary

| Step  | Description                                      | Input                       | Output                                      |
| ----- | ------------------------------------------------ | --------------------------- | ------------------------------------------- |
| **1** | Convert third-party raw data into CUBE-MT format | `raw_data`                  | `muse_no_qids_cube_mt.json`                 |
| **2** | Replace missing Q-IDs using Wikidata API         | `muse_no_qids_cube_mt.json` | Enriched JSON with `QID`, `P31`, and `P495` |

---

## References

* [Wikidata API Documentation](https://www.wikidata.org/w/api.php)
