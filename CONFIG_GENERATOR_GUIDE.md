# Config Generator Guide

## Overview

The Config Generator automatically creates the `config.json` file by:
1. Analyzing your CSV data file to detect audiences
2. Parsing markdown files with persona descriptions
3. Interactively helping you select charts and map personas

This eliminates manual config file creation and reduces errors.

## New Workflow

### Old Way (Manual)
1. Prepare template.pptx
2. Prepare data.csv
3. **Manually write config.json** ← Error-prone!
4. Run audience_book_updater.py

### New Way (Automated)
1. Prepare template.pptx
2. Prepare data.csv (tab-separated)
3. **Write persona markdown files** ← Much easier!
4. **Run generate_config.py** ← Automatic!
5. Run audience_book_updater.py

## Prerequisites

Your CSV file must be **tab-separated** with this structure:
```
CAT	SUBCAT	Audience1_Minutes	Audience1_Audience%	Audience1_Index	Audience2_Minutes	Audience2_Audience%	Audience2_Index...
```

**Required columns:**
- Column 1: Category (CAT)
- Column 2: Subcategory (SUBCAT)
- Repeating pattern for each audience:
  - `{AudienceName}_Minutes`
  - `{AudienceName}_Audience%`
  - `{AudienceName}_Index`

## Step 1: Create Persona Markdown Files

### Using the Template

Copy the template for each persona:
```bash
cp persona_template.md persona1.md
cp persona_template.md persona2.md
```

### Fill in Each Section

The generator extracts data from these specific sections:

#### Required Sections

1. **Title** - Must be in this exact format:
   ```markdown
   # Persona Archetype: [Name]
   ```

2. **Core Demographics** - Must include:
   ```markdown
   ## Core Demographics
   - **Age:** 46
   - **Job:** Senior Project Manager
   - **Location:** Adelaide, South Australia
   - **Source Audience:** Panel + Battery Intenders
   ```

   The `Source Audience` field is critical - it must match an audience name in your CSV!

3. **Quote** - A blockquote after demographics:
   ```markdown
   > "Your memorable quote here"
   ```

4. **Backstory** - A narrative paragraph:
   ```markdown
   ## Backstory
   [Your backstory paragraph here...]
   ```

5. **Empathy Map** - Must have these subsections:
   ```markdown
   ## Empathy Map

   ### Thinks & Feels
   - "First thought or feeling"
   - "Second thought or feeling"

   ### Sees
   - "What they see in their environment"

   ### Says & Does
   - "Their behaviors and actions"

   ### Hears
   - "What they hear from others"
   ```

The generator will extract text from the quoted bullet points.

### Example Markdown File

See the example Andrew Campbell persona in the repo for a complete reference.

## Step 2: Run the Config Generator

### Basic Usage

```bash
python generate_config.py data.csv persona1.md persona2.md persona3.md
```

You can include as many persona markdown files as you need.

### Interactive Process

The generator will guide you through these steps:

#### 1. CSV Analysis
```
Step 1: Analyzing CSV file...
  Found 4 audiences:
    1. GenPop
    2. Battery Intenders
    3. Panel + Battery Intenders
    4. New Builds
  Found 15 categories
```

#### 2. Markdown Parsing
```
Step 2: Parsing persona markdown files...
  ✓ Loaded: Andrew Campbell
  ✓ Loaded: Sarah Martinez
  Loaded 2 personas
```

#### 3. Client Name
```
Step 3: Configuration
Enter client name: Acme Energy Solutions
```

#### 4. Persona Mapping
```
Step 4: Assigning personas to template slots...

Persona 1: Andrew Campbell
  Age: 46, Job: Senior Project Manager
  Source Audience: Panel + Battery Intenders
  ✓ Matched to CSV audience: Panel + Battery Intenders
```

If auto-matching fails:
```
Persona 2: Unknown Persona
  ⚠ Could not auto-match. Available audiences:
    1. GenPop
    2. Battery Intenders
    3. Panel + Battery Intenders
    4. New Builds
  Select audience number (1-4): 3
```

#### 5. Chart Selection
```
Step 5: Selecting charts...
Available categories:
  1. MEDIA TYPOLOGY INDEX (SUMMARY)
  2. AVERAGE TIME USUALLY SPENT USING MEDIA FOR WHOLE WEEK
  3. SOCIAL MEDIA TOTAL DIGITAL (WEBSITES/APPS) USED IN 7 DAYS
  4. STREAMING VIDEO ON DEMAND USED IN THE LAST 7 DAYS (SVOD)
  5. BROADCAST VIDEO ON DEMAND USED IN THE LAST 7 DAYS (BVOD)
  ...

Enter chart selections (or press Enter to finish):
Format: <chart_number>,<category_number>,<title>
Example: 1,5,Social Media Usage

Chart 1 (or Enter to finish): 1,3,Social Media Platforms
  Subcategories in 'SOCIAL MEDIA TOTAL DIGITAL (WEBSITES/APPS) USED IN 7 DAYS':
    1. Discord (from Jan25)
    2. Facebook (revised Jan22)
    3. Facebook Messenger (App) (from Aug24)
    4. Instagram (revised Jan25)
    5. LinkedIn (revised Jan25)
    6. TikTok (revised Jan25)
    7. YouTube
    ...
  Select subcategories (comma-separated numbers, or 'all'): 2,4,5,6,7
  ✓ Added chart 1: Social Media Platforms (5 subcategories)

Chart 2 (or Enter to finish): 2,4,Streaming Services
  Subcategories in 'STREAMING VIDEO ON DEMAND USED IN THE LAST 7 DAYS (SVOD)':
    1. Amazon Prime Video
    2. Netflix
    3. Disney Plus
    ...
  Select subcategories (comma-separated numbers, or 'all'): all
  ✓ Added chart 2: Streaming Services (20 subcategories)

Chart 3 (or Enter to finish):
```

Press Enter when done adding charts.

#### 6. Completion
```
SUCCESS!
Configuration saved to: config.json

Summary:
  Client: Acme Energy Solutions
  Personas: 2
  Charts: 2

Next steps:
  1. Review config.json
  2. Run: python audience_book_updater.py
```

## Step 3: Review and Run

### Review Generated Config

Open `config.json` and verify:
- Client name is correct
- Personas mapped to correct CSV audiences
- Qualitative text looks good
- Charts have the right categories and subcategories

### Make Manual Adjustments (if needed)

You can edit the generated `config.json`:
- Adjust chart titles
- Modify display names for subcategories
- Reorder items
- Add or remove fields in qualitativeText

### Run the Updater

```bash
python audience_book_updater.py
```

## Tips & Tricks

### Matching Source Audiences

The generator tries to auto-match your markdown's `Source Audience` to CSV columns:
- Exact match: "Panel + Battery Intenders" = "Panel + Battery Intenders" ✓
- Case-insensitive: "battery intenders" = "Battery Intenders" ✓
- Partial match: "Battery" matches "Battery Intenders" ✓

**Best Practice:** Copy the exact audience name from your CSV into the markdown.

### Selecting Chart Subcategories

When selecting subcategories:
- Use `all` to include everything: `all`
- Use comma-separated numbers for specific items: `1,3,5,7`
- The numbers correspond to the list shown on screen

### Chart Numbering

Chart numbers don't have to be sequential:
```
Chart 1 (or Enter to finish): 1,3,Social Media
Chart 2 (or Enter to finish): 2,5,Streaming
Chart 3 (or Enter to finish): 5,1,Traditional Media  # Chart slot 5
```

This lets you control which chart goes in which template slot.

### Rerunning the Generator

If you need to regenerate:
```bash
# Backup your current config if you want to keep it
cp config.json config.backup.json

# Run generator again
python generate_config.py data.csv persona1.md persona2.md
```

The generator will overwrite `config.json`.

### Validating Output

Always validate your generated config:
```bash
python validate_config.py
```

This catches any issues before running the main updater.

## Troubleshooting

### "CSV file not found"
- Ensure your CSV file path is correct
- Use tab-separated format (not comma-separated)

### "Could not auto-match" for all personas
- Check that your CSV has the column pattern `{AudienceName}_Audience%`
- Verify the `Source Audience` field in your markdown matches CSV audience names

### "Error loading persona.md"
- Verify your markdown has all required sections
- Check for proper markdown formatting (headers, quotes, bullets)
- Look at `persona_template.md` for the expected structure

### Empty qualitativeText fields
- Ensure empathy map sections use the exact names: `Thinks & Feels`, `Sees`, `Says & Does`, `Hears`
- Text must be in quoted bullet points: `- "Your text here"`

### Charts not appearing
- Verify category names exactly match CSV `CAT` column values
- Check subcategory names match CSV `SUBCAT` column values

## Example Commands

### Single Persona
```bash
python generate_config.py survey_data.csv andrew_campbell.md
```

### Multiple Personas
```bash
python generate_config.py survey_data.csv persona1.md persona2.md persona3.md
```

### With Full Paths
```bash
python generate_config.py /path/to/data.csv /path/to/personas/*.md
```

## What Gets Mapped to config.json

| Markdown Section | Config Field | Template Placeholder |
|---|---|---|
| Persona Name (first name only) + Age | qualitativeText.Persona_Name | P{N}_TEXT::Persona_Name |
| Job | qualitativeText.Persona_Title | P{N}_TEXT::Persona_Title |
| Backstory | qualitativeText.Persona_Bio | P{N}_TEXT::Persona_Bio |
| Thinks & Feels (combined bullets) | qualitativeText.Thinks_Feels | P{N}_TEXT::Thinks_Feels |
| Sees (combined bullets) | qualitativeText.Sees | P{N}_TEXT::Sees |
| Says & Does (combined bullets) | qualitativeText.Says_Does | P{N}_TEXT::Says_Does |
| Hears (combined bullets) | qualitativeText.Hears | P{N}_TEXT::Hears |
| Source Audience | csvAudienceName | (maps to CSV columns) |

## Advanced: Customizing the Mapping

If you need different text fields, you can:

1. Edit `generate_config.py` to extract additional markdown sections
2. Update the `qualitativeText` dictionary in the generator
3. Ensure your template.pptx has matching placeholder names

For example, to add a "Goals" field:
- Add `### Goals` section to your markdown
- Modify generator to extract it
- Add `P{N}_TEXT::Goals` text box to template
