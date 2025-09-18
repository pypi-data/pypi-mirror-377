# SPSS Metadata Printer 📊

Easy-to-use Python package for extracting, viewing, and exporting metadata from SPSS files with beautiful formatting.

## ✨ Features

- 📋 **Pretty-print comprehensive SPSS metadata** to console
- 💾 **Export metadata summaries** to text files automatically saved to Downloads
- 📄 **Extract metadata dictionary to JSON** for programmatic access and archival
- 📊 **Detailed variable information** including labels, types, and value mappings
- 🎨 **Beautiful table formatting** with configurable width and display options

## 🚀 Quick Start

### Installation

```bash
pip install metaprinter
```

Or using uv:

```bash
uv add metaprinter
```

### Basic Usage

```python
import pyreadstat
from metaprinter import print_metadata, export_metadata, extract_metadict

# Load your SPSS file
df, meta = pyreadstat.read_sav('data.sav')

# Display beautiful metadata summary inside a notebook
print_summary = print_metadata(df, meta)

# Export to Downloads/metadata_summary.txt
export_summary = export_metadata(df, meta)

# Extract metadata to JSON (Downloads/meta_dictionary.json)
extract_metadict(meta)
```

**Output Preview:**
```
============================================================
SPSS FILE METADATA
============================================================
File encoding   : 'UTF-8'
Number of cols  : 25
Number of rows  : 100
Table name      : 'Table'
File label      : 'Customer Satisfaction Survey'
Notes           : 'Notes'

VARIABLE METADATA
============================================================
┌───────────────┬─────────┬──────────┬───────────┬──────────────┬─────────────────────┬─────────────────────┐
│ column        ┆ dtype   ┆ column_n ┆ n_uniques ┆ n_categories ┆ column_label        ┆ value_labels        │
│ ---           ┆ ---     ┆ ---      ┆ ---       ┆ ---          ┆ ---                 ┆ ---                 │
│ str           ┆ str     ┆ i64      ┆ i64       ┆ i64          ┆ str                 ┆ str                 │
╞═══════════════╪═════════╪══════════╪═══════════╪══════════════╪═════════════════════╪═════════════════════╡
│ respondent_id ┆ Int64   ┆ 1547     ┆ 1547      ┆ 0            ┆ Respondent ID       ┆                     │
│ satisfaction  ┆ Int64   ┆ 1523     ┆ 5         ┆ 5            ┆ Satisfaction Level  ┆ {                   │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "1": "Very Low",  │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "2": "Low",       │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "3": "Neutral",   │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "4": "High",      │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "5": "Very High"  │
│               ┆         ┆          ┆           ┆              ┆                     ┆ }                   │
│ age           ┆ Int64   ┆ 1534     ┆ 6         ┆ 6            ┆ Age Group Category  ┆ {                   │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "1": "18-25",     │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "2": "26-35",     │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "3": "36-45",     │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "4": "46-55",     │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "5": "56-65",     │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "6": "65+"        │
│               ┆         ┆          ┆           ┆              ┆                     ┆ }                   │
│ ...           ┆ ...     ┆ ...      ┆ ...       ┆ ...          ┆ ...                 ┆ ...                 │
└───────────────┴─────────┴──────────┴───────────┴──────────────┴─────────────────────┴─────────────────────┘
```

## 📖 API Reference

### `print_metadata(df, meta, show_all_columns=True, max_width=222, include_all=False)`

Print a comprehensive metadata summary for SPSS data loaded with pyreadstat.

**Parameters:**
- `df`: DataFrame containing the SPSS data (Pandas or Polars)
- `meta`: Metadata object from `pyreadstat.read_sav()`
- `show_all_columns`: Whether to show all columns without truncation (default: True, optional)
- `max_width`: Maximum table width in characters (default: 222, optional)
- `include_all`: Whether to include all available metadata fields (default: False, optional)


---

### `export_metadata(df, meta, filename=None, show_all_columns=True, max_width=222, include_all=False)`

Export SPSS metadata summary to a text file in the Downloads folder.

**Parameters:**
- `df`: DataFrame containing the SPSS data (Pandas or Polars)
- `meta`: Metadata object from `pyreadstat.read_sav()`
- `filename`: Custom filename without extension (default: "metadata_summary")
- `show_all_columns`: Whether to show all columns without truncation (default: True, optional)
- `max_width`: Maximum table width in characters (default: 222, optional)
- `include_all`: Whether to include all available metadata fields (default: False, optional)


---

### `extract_metadict(meta, include_all=False, output_path=None)`

Extract metadata dictionary from pyreadstat meta object and save as JSON.

**Parameters:**
- `meta`: Metadata object from `pyreadstat.read_sav()`
- `include_all`: Whether to include all metadata fields or just essential ones (default: False, optional)
- `output_path`: Custom file path for JSON output (must end with .json). If None, saves to Downloads/meta_dictionary.json (default: None, optional)

**Example JSON Output (basic):**
```json
{
    "General Information": {
        "Notes": "Survey conducted in 2024",
        "Creation Time": "2024-01-15 10:30:00",
        "File Encoding": "UTF-8",
        "Number of Columns": 25,
        "Number of Rows": 100,
        "Table Name": "Table",
        "File Label": "Customer Satisfaction Survey"
    },
    "Variable Information": {
        "Column Names to Labels": {
            "respondent_id": "Respondent ID",
            "satisfaction": "Satisfaction Level",
            "age": "Age Group Category"
        },
        "Variable Value Labels": {
            "satisfaction": {
                "1": "Very Low",
                "2": "Low",
                "3": "Neutral",
                "4": "High",
                "5": "Very High"
            }
        }
    }
}
```

---

## 📋 Requirements

- Python >=3.11
- pyreadstat >=1.3.0
- polars >=1.3.0
- pandas >=2.3.0

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.