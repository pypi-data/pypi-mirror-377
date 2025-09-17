# TidySPSS

A Python package for quick processing, transforming, and managing SPSS (.sav) files with support for Excel and CSV inputs. This package is built on top of pyreadstat and pandas to give you flexible, production-ready template for processing and transforming data files into SPSS format with full metadata control.

## Philosophy

**"Make simple things simple, and complex things possible"**

## 📄 Processing Flow

```
LOAD → TRANSFORM → CONFIGURE → SAVE
```

1. **LOAD**: Read file with metadata preservation
2. **TRANSFORM**: Apply any pandas operations directly
3. **CONFIGURE**: Set SPSS-specific options
4. **SAVE**: Output with all configurations applied

## Features

- 📁 **Multi-format support**: Read from SPSS (.sav/.zsav), Excel (.xlsx/.xls), and CSV files
- 🔄 **Comprehensive transformations**: Reorder, rename, drop, and keep columns with ease
- 🏷️ **Metadata management**: Full support for SPSS labels, formats, measures, and display widths
- 🔧 **Value replacement**: Replace specific values across columns
- 📊 **Column positioning**: Advanced column reordering with range specifications
- 🔀 **File merging**: Combine multiple data files by stacking rows with source tracking
- 🌐 **Encoding support**: Automatic handling of multiple character encodings
- 🔧 **Production-ready**: Comprehensive logging and error handling

## Installation

Install using pip:

```bash
pip install tidyspss
```

Or using uv:

```bash
uv add tidyspss
```

## Quick Start

### Basic Usage

```python
from tidyspss import read_input_file, process_and_save

# Read a file (automatically detects format)
df, meta = read_input_file("data.sav")  # or .xlsx, .csv

# Process and save with transformations
df, meta = process_and_save(
    df=df,
    meta=meta,
    output_path="output.sav",
    user_variable_rename={"old_name": "new_name"},
    user_variable_drop=["unwanted_col1", "unwanted_col2"],
    user_column_labels={"Q1": "Question 1", "Q2": "Question 2"}
)
```

### Merging Multiple Files

```python
from tidyspss import add_cases, process_and_save

# Merge multiple files by stacking rows
files = ["wave1.sav", "wave2.xlsx", "wave3.csv"]
merged_df, merged_meta = add_cases(
    input_files=files,
    meta_priority=1,  # Use first file's metadata as base
    source_name="source_file"  # Column name for tracking source
)

# The merged dataframe will have a 'source_file' column 
# containing the filename each row came from

# Process and save the merged data
merged_df, merged_meta = process_and_save(
    df=merged_df,
    meta=merged_meta,
    output_path="merged_output.sav"
)
```

## API Reference

### Main Functions

#### `read_input_file(file_path)`
Reads a file into a pandas DataFrame with metadata.
- Supports: .sav, .zsav, .xlsx, .xls, .csv
- Returns: `(DataFrame, metadata)` tuple

#### `add_cases(input_files, meta_priority=1, source_name="mrgsrc")`
Merges multiple data files by stacking rows (concatenating).

**Parameters:**
- `input_files`: List of file paths to merge (can be .sav, .zsav, .xlsx, .xls, or .csv)
- `meta_priority`: Which file's metadata to use as base
  - If int: 1-based index of the file in input_files list
  - If str: exact filename that exists in input_files list
- `source_name`: Column name for tracking source file of each record (default: "mrgsrc")

**Returns:**
- `(merged_df, merged_meta)`: Tuple of concatenated DataFrame with source tracking column and consolidated metadata

**Example:**
```python
# Use first file's metadata
df, meta = add_cases(["data1.sav", "data2.xlsx"], meta_priority=1)

# Use specific file's metadata
df, meta = add_cases(["data1.sav", "data2.xlsx"], meta_priority="data2.xlsx")

# Custom source column name
df, meta = add_cases(files, source_name="wave_source")
```

#### `process_and_save(df, meta, output_path, **kwargs)`
Processes DataFrame with configurations and saves to SPSS format.

**Parameters:**
- `df`: Input DataFrame
- `meta`: Metadata from SPSS file (or None)
- `output_path`: Path for output .sav file
- `user_column_position`: Dict for column reordering
- `user_variable_drop`: List of columns to drop
- `user_variable_keep`: List of columns to keep (drops all others)
- `user_variable_rename`: Dict for renaming columns
- `user_value_replacement`: Dict for replacing values
- `user_column_labels`: Dict of column labels
- `user_variable_value_labels`: Dict of value labels
- `user_variable_format`: Dict of variable formats
- `user_variable_measure`: Dict of variable measures
- `user_variable_display_width`: Dict of display widths
- `user_missing_ranges`: Dict of missing value ranges
- `user_note`: File note string
- `user_file_label`: File label string
- `user_compress`: Boolean for file compression
- `user_row_compress`: Boolean for row compression


## Requirements

- Python ≥ 3.11
- pandas ≥ 2.3.0
- pyreadstat ≥ 1.3.0
- openpyxl ≥ 3.0.0

## License

MIT License - see LICENSE file for details.