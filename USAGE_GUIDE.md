# Quick Start Guide

## First Time Setup

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare Your Files

You need three files in the same directory as the script:

#### a) `template.pptx`
Your PowerPoint template with pre-named shapes following this convention:
- Text: `P1_TEXT::Persona_Name`, `P1_TEXT::Persona_Bio`, etc.
- Charts: `P1_CHART::1`, `P1_CHART::2`, etc.
- Chart Titles: `P1_TEXT::Chart1_Title`, `P1_TEXT::Chart2_Title`, etc.

#### b) `data.csv`
Your survey data in CSV format. See `data.example.csv` for the structure:
- Must have `Category` and `Subcategory` columns
- Must have `{AudienceName}_Audience %` and `{AudienceName}_Index` columns for each audience

#### c) `config.json`
Your configuration file. Start by copying the template:
```bash
cp config.template.json config.json
```

### 3. Edit config.json

Customize the configuration for your specific report:

```json
{
  "clientName": "Acme University",
  "personas": [
    {
      "templateSlot": 1,
      "csvAudienceName": "Budget Bargainers",
      "qualitativeText": {
        "Persona_Name": "Ben, 24",
        "Persona_Title": "Non-School Leavers",
        "Persona_Bio": "Your persona description here..."
      }
    }
  ],
  "charts": [
    {
      "chartSlot": 1,
      "title": "Media Typology",
      "category": "Media",
      "subcategories": [
        {"csvName": "Newspapers", "displayName": "Newspapers"}
      ]
    }
  ]
}
```

### 4. Run the Script
```bash
python audience_book_updater.py
```

### 5. Check the Output
- Output file: `[ClientName] - Audience Book - [Date].pptx`
- Log file: `audience_book_updater.log`

## Common Configuration Scenarios

### Scenario 1: Two Personas, Three Charts
```json
{
  "clientName": "Sample Client",
  "personas": [
    {
      "templateSlot": 1,
      "csvAudienceName": "Budget Bargainers",
      "qualitativeText": { ... }
    },
    {
      "templateSlot": 2,
      "csvAudienceName": "Go Getters",
      "qualitativeText": { ... }
    }
  ],
  "charts": [
    {"chartSlot": 1, "title": "Media", ...},
    {"chartSlot": 2, "title": "Social Media", ...},
    {"chartSlot": 3, "title": "Online Activities", ...}
  ]
}
```

This will:
- Keep only slides for Personas 1 and 2
- Delete slides for Personas 3, 4, 5, etc.
- Keep Charts 1, 2, and 3 for each persona
- Delete Charts 4, 5, 6, etc. (if they exist in the template)

### Scenario 2: Full Seven Personas
```json
{
  "clientName": "Full Report Client",
  "personas": [
    {"templateSlot": 1, "csvAudienceName": "Audience1", ...},
    {"templateSlot": 2, "csvAudienceName": "Audience2", ...},
    {"templateSlot": 3, "csvAudienceName": "Audience3", ...},
    {"templateSlot": 4, "csvAudienceName": "Audience4", ...},
    {"templateSlot": 5, "csvAudienceName": "Audience5", ...},
    {"templateSlot": 6, "csvAudienceName": "Audience6", ...},
    {"templateSlot": 7, "csvAudienceName": "Audience7", ...}
  ],
  "charts": [ ... ]
}
```

## Understanding the Naming Convention

### Persona Slots
The `templateSlot` number determines which section of the template to use:
- `templateSlot: 1` → All shapes named `P1_...`
- `templateSlot: 2` → All shapes named `P2_...`
- And so on...

### Text Fields
For each persona slot, you can populate any text field by adding it to `qualitativeText`:
```json
"qualitativeText": {
  "Persona_Name": "Text for P1_TEXT::Persona_Name",
  "Custom_Field": "Text for P1_TEXT::Custom_Field"
}
```

The script will look for a shape named `P{slot}_TEXT::{field_name}` and update its content.

### Chart Slots
Charts are numbered independently:
- `chartSlot: 1` → Updates `P1_CHART::1`, `P2_CHART::1`, etc.
- `chartSlot: 2` → Updates `P1_CHART::2`, `P2_CHART::2`, etc.

Each chart is updated for **every persona** you've configured.

## Tips & Tricks

### 1. Testing with Minimal Configuration
Start small and expand:
```json
{
  "clientName": "Test",
  "personas": [
    {
      "templateSlot": 1,
      "csvAudienceName": "Budget Bargainers",
      "qualitativeText": {
        "Persona_Name": "Test Name"
      }
    }
  ],
  "charts": []
}
```

### 2. Matching CSV Audience Names
The `csvAudienceName` must **exactly match** the column prefix in your CSV:

CSV columns: `Budget Bargainers_Audience %`, `Budget Bargainers_Index`
Config: `"csvAudienceName": "Budget Bargainers"`

### 3. Matching Categories and Subcategories
These must **exactly match** the values in your CSV's `Category` and `Subcategory` columns:

```csv
Category,Subcategory,...
Media,Newspapers,...
```

```json
{
  "chartSlot": 1,
  "category": "Media",
  "subcategories": [
    {"csvName": "Newspapers", "displayName": "Newspapers"}
  ]
}
```

### 4. Custom Display Names
You can rename items in charts without changing the CSV:
```json
"subcategories": [
  {"csvName": "Free-to-air TV", "displayName": "Free TV"}
]
```

### 5. Checking What Went Wrong
Always check the log file if something doesn't work:
```bash
cat audience_book_updater.log
```

Look for warnings like:
- `Shape not found: P1_TEXT::Something` → Check template naming
- `Columns not found for audience X` → Check CSV column names
- `Subcategory X not found` → Check CSV data

## Troubleshooting Checklist

- [ ] All three files (`template.pptx`, `data.csv`, `config.json`) are in the script directory
- [ ] Python dependencies are installed (`pip install -r requirements.txt`)
- [ ] Template shapes follow the naming convention exactly
- [ ] `csvAudienceName` matches the CSV column prefix exactly
- [ ] Category and subcategory names match the CSV exactly
- [ ] JSON syntax is valid (use a JSON validator if unsure)
- [ ] Reviewed the log file for specific errors

## Example Complete Workflow

1. **Copy template file**:
   ```bash
   cp /path/to/master/template.pptx ./template.pptx
   ```

2. **Copy data file**:
   ```bash
   cp /path/to/survey/results.csv ./data.csv
   ```

3. **Create configuration**:
   ```bash
   cp config.template.json config.json
   # Edit config.json with your text editor
   ```

4. **Run the updater**:
   ```bash
   python audience_book_updater.py
   ```

5. **Verify output**:
   ```bash
   ls -lh *Audience_Book*.pptx
   ```

6. **Check for issues**:
   ```bash
   tail -n 50 audience_book_updater.log
   ```

## Advanced: Running Multiple Reports

You can organize multiple configurations:

```bash
# Create separate config files
cp config.template.json config_client_a.json
cp config.template.json config_client_b.json

# Run with specific config
python audience_book_updater.py
# (Edit script to accept config file as argument, or copy config_client_a.json to config.json before running)
```

## Getting Help

If you encounter issues:
1. Check the log file for detailed error messages
2. Verify your files against the examples provided
3. Review the README.md for comprehensive documentation
4. Ensure all naming conventions are followed exactly
