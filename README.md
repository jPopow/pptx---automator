# Audience Book Updater

A Python-based command-line tool that directly modifies PowerPoint template files by injecting data from CSV files, producing populated audience book presentations.

## Overview

This tool automates the creation of audience book presentations by:
- Reading pre-named placeholders in a master PowerPoint template
- Replacing placeholder content with data from a CSV file
- Preserving the original design, structure, and styling of the template
- Dynamically cleaning up unused personas and charts

## Core Philosophy

**Direct Modification, Not Recreation**: The script edits the existing template rather than creating a new presentation from scratch. This ensures perfect preservation of all design elements, formatting, and styling.

## Requirements

- Python 3.8 or higher
- Required Python packages (see `requirements.txt`):
  - `python-pptx` (>= 0.6.21)
  - `pandas` (>= 1.3.0)
  - `openpyxl` (>= 3.0.0)

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Step 1: Prepare Your Files

Place the following three files in the same directory as the script:

1. **`template.pptx`** - Your master PowerPoint template with pre-named placeholders
2. **`data.csv`** - Your CSV file containing survey data
3. **`config.json`** - Your configuration file (see below)

### Step 2: Configure Your Report

Create a `config.json` file to specify what data to use. You can start by copying `config.template.json`:

```bash
cp config.template.json config.json
```

Then edit `config.json` to match your needs:

```json
{
  "clientName": "Your Client Name Here",
  "personas": [
    {
      "templateSlot": 1,
      "csvAudienceName": "Budget Bargainers",
      "qualitativeText": {
        "Persona_Name": "Ben, 24",
        "Persona_Title": "Non-School Leavers",
        "Persona_Bio": "Description of the persona...",
        "Thinks_Feels": "What they think and feel...",
        "Sees": "What they see...",
        "Says_Does": "What they say and do...",
        "Hears": "What they hear..."
      }
    }
  ],
  "charts": [
    {
      "chartSlot": 1,
      "title": "Media Typology",
      "category": "Media",
      "subcategories": [
        {"csvName": "Newspapers", "displayName": "Newspapers"},
        {"csvName": "Magazines", "displayName": "Magazines"}
      ]
    }
  ]
}
```

### Step 3: Run the Script

Execute the script from your terminal:

```bash
python audience_book_updater.py
```

Or make it executable and run directly:

```bash
chmod +x audience_book_updater.py
./audience_book_updater.py
```

### Step 4: Review Output

The script will:
- Validate all input files
- Process the template according to your configuration
- Save the output as `[ClientName] - Audience Book - [Date].pptx`
- Generate a log file (`audience_book_updater.log`)

## Template Naming Convention

Your PowerPoint template must use the following naming convention for shapes:

### Text Placeholders
- Format: `P{slot}_TEXT::{field_name}`
- Examples:
  - `P1_TEXT::Persona_Name`
  - `P1_TEXT::Persona_Bio`
  - `P2_TEXT::Thinks_Feels`

### Chart Placeholders
- Format: `P{slot}_CHART::{chart_number}`
- Examples:
  - `P1_CHART::1`
  - `P2_CHART::2`

### Chart Title Placeholders
- Format: `P{slot}_TEXT::Chart{number}_Title`
- Examples:
  - `P1_TEXT::Chart1_Title`
  - `P2_TEXT::Chart2_Title`

## CSV Data Structure

Your `data.csv` file should have the following structure:

```csv
Category,Subcategory,Audience1_Audience %,Audience1_Index,Audience2_Audience %,Audience2_Index,...
Media,Newspapers,45.2,102,38.1,95,...
Media,Magazines,32.5,87,41.2,110,...
Social Media,Facebook,78.3,98,82.1,103,...
```

**Required Columns**:
- `Category`: Main category grouping
- `Subcategory`: Specific item within the category
- `{AudienceName}_Audience %`: Percentage value for the audience
- `{AudienceName}_Index`: Index value for the audience

The `{AudienceName}` must match the `csvAudienceName` in your `config.json`.

## Configuration File Details

### Client Name
```json
"clientName": "Your Client Name"
```
Used in the output filename.

### Personas Array
Each persona object includes:
- **`templateSlot`**: Which persona slot in the template (1, 2, 3, etc.)
- **`csvAudienceName`**: The audience name as it appears in the CSV column headers
- **`qualitativeText`**: Key-value pairs for all text fields to populate

### Charts Array
Each chart object includes:
- **`chartSlot`**: Which chart position (1, 2, 3, etc.)
- **`title`**: The chart title to display
- **`category`**: The category to filter from the CSV
- **`subcategories`**: Array of subcategory mappings
  - `csvName`: Name as it appears in the CSV
  - `displayName`: Name to display in the chart

## How It Works

The script operates in five phases:

### Phase 1: Initialization & Validation
- Checks for required files (`template.pptx`, `data.csv`, `config.json`)
- Loads CSV data into a pandas DataFrame
- Loads configuration from JSON
- Opens the PowerPoint template

### Phase 2: Text Population
- Iterates through each persona in the configuration
- Finds shapes by name in the template
- Replaces text content while preserving formatting

### Phase 3: Chart Population
- For each chart configuration:
  - Extracts data from CSV for specified category and subcategories
  - Updates chart data for each persona
  - Updates chart titles

### Phase 4: Dynamic Cleanup
- Identifies unused persona slots
- Deletes slides containing unused personas
- Removes unused chart shapes
- Keeps the presentation clean and relevant

### Phase 5: Finalization
- Saves the modified presentation with a timestamped filename
- Generates completion summary

## Logging

The script generates detailed logs in `audience_book_updater.log` including:
- Progress through each phase
- Warnings for missing shapes or data
- Error messages with stack traces
- Summary of operations

## Troubleshooting

### "Missing required files" error
- Ensure `template.pptx`, `data.csv`, and `config.json` are in the same directory as the script

### "Shape not found" warnings
- Verify that your template uses the correct naming convention
- Check that the shape names exactly match the expected format
- Ensure the template slot numbers in config match the template

### "Columns not found for audience" warnings
- Verify that the `csvAudienceName` in config exactly matches the column prefix in CSV
- Check for extra spaces or capitalization differences

### Chart data not updating
- Ensure the category and subcategory names in config exactly match those in the CSV
- Verify that the CSV has the required `_Audience %` and `_Index` columns for each audience

## Example Workflow

1. **Prepare your template** (`template.pptx`) with named placeholders for 7 personas
2. **Gather your data** in the standardized `data.csv` format
3. **Create config** for 2 personas and 3 charts
4. **Run the script**:
   ```bash
   python audience_book_updater.py
   ```
5. **Review output**: `Client Name - Audience Book - 20241118.pptx` will contain only the 2 configured personas with their 3 charts each

## Best Practices

1. **Start with the template**: Copy `config.template.json` to `config.json` and modify
2. **Test incrementally**: Start with one persona and one chart, then expand
3. **Check logs**: Review the log file if anything unexpected happens
4. **Backup your template**: Keep an original copy of `template.pptx`
5. **Validate CSV data**: Ensure no missing values in critical columns

## License

This tool is provided as-is for internal use.

## Support

For issues or questions, check the log file first, then review:
- Template naming conventions
- CSV data structure
- Configuration file format
