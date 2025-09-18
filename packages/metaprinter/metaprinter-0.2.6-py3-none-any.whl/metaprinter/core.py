"""
SPSS Metadata Utility Module
============================
A utility module for printing and exporting SPSS data metadata using pyreadstat and polars.

This module provides functions to:
- Display comprehensive metadata from SPSS files
- Export metadata summaries to text files
- Handle both basic and extended metadata fields

Author: [Your Name]
Version:
Dependencies: pyreadstat, polars, pandas
"""

import json
import polars as pl
import pandas as pd
import os
from pathlib import Path
from io import StringIO
import sys
from datetime import datetime
from typing import Optional, Dict, Any, Union, Tuple


def _prepare_metadata_summary(df, meta, include_all=False):
    """
    Internal function to prepare metadata summary.
    Used by both print_metadata and export_metadata to avoid code duplication.

    Parameters:
    -----------
    df : polars.DataFrame or pandas.DataFrame
        The dataframe containing the SPSS data
    meta : pyreadstat metadata object
        The metadata object returned by pyreadstat.read_sav()
    include_all : bool, default False
        Whether to include all available metadata fields

    Returns:
    --------
    tuple
        (polars.DataFrame, dict) - The metadata summary DataFrame and category counts
    """
    # Convert to Polars if it's a Pandas DataFrame
    if isinstance(df, pd.DataFrame):
        df = pl.from_pandas(df)

    # Count categorical labels for each variable
    cat_counts = {
        var: len(labels) for var, labels in meta.variable_value_labels.items()
    }

    # Create pretty-formatted JSON strings for value labels
    value_labels_pretty = [
        json.dumps(
            meta.variable_value_labels.get(col, {}), indent=2, ensure_ascii=False
        )
        if meta.variable_value_labels.get(col)
        else ""
        for col in df.columns
    ]

    # Calculate column_n excluding nulls and empty strings for string columns
    column_n_values = []
    for c in df.columns:
        if df[c].dtype in [pl.Utf8, pl.String, pl.Categorical]:
            # For string columns, exclude both nulls and empty strings
            count = len(df.filter(pl.col(c).is_not_null() & (pl.col(c) != "")))
        else:
            # For non-string columns, just count non-nulls
            count = len(df.filter(pl.col(c).is_not_null()))
        column_n_values.append(count)

    # Build the metadata summary based on include_all parameter
    if include_all:
        # Build complete dictionary with all metadata fields
        summary_dict = {
            "column": df.columns,
            "dtype": df.dtypes,
            "column_n": column_n_values,
            "n_categories": [cat_counts.get(c, 0) for c in df.columns],
            "column_label": meta.column_labels,
            "value_labels": value_labels_pretty,
            "variable_measure": [
                meta.variable_measure.get(c, "unknown") for c in df.columns
            ],
            "variable_format": [
                meta.original_variable_types.get(c, "") for c in df.columns
            ],
            "missing_ranges": [meta.missing_ranges.get(c, []) for c in df.columns],
            "missing_user_values": [
                meta.missing_user_values.get(c, []) for c in df.columns
            ],
            "variable_alignment": [
                meta.variable_alignment.get(c, "unknown") for c in df.columns
            ],
            "variable_storage_width": [
                meta.variable_storage_width.get(c, None) for c in df.columns
            ],
            "variable_display_width": [
                meta.variable_display_width.get(c, None) for c in df.columns
            ],
        }
    else:
        # Basic metadata summary
        summary_dict = {
            "column": df.columns,
            "dtype": df.dtypes,
            "column_n": column_n_values,
            "n_categories": [cat_counts.get(c, 0) for c in df.columns],
            "column_label": meta.column_labels,
            "value_labels": value_labels_pretty,
        }

    return pl.DataFrame(summary_dict), cat_counts


def _format_metadata_output(meta, summary, include_all, show_all_columns, max_width):
    """
    Internal function to format metadata for output.

    Parameters:
    -----------
    meta : pyreadstat metadata object
        The metadata object returned by pyreadstat.read_sav()
    summary : polars.DataFrame
        The prepared metadata summary DataFrame
    include_all : bool
        Whether all metadata fields are included
    show_all_columns : bool
        Whether to show all columns without truncation
    max_width : int
        Maximum table width in characters

    Returns:
    --------
    str
        The formatted metadata output as a string
    """
    output = StringIO()

    # File-level metadata header
    print("=" * 60, file=output)
    print("SPSS FILE METADATA", file=output)
    print("=" * 60, file=output)
    print(f"File encoding   : {meta.file_encoding!r}", file=output)
    print(f"Number of cols  : {meta.number_columns}", file=output)
    print(f"Number of rows  : {meta.number_rows}", file=output)
    print(f"Table name      : {meta.table_name!r}", file=output)
    print(f"File label      : {meta.file_label!r}", file=output)
    print(f"Notes           : {meta.notes!r}", file=output)
    print(file=output)

    # Variable metadata header
    print("VARIABLE METADATA", file=output)
    if include_all:
        print("(Showing all available metadata fields)", file=output)
    else:
        print(
            "(Showing basic metadata - use include_all=True for all fields)",
            file=output,
        )
    print("=" * 60, file=output)

    # Configure display options
    config_options = {"tbl_width_chars": max_width, "fmt_str_lengths": 5000}

    if show_all_columns:
        config_options.update({"tbl_cols": -1, "tbl_rows": -1})

    # Format the summary table
    with pl.Config(**config_options):
        print(summary, file=output)

    return output.getvalue()


def print_metadata(df, meta, show_all_columns=True, max_width=222, include_all=False):
    """
    Print a comprehensive metadata summary for SPSS data loaded with pyreadstat.

    Parameters:
    -----------
    df : polars.DataFrame or pandas.DataFrame
        The dataframe containing the SPSS data
    meta : pyreadstat metadata object
        The metadata object returned by pyreadstat.read_sav()
    show_all_columns : bool, default True
        Whether to show all columns without truncation
    max_width : int, default 222
        Maximum table width in characters
    include_all : bool, default False
        Whether to include all available metadata fields. If False, only shows basic fields
        (column, dtype, column_n, n_categories, column_label, value_labels)

    Returns:
    --------
    polars.DataFrame
        The metadata summary table for further use if needed

    Example:
    --------
    >>> import pyreadstat
    >>> df, meta = pyreadstat.read_sav('your_file.sav')
    >>> metadata_summary = print_metadata(df, meta)
    """
    # Prepare the metadata summary
    summary, _ = _prepare_metadata_summary(df, meta, include_all)

    # Format and print the output
    output = _format_metadata_output(
        meta, summary, include_all, show_all_columns, max_width
    )
    print(output, end="")

    return summary


def export_metadata(
    df, meta, filename=None, show_all_columns=True, max_width=222, include_all=False
):
    """
    Export SPSS metadata summary to a text file in the downloads folder.

    Parameters:
    -----------
    df : polars.DataFrame or pandas.DataFrame
        The dataframe containing the SPSS data
    meta : pyreadstat metadata object
        The metadata object returned by pyreadstat.read_sav()
    filename : str, optional
        Custom filename (without extension). If None, uses "metadata_summary"
    show_all_columns : bool, default True
        Whether to show all columns without truncation
    max_width : int, default 222
        Maximum table width in characters
    include_all : bool, default False
        Whether to include all available metadata fields. If False, only shows basic fields
        (column, dtype, column_n, n_categories, column_label, value_labels)

    Returns:
    --------
    str or None
        The full path where the file was saved, or None if export failed

    Example:
    --------
    >>> import pyreadstat
    >>> df, meta = pyreadstat.read_sav('your_file.sav')
    >>> export_path = export_metadata(df, meta, filename="my_metadata", include_all=True)
    """
    # Prepare the metadata summary
    summary, _ = _prepare_metadata_summary(df, meta, include_all)

    # Format the output
    content = _format_metadata_output(
        meta, summary, include_all, show_all_columns, max_width
    )

    # Determine the downloads folder path
    downloads_path = Path.home() / "Downloads"
    if not downloads_path.exists():
        # Fallback to current directory if Downloads folder doesn't exist
        downloads_path = Path.cwd()

    # Set filename
    if filename is None:
        filename = "metadata_summary"

    # Ensure .txt extension
    if not filename.endswith(".txt"):
        filename = f"{filename}.txt"

    full_path = downloads_path / filename

    # Write to file
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Metadata summary exported successfully to: {full_path}")
        return str(full_path)

    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return None


def print_and_export_metadata(
    df,
    meta,
    export_filename=None,
    show_all_columns=True,
    max_width=222,
    include_all=False,
):
    """
    Convenience function that both prints and exports SPSS metadata summary.

    Parameters:
    -----------
    df : polars.DataFrame or pandas.DataFrame
        The dataframe containing the SPSS data
    meta : pyreadstat metadata object
        The metadata object returned by pyreadstat.read_sav()
    export_filename : str, optional
        Custom filename for export (without extension). If None, uses "metadata_summary"
    show_all_columns : bool, default True
        Whether to show all columns without truncation
    max_width : int, default 222
        Maximum table width in characters
    include_all : bool, default False
        Whether to include all available metadata fields. If False, only shows basic fields
        (column, dtype, column_n, n_categories, column_label, value_labels)

    Returns:
    --------
    tuple
        (polars.DataFrame, str) - The metadata summary table and export file path

    Example:
    --------
    >>> import pyreadstat
    >>> df, meta = pyreadstat.read_sav('your_file.sav')
    >>> summary, export_path = print_and_export_metadata(df, meta, include_all=True)
    """
    # Print to console
    summary = print_metadata(df, meta, show_all_columns, max_width, include_all)

    # Export to file
    export_path = export_metadata(
        df, meta, export_filename, show_all_columns, max_width, include_all
    )

    return summary, export_path


def extract_metadict(meta, include_all=False, output_path=None):
    """
    Extract metadata dictionary from pyreadstat meta object and save as JSON.

    Parameters
    ----------
    meta : pyreadstat.metadata_container
        The metadata returned by pyreadstat.read_sav(...).
    include_all : bool, optional (default=False)
        If False, only include General Information, Column Names to Labels, and Variable Value Labels.
        If True, include all available metadata as in the original script.
    output_path : str, optional
        File path to save JSON (must end with .json). If None, the JSON will be
        saved automatically to the Downloads folder.
    """

    # Recursive datetime/dict/list conversion
    def convert_to_string(value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(value, dict):
            return {k: convert_to_string(v) for k, v in value.items()}
        if isinstance(value, list):
            return [convert_to_string(v) for v in value]
        return value

    # Always included section
    meta_dict = {
        "General Information": {
            "Notes": convert_to_string(meta.notes),
            "Creation Time": convert_to_string(meta.creation_time),
            "Modification Time": convert_to_string(meta.modification_time),
            "File Encoding": meta.file_encoding,
            "Number of Columns": meta.number_columns,
            "Number of Rows": meta.number_rows,
            "Table Name": meta.table_name,
            "File Label": meta.file_label,
        }
    }

    if include_all:
        # Full details
        meta_dict["Variable Information"] = {
            "Column Names to Labels": meta.column_names_to_labels,
            "Column Names": meta.column_names,
            "Column Labels": meta.column_labels,
            "Variable Value Labels": convert_to_string(meta.variable_value_labels),
            "Value Labels": convert_to_string(meta.value_labels),
            "Variable to Label": meta.variable_to_label,
            "Original Variable Types": meta.original_variable_types,
            "Readstat Variable Types": meta.readstat_variable_types,
            "Missing Ranges": convert_to_string(meta.missing_ranges),
            "Missing User Values": convert_to_string(meta.missing_user_values),
            "Variable Alignment": meta.variable_alignment,
            "Variable Storage Width": meta.variable_storage_width,
            "Variable Display Width": meta.variable_display_width,
            "Variable Measure": meta.variable_measure,
        }
    else:
        # Only key mappings
        meta_dict["Variable Information"] = {
            "Column Names to Labels": meta.column_names_to_labels,
            "Variable Value Labels": convert_to_string(meta.variable_value_labels),
        }

    # Save to specified path or Downloads
    if output_path:
        if not output_path.lower().endswith(".json"):
            raise ValueError("output_path must end with .json")
        save_path = output_path
    else:
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(downloads_dir, exist_ok=True)
        save_path = os.path.join(downloads_dir, "meta_dictionary.json")

    with open(save_path, "w", encoding="utf-8") as file:
        json.dump(meta_dict, file, ensure_ascii=False, indent=4)

    print(f"✅ Metadata dictionary saved successfully to: {save_path}")

    

def combined_label_maker(
    input_path: str,
    output_path: str,
    col_label_sheet: str = 'col_label',
    value_label_sheet: str = 'value_label',
    col_dict_name: str = 'user_column_labels',
    value_dict_name: str = 'user_variable_value_labels',
    quote_style: str = "'''",
    indent: str = "    ",
    encoding: str = 'utf-8',
    variable_column: str = 'variable',
    value_column: str = 'value',
    label_column: str = 'label',
    verbose: bool = True
) -> Tuple[Dict[str, str], Dict[str, Dict[Union[int, float, str], str]]]:
    """
    Transform Excel file with two sheets into a single Python file containing both 
    column labels and value labels dictionaries.
    
    Parameters
    ----------
    input_path : str
        Path to input Excel file with two sheets: one for column labels, one for value labels
    output_path : str
        Path where the output Python file will be saved
    col_label_sheet : str, optional
        Name of the sheet containing column labels (default: 'col_label')
    value_label_sheet : str, optional
        Name of the sheet containing value labels (default: 'value_label')
    col_dict_name : str, optional
        Name of the column labels dictionary in output (default: 'user_column_labels')
    value_dict_name : str, optional
        Name of the value labels dictionary in output (default: 'user_variable_value_labels')
    quote_style : str, optional
        Quote style for strings in output (default: triple quotes)
    indent : str, optional
        Indentation for dictionary items (default: 4 spaces)
    encoding : str, optional
        File encoding (default: 'utf-8')
    variable_column : str, optional
        Name of the column containing variable names (default: 'variable')
    value_column : str, optional
        Name of the column containing values in value_label sheet (default: 'value')
    label_column : str, optional
        Name of the column containing labels (default: 'label')
    verbose : bool, optional
        Whether to print progress messages (default: True)
    
    Returns
    -------
    Tuple[Dict[str, str], Dict[str, Dict[Union[int, float, str], str]]]
        Tuple containing (column_labels_dict, value_labels_dict)
    
    Examples
    --------
    >>> # Basic usage
    >>> col_labels, val_labels = combined_label_maker(
    ...     input_path="label_mapping.xlsx",
    ...     output_path="label_mapping.py"
    ... )
    
    >>> # Custom configuration
    >>> col_labels, val_labels = combined_label_maker(
    ...     input_path="mappings.xlsx",
    ...     output_path="all_labels.py",
    ...     col_label_sheet="columns",
    ...     value_label_sheet="values",
    ...     col_dict_name="column_labels",
    ...     value_dict_name="value_labels"
    ... )
    """
    
    def _print(msg: str):
        """Helper function for conditional printing"""
        if verbose:
            print(msg)
    
    # ============ Helper functions from column_label_maker ============
    
    def clean_variable_name(val):
        """Clean variable names - keep exactly as is, only check for null values"""
        if pd.isna(val):
            return None
        return str(val)
    
    def clean_label_text(val):
        """Clean label text - handle whitespace but preserve empty strings"""
        if pd.isna(val):
            return ""
        text = str(val)
        if text.strip() == "":
            return ""
        return text.strip()
    
    # ============ Helper functions from value_label_maker ============
    
    def convert_value(val):
        """Smart value type detection: tries int, then float, then keeps as string"""
        if pd.isna(val):
            return None
        try:
            if float(val).is_integer():
                return int(val)
            return float(val)
        except (ValueError, TypeError):
            return str(val).strip()
    
    # ============ Processing functions ============
    
    def process_column_labels(df):
        """Process column labels sheet"""
        _print("\n📊 Processing Column Labels Sheet...")
        
        # Validate columns
        if variable_column not in df.columns or label_column not in df.columns:
            raise ValueError(f"Column labels sheet must have '{variable_column}' and '{label_column}' columns")
        
        initial_rows = len(df)
        _print(f"  Found {initial_rows} rows")
        
        # Clean data
        df['variable_cleaned'] = df[variable_column].apply(clean_variable_name)
        df['label_cleaned'] = df[label_column].apply(clean_label_text)
        
        # Remove rows with null variable names
        df_cleaned = df[df['variable_cleaned'].notna()].copy()
        df_cleaned[variable_column] = df_cleaned['variable_cleaned']
        df_cleaned[label_column] = df_cleaned['label_cleaned']
        
        removed = initial_rows - len(df_cleaned)
        if removed > 0:
            _print(f"  ⚠ Removed {removed} rows with null variable names")
        
        # Check for duplicates
        duplicates = df_cleaned[variable_column].value_counts()
        duplicate_count = (duplicates > 1).sum()
        if duplicate_count > 0:
            _print(f"  ⚠ Warning: Found {duplicate_count} duplicate variable names")
        
        # Create dictionary
        column_labels = df_cleaned.set_index(variable_column)[label_column].to_dict()
        
        empty_labels = sum(1 for label in column_labels.values() if label == "")
        _print(f"  ✓ Processed {len(column_labels)} column labels ({empty_labels} empty)")
        
        return column_labels
    
    def process_value_labels(df):
        """Process value labels sheet"""
        _print("\n📊 Processing Value Labels Sheet...")
        
        # Validate columns
        required_cols = [variable_column, value_column, label_column]
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Value labels sheet missing columns: {missing}")
        
        initial_rows = len(df)
        _print(f"  Found {initial_rows} rows")
        
        # Clean data
        df_cleaned = df.dropna(subset=[value_column, variable_column])
        df_cleaned = df_cleaned[df_cleaned[variable_column].astype(str).str.strip() != '']
        
        # Clean labels
        df_cleaned[label_column] = df_cleaned[label_column].apply(
            lambda x: str(x).strip() if pd.notna(x) and str(x).strip() != '' else x
        )
        
        # Convert values
        df_cleaned[value_column] = df_cleaned[value_column].apply(convert_value)
        df_cleaned = df_cleaned[df_cleaned[value_column].notna()]
        
        removed = initial_rows - len(df_cleaned)
        if removed > 0:
            _print(f"  ⚠ Removed {removed} invalid rows")
        
        # Check for duplicate variable-value pairs
        duplicates = df_cleaned.groupby([variable_column, value_column]).size()
        duplicate_count = (duplicates > 1).sum()
        if duplicate_count > 0:
            _print(f"  ⚠ Warning: Found {duplicate_count} duplicate variable-value pairs")
        
        # Create nested dictionary
        value_labels = {}
        grouped = df_cleaned.groupby(variable_column, sort=False)
        
        for variable, group in grouped:
            value_dict = {}
            for idx, row in group.iterrows():
                value_dict[row[value_column]] = row[label_column]
            value_labels[variable] = value_dict
        
        total_labels = sum(len(labels) for labels in value_labels.values())
        _print(f"  ✓ Processed {len(value_labels)} variables with {total_labels} total value labels")
        
        return value_labels
    
    def format_column_dict(data, dict_name_param):
        """Format column labels dictionary"""
        lines = [f"{dict_name_param} = {{"]
        for variable, label in data.items():
            lines.append(f"{indent}'{variable}': {quote_style}{label}{quote_style},")
        lines.append("}")
        return lines
    
    def format_value_dict(data, dict_name_param):
        """Format value labels dictionary"""
        lines = [f"\n\n{dict_name_param} = {{"]
        for variable, value_dict in data.items():
            lines.append(f"{indent}'{variable}': {{")
            for value, label in value_dict.items():
                if isinstance(value, str):
                    key_repr = f"'{value}'"
                else:
                    key_repr = str(value)
                lines.append(f"{indent}{indent}{key_repr}: {quote_style}{label}{quote_style},")
            lines.append(f"{indent}}},")
        lines.append("}")
        return lines
    
    def save_combined_output(col_labels, val_labels, file_path):
        """Save both dictionaries to a single Python file"""
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Format both dictionaries
        all_lines = []
        all_lines.extend(format_column_dict(col_labels, col_dict_name))
        all_lines.extend(format_value_dict(val_labels, value_dict_name))
        
        # Write to file
        with open(output_path, "w", encoding=encoding) as file:
            file.write("\n".join(all_lines))
        
        _print(f"\n✓ Combined dictionaries saved to: {output_path}")
    
    # ============ Main execution ============
    
    try:
        _print("=" * 60)
        _print("COMBINED LABEL MAKER - Starting Processing")
        _print("=" * 60)
        _print(f"Input file: {input_path}")
        _print(f"Output file: {output_path}")
        
        # Load Excel file
        file_path = Path(input_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        if not file_path.suffix.lower() in ['.xlsx', '.xls']:
            raise ValueError(f"Input must be an Excel file, got: {file_path.suffix}")
        
        # Check available sheets
        xl_file = pd.ExcelFile(file_path)
        available_sheets = xl_file.sheet_names
        _print(f"\nAvailable sheets: {available_sheets}")
        
        # Validate required sheets exist
        if col_label_sheet not in available_sheets:
            raise ValueError(f"Sheet '{col_label_sheet}' not found. Available: {available_sheets}")
        if value_label_sheet not in available_sheets:
            raise ValueError(f"Sheet '{value_label_sheet}' not found. Available: {available_sheets}")
        
        # Process column labels sheet
        df_col = pd.read_excel(file_path, sheet_name=col_label_sheet)
        column_labels = process_column_labels(df_col)
        
        # Process value labels sheet
        df_val = pd.read_excel(file_path, sheet_name=value_label_sheet)
        value_labels = process_value_labels(df_val)
        
        # Save combined output
        save_combined_output(column_labels, value_labels, output_path)
        
        # Print summary
        _print("\n" + "=" * 60)
        _print("PROCESSING SUMMARY")
        _print("=" * 60)
        _print(f"Column Labels Dictionary: {len(column_labels)} variables")
        _print(f"Value Labels Dictionary: {len(value_labels)} variables")
        
        # Show variables with longest column labels
        if column_labels:
            # Filter out empty labels and sort by length
            non_empty_labels = [(var, label) for var, label in column_labels.items() if label != ""]
            if non_empty_labels:
                sorted_by_length = sorted(non_empty_labels, key=lambda x: len(x[1]), reverse=True)
                _print(f"\nVariables with longest labels:")
                for i, (var, label) in enumerate(sorted_by_length[:3], 1):
                    preview = label[:50] + "..." if len(label) > 50 else label
                    _print(f"  {i}. {var}: {len(label)} chars - '{preview}'")
        
        # Show top variables with most value labels
        if value_labels:
            sorted_vars = sorted(value_labels.items(), key=lambda x: len(x[1]), reverse=True)
            _print(f"\nTop 5 variables by value label count:")
            for i, (var, labels) in enumerate(sorted_vars[:5], 1):
                _print(f"  {i}. {var}: {len(labels)} labels")
        
        _print("=" * 60)
        _print("🎉 Combined label transformation completed successfully!")
        
        return column_labels, value_labels
        
    except Exception as e:
        _print(f"\n❌ Error during transformation: {str(e)}")
        raise


# Optional: Add version info and other module metadata
__version__ = "0.2.0"
__author__ = "Your Name"
__all__ = [
    "print_metadata",
    "export_metadata",
    "print_and_export_metadata",
    "extract_metadict",
    "combined_label_maker"
]


if __name__ == "__main__":
    # Example usage when run as a script
    print("SPSS Metadata Utility Module")
    print(f"Version: {__version__}")
    print("\nThis module provides functions for working with SPSS metadata.")
    print("\nUsage:")
    print("  import pyreadstat")
    print("  from spss_metadata_utils import print_metadata, export_metadata")
    print("  ")
    print("  df, meta = pyreadstat.read_sav('your_file.sav')")
    print("  ")
    print("  # Print basic metadata")
    print("  print_metadata(df, meta)")
    print("  ")
    print("  # Export with all metadata fields")
    print("  export_metadata(df, meta, include_all=True)")

    col_labels, val_labels = combined_label_maker(
    input_path="label_mapping.xlsx",
    output_path="label_mapping.py"
    )
    
    # Custom configuration example
    # col_labels, val_labels = combined_label_maker(
    #     input_path="my_mappings.xlsx",
    #     output_path="all_labels.py",
    #     col_label_sheet="columns",
    #     value_label_sheet="values",
    #     col_dict_name="my_column_labels",
    #     value_dict_name="my_value_labels",
    #     verbose=True
    # )
