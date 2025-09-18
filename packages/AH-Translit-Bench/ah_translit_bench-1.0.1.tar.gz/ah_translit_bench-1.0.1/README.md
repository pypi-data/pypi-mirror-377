# AH-Translit_Bench: Arabic to Hindi Transliteration Benchmark Dataset

[![PyPI version](https://badge.fury.io/py/AH-Translit_Bench.svg)](https://pypi.org/project/AH-Translit_Bench/)
[![GitHub license](https://img.shields.io/github/license/vilalali/AH-Translit-Bench.svg)](https://github.com/vilalali/AH-Translit-Bench/blob/main/LICENSE)

## Description

AH-Translit_Bench is a 2000-entry Arabic to Hindi transliteration benchmark dataset covering Al-Quran, bibliographical, and Modern Standard Arabic (MSA) domains. Provided as a pip-installable Python package for model testing and research.

## Dataset Curators

This dataset was curated by:
*   **Vilal Ali**  
    MS By Research Student at Data Sciences And Analytics Centre, IIIT Hyderabad
    Email: vilal.ali@research.iiit.ac.in
*   **Mohd Hozaifa Khan**  
    MS By Research Student at Center for Visual Information Technology (CVIT) IIIT Hyderabad
    Email: mohd.hozaifa@research.iiit.ac.in

## Dataset Usage

This dataset is ideal for `testing models` for `Arabic to Hindi` transliteration tasks.

## Content Type

Text, specifically Arabic source text and its corresponding Hindi transliterated target text.

## File Type
CSV (Comma Separated Values)

## Version Description

Version 1.0 features 2000 Arabic-Hindi pairs segmented into three domain-specific CSVs (Al-Quran: 500, Biblo: 1000, MSA: 500). Each file contains accurately transliterated Arabic to Hindi text, suitable for model evaluation.

## Dataset Structure

The package includes three `.csv` files, each representing a distinct domain. Each CSV contains two columns: `Arabic source` text and its `Hindi transliteration`.

*   `al-quran_test_bench_mark_500.csv`: 500 entries from the Al-Quran domain.
*   `biblo_test_bench_mark_1000.csv`: 1000 entries from the bibliographical domain.
*   `msa_test_bench_mark_500.csv`: 500 entries from the Modern Standard Arabic (MSA) domain.

## How to Use this Dataset

To use this dataset, first install it via pip:

```bash
pip install AH-Translit_Bench
```

Then, in your Python code, you can load specific domains:

```python
import pandas as pd
from AH_Translit_Bench import load_dataset, get_available_domains

# See what domains are available
print("Available domains:", get_available_domains())
# Expected output: Available domains: ['al-quran', 'biblo', 'msa']

# Load the Al-Quran dataset
al_quran_df = load_dataset('al-quran')
print("\nAl-Quran Dataset Head:")
print(al_quran_df.head())
print(f"Al-Quran Dataset Shape: {al_quran_df.shape}") # Expected: (500, 2)

# Load the Bibliographical dataset
biblo_df = load_dataset('biblo')
print("\nBibliographical Dataset Head:")
print(biblo_df.head())
print(f"Bibliographical Dataset Shape: {biblo_df.shape}") # Expected: (1000, 2)

# Load the Modern Standard Arabic (MSA) dataset
msa_df = load_dataset('msa')
print("\nMSA (Modern Standard Arabic) Dataset Head:")
print(msa_df.head())
print(f"MSA Dataset Shape: {msa_df.shape}") # Expected: (500, 2)

# Example of accessing the first entry's data
first_arabic_text_al_quran = al_quran_df['Arabic'].iloc # Corrected to access value
first_hindi_translit_al_quran = al_quran_df['Hindi'].iloc # Corrected to access value
print(f"\nFirst Al-Quran entry: Arabic='{first_arabic_text_al_quran}', Hindi='{first_hindi_translit_al_quran}'")
```

## Example Data Snippet

Here's an example of how the data looks within the CSV files:

```csv
Arabic,Hindi
المطبعة الحيدرية،,"अल-मतबअह अल-हैदरियह,"
```

## License

This Python package code is licensed under the MIT License.

The dataset content (the CSV files) is released under the **Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)**.
You are free to:
*   **Share** — copy and redistribute the material in any medium or format.
*   **Adapt** — remix, transform, and build upon the material.
Under the following terms:
*   **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
*   **NonCommercial** — You may not use the material for commercial purposes. This means it is restricted to **research or learning purposes only**.
*   No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.
For the full license text, see: [https://creativecommons.org/licenses/by-nc/4.0/](https://creativecommons.org/licenses/by-nc/4.0/)


## Acknowledgements

The AH-Translit team from IIIT Hyderabad is happy to share this benchmark dataset. We extend our sincere thanks to **India Data** for hosting this dataset on their platform.

## Authors
**Vilal Ali** [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-0077B5.svg?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/vilal-ali/)
---
**Mohd Hozaifa Khan** [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-0077B5.svg?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mohd-hozaifa-khan-361b7814a/)
---
