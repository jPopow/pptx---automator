#!/usr/bin/env python3
"""
Configuration Validator for Audience Book Updater

This script validates the config.json file to catch common errors before running the main script.
"""

import json
import sys
from pathlib import Path


class ConfigValidator:
    """Validates the config.json file structure and content."""

    def __init__(self, config_path='config.json'):
        """Initialize the validator."""
        self.config_path = Path(config_path)
        self.config = None
        self.errors = []
        self.warnings = []

    def load_config(self):
        """Load the config file."""
        if not self.config_path.exists():
            self.errors.append(f"Config file not found: {self.config_path}")
            return False

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON syntax: {str(e)}")
            return False
        except Exception as e:
            self.errors.append(f"Error loading config: {str(e)}")
            return False

    def validate_structure(self):
        """Validate the basic structure of the config."""
        if not isinstance(self.config, dict):
            self.errors.append("Config must be a JSON object")
            return False

        # Check required top-level keys
        if 'clientName' not in self.config:
            self.errors.append("Missing required field: 'clientName'")

        if 'personas' not in self.config:
            self.errors.append("Missing required field: 'personas'")
        elif not isinstance(self.config['personas'], list):
            self.errors.append("'personas' must be an array")

        if 'charts' not in self.config:
            self.warnings.append("No 'charts' field found - no charts will be populated")

        return len(self.errors) == 0

    def validate_personas(self):
        """Validate the personas configuration."""
        personas = self.config.get('personas', [])

        if len(personas) == 0:
            self.warnings.append("No personas configured - output will be empty")
            return True

        template_slots = set()

        for i, persona in enumerate(personas):
            persona_num = i + 1

            # Check required fields
            if 'templateSlot' not in persona:
                self.errors.append(f"Persona {persona_num}: Missing 'templateSlot'")
                continue

            if 'csvAudienceName' not in persona:
                self.errors.append(f"Persona {persona_num}: Missing 'csvAudienceName'")

            if 'qualitativeText' not in persona:
                self.errors.append(f"Persona {persona_num}: Missing 'qualitativeText'")
            elif not isinstance(persona['qualitativeText'], dict):
                self.errors.append(f"Persona {persona_num}: 'qualitativeText' must be an object")

            # Check for duplicate template slots
            slot = persona.get('templateSlot')
            if slot in template_slots:
                self.errors.append(f"Persona {persona_num}: Duplicate templateSlot {slot}")
            else:
                template_slots.add(slot)

            # Validate qualitative text fields
            qual_text = persona.get('qualitativeText', {})
            if len(qual_text) == 0:
                self.warnings.append(f"Persona {persona_num}: No qualitative text fields defined")

        return len(self.errors) == 0

    def validate_charts(self):
        """Validate the charts configuration."""
        charts = self.config.get('charts', [])

        if len(charts) == 0:
            return True  # Already warned in structure validation

        chart_slots = set()

        for i, chart in enumerate(charts):
            chart_num = i + 1

            # Check required fields
            if 'chartSlot' not in chart:
                self.errors.append(f"Chart {chart_num}: Missing 'chartSlot'")
                continue

            if 'title' not in chart:
                self.errors.append(f"Chart {chart_num}: Missing 'title'")

            if 'category' not in chart:
                self.errors.append(f"Chart {chart_num}: Missing 'category'")

            if 'subcategories' not in chart:
                self.errors.append(f"Chart {chart_num}: Missing 'subcategories'")
            elif not isinstance(chart['subcategories'], list):
                self.errors.append(f"Chart {chart_num}: 'subcategories' must be an array")
            else:
                # Validate subcategories
                subcats = chart['subcategories']
                if len(subcats) == 0:
                    self.warnings.append(f"Chart {chart_num}: No subcategories defined")

                for j, subcat in enumerate(subcats):
                    if not isinstance(subcat, dict):
                        self.errors.append(f"Chart {chart_num}, Subcat {j+1}: Must be an object")
                        continue

                    if 'csvName' not in subcat:
                        self.errors.append(f"Chart {chart_num}, Subcat {j+1}: Missing 'csvName'")

                    if 'displayName' not in subcat:
                        self.errors.append(f"Chart {chart_num}, Subcat {j+1}: Missing 'displayName'")

            # Check for duplicate chart slots
            slot = chart.get('chartSlot')
            if slot in chart_slots:
                self.errors.append(f"Chart {chart_num}: Duplicate chartSlot {slot}")
            else:
                chart_slots.add(slot)

        return len(self.errors) == 0

    def validate(self):
        """Run all validation checks."""
        print("Validating configuration file...")
        print()

        # Load config
        if not self.load_config():
            return False

        # Run validation checks
        self.validate_structure()
        self.validate_personas()
        self.validate_charts()

        # Print results
        if self.errors:
            print("❌ VALIDATION FAILED")
            print()
            print("Errors:")
            for error in self.errors:
                print(f"  • {error}")
            print()

        if self.warnings:
            print("⚠️  WARNINGS")
            print()
            for warning in self.warnings:
                print(f"  • {warning}")
            print()

        if not self.errors and not self.warnings:
            print("✓ Configuration is valid!")
            print()

        if not self.errors and self.warnings:
            print("✓ Configuration is valid (with warnings)")
            print()

        # Print summary
        print("Summary:")
        print(f"  • Client: {self.config.get('clientName', 'N/A')}")
        print(f"  • Personas: {len(self.config.get('personas', []))}")
        print(f"  • Charts: {len(self.config.get('charts', []))}")
        print()

        return len(self.errors) == 0


def main():
    """Main entry point."""
    print("=" * 60)
    print("CONFIG VALIDATOR")
    print("=" * 60)
    print()

    validator = ConfigValidator()
    is_valid = validator.validate()

    if is_valid:
        print("✓ Ready to run audience_book_updater.py")
        sys.exit(0)
    else:
        print("✗ Please fix the errors above before running the updater")
        sys.exit(1)


if __name__ == "__main__":
    main()
