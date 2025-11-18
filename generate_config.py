#!/usr/bin/env python3
"""
Configuration Generator for Audience Book Updater

This script automatically generates config.json from:
1. A CSV file with audience data
2. Markdown files with persona descriptions
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd


class MarkdownPersonaParser:
    """Parses persona information from markdown files."""

    def __init__(self, md_file_path: str):
        """Initialize parser with markdown file path."""
        self.md_file_path = Path(md_file_path)
        self.content = ""
        self.persona = {}

    def parse(self) -> Dict:
        """
        Parse the markdown file and extract persona information.

        Returns:
            Dictionary with persona data.
        """
        if not self.md_file_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {self.md_file_path}")

        with open(self.md_file_path, 'r', encoding='utf-8') as f:
            self.content = f.read()

        # Extract persona name from title
        self.persona['name'] = self._extract_persona_name()

        # Extract core demographics
        demographics = self._extract_demographics()
        self.persona['age'] = demographics.get('age', '')
        self.persona['job'] = demographics.get('job', '')
        self.persona['location'] = demographics.get('location', '')
        self.persona['source_audience'] = demographics.get('source_audience', '')

        # Extract quote
        self.persona['quote'] = self._extract_quote()

        # Extract empathy map sections
        self.persona['thinks_feels'] = self._extract_section('Thinks & Feels')
        self.persona['sees'] = self._extract_section('Sees')
        self.persona['says_does'] = self._extract_section('Says & Does')
        self.persona['hears'] = self._extract_section('Hears')

        # Extract backstory
        self.persona['bio'] = self._extract_backstory()

        return self.persona

    def _extract_persona_name(self) -> str:
        """Extract persona name from title."""
        match = re.search(r'#\s+Persona Archetype:\s*(.+)', self.content)
        if match:
            return match.group(1).strip()
        return "Unknown"

    def _extract_demographics(self) -> Dict:
        """Extract core demographics section."""
        demographics = {}

        # Find the Core Demographics section
        demo_match = re.search(
            r'##\s+Core Demographics\s*\n(.*?)(?=\n##|\n---|\Z)',
            self.content,
            re.DOTALL
        )

        if demo_match:
            demo_text = demo_match.group(1)

            # Extract age
            age_match = re.search(r'\*\*Age:\*\*\s*(\d+)', demo_text)
            if age_match:
                demographics['age'] = age_match.group(1)

            # Extract job
            job_match = re.search(r'\*\*Job:\*\*\s*(.+)', demo_text)
            if job_match:
                demographics['job'] = job_match.group(1).strip()

            # Extract location
            location_match = re.search(r'\*\*Location:\*\*\s*(.+)', demo_text)
            if location_match:
                demographics['location'] = location_match.group(1).strip()

            # Extract source audience
            source_match = re.search(r'\*\*Source Audience:\*\*\s*(.+)', demo_text)
            if source_match:
                demographics['source_audience'] = source_match.group(1).strip()

        return demographics

    def _extract_quote(self) -> str:
        """Extract the persona quote."""
        # Look for blockquote after demographics
        quote_match = re.search(r'>\s*"(.+?)"', self.content)
        if quote_match:
            return quote_match.group(1).strip()
        return ""

    def _extract_backstory(self) -> str:
        """Extract the backstory section."""
        backstory_match = re.search(
            r'##\s+Backstory\s*\n(.*?)(?=\n##|\n---|\Z)',
            self.content,
            re.DOTALL
        )

        if backstory_match:
            # Clean up the text
            text = backstory_match.group(1).strip()
            # Remove extra whitespace
            text = re.sub(r'\n+', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            return text

        return ""

    def _extract_section(self, section_name: str) -> str:
        """
        Extract text from an empathy map section.

        Args:
            section_name: Name of the section (e.g., 'Thinks & Feels')

        Returns:
            Combined text from all bullet points in the section.
        """
        # Escape special characters in section name
        escaped_name = re.escape(section_name)

        # Find the section
        section_match = re.search(
            rf'###\s+{escaped_name}\s*\n(.*?)(?=\n###|\n##|\n---|\Z)',
            self.content,
            re.DOTALL
        )

        if not section_match:
            return ""

        section_text = section_match.group(1)

        # Extract bullet points (lines starting with -)
        bullets = re.findall(r'-\s*"(.+?)"', section_text)

        if bullets:
            # Combine all bullet points
            return ' '.join(bullets)

        return ""


class CSVAudienceAnalyzer:
    """Analyzes CSV file to detect audiences and categories."""

    def __init__(self, csv_file_path: str):
        """Initialize analyzer with CSV file path."""
        self.csv_file_path = Path(csv_file_path)
        self.df = None
        self.audiences = []
        self.categories = {}

    def analyze(self) -> Tuple[List[str], Dict[str, List[str]]]:
        """
        Analyze CSV to detect audiences and categories.

        Returns:
            Tuple of (audience_names, categories_dict)
        """
        if not self.csv_file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_file_path}")

        # Try to read CSV with tab separator first
        try:
            self.df = pd.read_csv(self.csv_file_path, sep='\t')
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")

        # Validate we have enough columns
        if len(self.df.columns) < 2:
            raise ValueError(
                f"CSV file must have at least 2 columns (CAT and SUBCAT).\n"
                f"Found {len(self.df.columns)} column(s): {list(self.df.columns)}\n\n"
                f"Common issues:\n"
                f"  1. File is not tab-separated (must use tabs, not commas)\n"
                f"  2. File has wrong encoding\n"
                f"  3. First line should be headers: CAT, SUBCAT, then audience columns\n\n"
                f"Expected format:\n"
                f"  CAT<tab>SUBCAT<tab>Audience1_Minutes<tab>Audience1_Audience%<tab>...\n"
            )

        # Check for audience columns
        audience_cols = [col for col in self.df.columns if '_Audience%' in col or '_Index' in col]
        if len(audience_cols) == 0:
            raise ValueError(
                f"No audience columns found in CSV.\n"
                f"Column names must include '_Audience%' or '_Index'.\n"
                f"Found columns: {list(self.df.columns)}\n\n"
                f"Example column names: 'GenPop_Audience%', 'Battery Intenders_Index'\n"
            )

        # Detect audiences
        self.audiences = self._detect_audiences()

        # Get categories and subcategories
        self.categories = self._get_categories()

        return self.audiences, self.categories

    def _detect_audiences(self) -> List[str]:
        """Detect audience names from column headers."""
        audiences = set()

        for col in self.df.columns:
            # Look for columns ending in _Audience% or _Index
            if col.endswith('_Audience%') or col.endswith('_Index'):
                # Extract audience name
                audience_name = col.rsplit('_', 1)[0]
                audiences.add(audience_name)

        return sorted(list(audiences))

    def _get_categories(self) -> Dict[str, List[str]]:
        """Get categories and their subcategories from the CSV."""
        categories = {}

        # Assuming first column is CAT and second is SUBCAT
        cat_col = self.df.columns[0]
        subcat_col = self.df.columns[1]

        for _, row in self.df.iterrows():
            category = str(row[cat_col]).strip()
            subcategory = str(row[subcat_col]).strip()

            if category and category != 'nan':
                if category not in categories:
                    categories[category] = []

                if subcategory and subcategory != 'nan':
                    if subcategory not in categories[category]:
                        categories[category].append(subcategory)

        return categories


class ConfigGenerator:
    """Main configuration generator."""

    def __init__(self):
        """Initialize the generator."""
        self.csv_analyzer = None
        self.personas = []
        self.audiences = []
        self.categories = {}
        self.config = {
            'clientName': '',
            'personas': [],
            'charts': []
        }

    def run_interactive(self, csv_path: str, markdown_paths: List[str]):
        """
        Run the configuration generator interactively.

        Args:
            csv_path: Path to the CSV data file.
            markdown_paths: List of paths to markdown persona files.
        """
        print("=" * 60)
        print("AUDIENCE BOOK CONFIG GENERATOR")
        print("=" * 60)
        print()

        # Step 1: Analyze CSV
        print("Step 1: Analyzing CSV file...")
        self.csv_analyzer = CSVAudienceAnalyzer(csv_path)
        self.audiences, self.categories = self.csv_analyzer.analyze()

        print(f"  Found {len(self.audiences)} audiences:")
        for i, aud in enumerate(self.audiences, 1):
            print(f"    {i}. {aud}")
        print(f"  Found {len(self.categories)} categories")
        print()

        # Step 2: Parse markdown files
        print("Step 2: Parsing persona markdown files...")
        for md_path in markdown_paths:
            try:
                parser = MarkdownPersonaParser(md_path)
                persona_data = parser.parse()
                self.personas.append(persona_data)
                print(f"  ✓ Loaded: {persona_data['name']}")
            except Exception as e:
                print(f"  ✗ Error loading {md_path}: {str(e)}")

        print(f"  Loaded {len(self.personas)} personas")
        print()

        # Step 3: Get client name
        print("Step 3: Configuration")
        client_name = input("Enter client name: ").strip()
        if not client_name:
            client_name = "Client"
        self.config['clientName'] = client_name
        print()

        # Step 4: Map personas to template slots
        print("Step 4: Assigning personas to template slots...")
        for i, persona in enumerate(self.personas, 1):
            print(f"\nPersona {i}: {persona['name']}")
            print(f"  Age: {persona['age']}, Job: {persona['job']}")
            print(f"  Source Audience: {persona['source_audience']}")

            # Try to auto-match source audience
            csv_audience = self._find_matching_audience(persona['source_audience'])

            if csv_audience:
                print(f"  ✓ Matched to CSV audience: {csv_audience}")
            else:
                print(f"  ⚠ Could not auto-match. Available audiences:")
                for j, aud in enumerate(self.audiences, 1):
                    print(f"    {j}. {aud}")
                choice = input(f"  Select audience number (1-{len(self.audiences)}): ").strip()
                try:
                    csv_audience = self.audiences[int(choice) - 1]
                except (ValueError, IndexError):
                    print(f"  Invalid choice. Skipping persona.")
                    continue

            # Build persona config entry
            persona_config = {
                'templateSlot': i,
                'csvAudienceName': csv_audience,
                'qualitativeText': {
                    'Persona_Name': f"{persona['name'].split()[0]}, {persona['age']}",
                    'Persona_Title': persona['job'],
                    'Persona_Bio': persona['bio'],
                    'Thinks_Feels': persona['thinks_feels'],
                    'Sees': persona['sees'],
                    'Says_Does': persona['says_does'],
                    'Hears': persona['hears']
                }
            }

            self.config['personas'].append(persona_config)

        print()
        print(f"✓ Configured {len(self.config['personas'])} personas")
        print()

        # Step 5: Select charts
        print("Step 5: Selecting charts...")
        print("Available categories:")
        cat_list = list(self.categories.keys())
        for i, cat in enumerate(cat_list, 1):
            print(f"  {i}. {cat} ({len(self.categories[cat])} subcategories)")

        print()
        print("Enter chart selections (or press Enter to finish):")
        print("Format: <chart_number>,<category_number>,<title>")
        print("Example: 1,5,Social Media Usage")
        print()

        chart_slot = 1
        while True:
            selection = input(f"Chart {chart_slot} (or Enter to finish): ").strip()

            if not selection:
                break

            try:
                parts = selection.split(',', 2)
                if len(parts) != 3:
                    print("  Invalid format. Use: <chart_number>,<category_number>,<title>")
                    continue

                slot_num = int(parts[0].strip())
                cat_num = int(parts[1].strip())
                title = parts[2].strip()

                if cat_num < 1 or cat_num > len(cat_list):
                    print(f"  Invalid category number. Choose 1-{len(cat_list)}")
                    continue

                category = cat_list[cat_num - 1]
                subcategories = self.categories[category]

                # Show subcategories
                print(f"  Subcategories in '{category}':")
                for i, subcat in enumerate(subcategories, 1):
                    print(f"    {i}. {subcat}")

                subcat_input = input("  Select subcategories (comma-separated numbers, or 'all'): ").strip()

                selected_subcats = []
                if subcat_input.lower() == 'all':
                    selected_subcats = subcategories
                else:
                    indices = [int(x.strip()) - 1 for x in subcat_input.split(',')]
                    selected_subcats = [subcategories[i] for i in indices if 0 <= i < len(subcategories)]

                # Build chart config
                chart_config = {
                    'chartSlot': slot_num,
                    'title': title,
                    'category': category,
                    'subcategories': [
                        {'csvName': subcat, 'displayName': subcat}
                        for subcat in selected_subcats
                    ]
                }

                self.config['charts'].append(chart_config)
                print(f"  ✓ Added chart {slot_num}: {title} ({len(selected_subcats)} subcategories)")
                chart_slot += 1

            except (ValueError, IndexError) as e:
                print(f"  Error: {str(e)}")

        print()
        print(f"✓ Configured {len(self.config['charts'])} charts")
        print()

        # Step 6: Save config
        output_path = Path('config.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

        print("=" * 60)
        print("SUCCESS!")
        print(f"Configuration saved to: {output_path}")
        print()
        print("Summary:")
        print(f"  Client: {self.config['clientName']}")
        print(f"  Personas: {len(self.config['personas'])}")
        print(f"  Charts: {len(self.config['charts'])}")
        print()
        print("Next steps:")
        print("  1. Review config.json")
        print("  2. Run: python audience_book_updater.py")
        print("=" * 60)

    def _find_matching_audience(self, source_audience: str) -> str:
        """
        Try to find a matching audience name in the CSV.

        Args:
            source_audience: The source audience from markdown.

        Returns:
            Matched audience name or empty string.
        """
        if not source_audience:
            return ""

        # Try exact match
        if source_audience in self.audiences:
            return source_audience

        # Try case-insensitive match
        source_lower = source_audience.lower()
        for aud in self.audiences:
            if aud.lower() == source_lower:
                return aud

        # Try partial match
        for aud in self.audiences:
            if source_lower in aud.lower() or aud.lower() in source_lower:
                return aud

        return ""


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate config.json from CSV and markdown files'
    )
    parser.add_argument(
        'csv_file',
        help='Path to the CSV data file'
    )
    parser.add_argument(
        'markdown_files',
        nargs='+',
        help='Path(s) to persona markdown file(s)'
    )

    args = parser.parse_args()

    try:
        generator = ConfigGenerator()
        generator.run_interactive(args.csv_file, args.markdown_files)
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
