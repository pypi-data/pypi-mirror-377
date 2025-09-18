# File: AH_Translit_Bench/__init__.py
import pandas as pd
import importlib.resources as pkg_resources
from . import data

def load_dataset(domain: str) -> pd.DataFrame:
    """
    Loads one of the AH-Translit_Bench datasets based on the specified domain.

    Args:
        domain (str): The domain of the dataset to load.
                      Must be one of 'al-quran', 'biblo', or 'msa'.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the Arabic and Hindi transliteration pairs.
                      The columns are typically 'Arabic' and 'Hindi'.

    Raises:
        ValueError: If an invalid domain is provided.
    """
    domain_files = {
        'al-quran': 'al-quran_test_bench_mark_500.csv',
        'biblo': 'biblo_test_bench_mark_1000.csv',
        'msa': 'msa_test_bench_mark_500.csv',
    }

    if domain.lower() not in domain_files:
        raise ValueError(f"Invalid domain: '{domain}'. "
                         f"Please choose from {list(domain_files.keys())}.")

    filename = domain_files[domain.lower()]

    with pkg_resources.path(data, filename) as data_path:
        df = pd.read_csv(data_path)

    return df

def get_available_domains() -> list:
    """Returns a list of available dataset domains."""
    return ['al-quran', 'biblo', 'msa']