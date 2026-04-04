# Notebooks

Interactive notebooks for exploring the London crime datasets.

| Platform | Link |
|----------|------|
| **Google Colab** | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fenneh/london-crime-data/blob/main/notebooks/explore_london_crime.ipynb) |
| **Deepnote** | [Open in Deepnote](https://deepnote.com/launch?url=https://github.com/fenneh/london-crime-data/blob/main/notebooks/explore_london_crime.ipynb) |
| **Local** | `jupyter notebook notebooks/explore_london_crime.ipynb` |

## Contents

| Notebook | Description |
|----------|-------------|
| [`explore_london_crime.ipynb`](explore_london_crime.ipynb) | Recorded crime, knife crime trends, stop and search, VAWG — full walkthrough |

## What the notebook covers

- Loading Parquet files directly from GitHub (no clone required)
- Wide → long format conversion for the geographic datasets
- Crime by major category and borough
- Knife crime monthly trend and seasonality (why February dips)
- Stop and search by officer-defined ethnicity, legislation, and outcome
- VAWG offences by type
- Full historical series back to 2010 by combining current + historical files
