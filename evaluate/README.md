
# CUBE-MT: Evaluating Cultural Diversity

This repository provides code for evaluating **cultural diversity** in model outputs (images or text). The pipeline has two main steps:

1. **Compute quality scores** for each artifact (image/text) using external evaluation tools.
2. **Compute cultural diversity** using the quality scores and tagged cultural entities.


## 1. Step 1 – Get Quality Scores

We first compute a **quality score** for each item. This is done separately for images and text.

### 1.1. Images – HPSv2 Score

Notebook: **`get_hpv2_score.ipynb`**

1. Install the **HPSv2** package by following the instructions in the HPSv2 repo:
   [https://github.com/tgxs002/HPSv2](https://github.com/tgxs002/HPSv2)

2. Open `get_hpv2_score.ipynb` (e.g. with Jupyter Lab / VS Code) and:

   * Set the paths to your **generated images**.
   * Run all cells to compute the quality scores.


---

### 1.2. Text – LLM-Blender PairRM Score

Notebook: **`get_pairRM_score.ipynb`**

1. Install **LLM-Blender** by following the instructions in their repo:
   [https://github.com/yuchenlin/LLM-Blender](https://github.com/yuchenlin/LLM-Blender)
2. Open `get_pairRM_score.ipynb` and:

   * Set the paths to your **generated texts** (prompts / responses).
   * Run all cells to compute PairRM quality scores.


---

## 3. Step 2 – Compute Cultural Diversity

Pre-requisites:

* A **quality score CSV** (for images or text), and
* A folder with **tagged cultural entities** (continents, countries, artifacts, etc.)


### 3.1. Inputs

* `quality_scores_csv`: path to the CSV file with quality scores

  * Example: `QS/images_quality_scores.csv`
* `tagged_artifacts_folder`: path to the folder containing tagged entities

  * Example: `tags/images/` (where each artifact has a JSON/CSV file with continent/country/artifact tags)
* `w1`, `w2`, `w3`: weights for each level of cultural granularity

  * `w1`: continent weight
  * `w2`: country weight
  * `w3`: artifact weight


### 3.2. Example (Images)

```python
from <YOUR_MODULE> import calculate_cultural_diversity  # update this import

weights_comb = [
    (1,   0,   0),      # Only continent
    (0,   1,   0),      # Only country
    (0,   0,   1),      # Only artifact
    (0.5, 0.5, 0),      # Continent + country
    (1/3, 1/3, 1/3),    # Equal weights
]

results = []

for w1, w2, w3 in weights_comb:
    cd_score = calculate_cultural_diversity(
        quality_scores_csv="<LOCAL_QUALITY_CSV_PATH>",
        tagged_artifacts_folder="<LOCAL_TAGGED_ARTIFACTS_PATH>",
        w1=w1,  # Continent weight
        w2=w2,  # Country weight
        w3=w3,  # Artifact weight
        batch_size=8,
    )
    results.append(
        f"Weights ({w1}, {w2}, {w3}) -> Cultural Diversity (qVS): {cd_score:.4f}"
    )

for line in results:
    print(line)
```

Replace:

* `"<LOCAL_QUALITY_CSV_PATH>"` with the path to your CSV, e.g. `"QS/images_quality_scores.csv"`
* `"<LOCAL_TAGGED_ARTIFACTS_PATH>"` with your tagged data folder, e.g. `"tags/images/"`
* `<YOUR_MODULE>` with the module where `calculate_cultural_diversity` is defined.


- Note the calculation is based on CUBE [https://github.com/google-deepmind/cube/blob/main/cultural_diversity.ipynb](https://github.com/google-deepmind/cube/blob/main/cultural_diversity.ipynb)