import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Cytologist related titles

cytologist_variants = [
    # Standard title variations
    r"(?i)\bCytologist\b",
    r"(?i)\bCytology\s?Specialist\b",
    r"(?i)\bCytotechnologist\b",
    r"(?i)\bClinical\s?Cytologist\b",
    r"(?i)\bMedical\s?Cytologist\b",

    # Common misspellings and case mistakes
    r"(?i)\bCyotologist\b",
    r"(?i)\bCytoligist\b",
    r"(?i)\bCytolologist\b",
    r"(?i)\bCytoligyst\b",

    # Variants in Spanish and other languages
    r"(?i)\bCitólogo\b",
    r"(?i)\bEspecialista\s?en\s?Citología\b",
    r"(?i)\bTécnico\s?en\s?Citología\b",

    # Other possible variations
    r"(?i)\bBoard\s?-?\s?Certified\s?Cytologist\b",
    r"(?i)\bPathology\s?Cytologist\b",
    r"(?i)\bDiagnostic\s?Cytologist\b",
]

# Exact matches that should be updated
cytologist_exact_matches = {
    r"(?i)\bCyotologist\b",
    r"(?i)\bCytoligist\b",
    r"(?i)\bCytolologist\b",
    r"(?i)\bCytoligyst\b",
    r"(?i)\bCitólogo\b",
    r"(?i)\bEspecialista\s?en\s?Citología\b",
    r"(?i)\bTécnico\s?en\s?Citología\b",
}

# Define patterns (these should NOT be changed)
cytologist_exclusions = {
    'Resident',
    'resident',
    'student',
    'Trainee',
    'Resident Doctor',
    'Resident Physician',
    'Intern',
    'intern',
    'Medical Intern',
    'Fellow',
    'fellow',
    'Clinical Fellow',
    'Medical Student',
    'Clinical Trainee',
    'Trainee Doctor',
    'Trainee Physician',
    'Junior Doctor',
    'Postgraduate Trainee',
    'Aesthetic Fellow',
    'Aesthetic Trainee',
    'Aesthetic Medicine Fellow',
    'Aesthetic Resident',
}

# Create a mask for cytologist
mask_cytologist = df['speciality'].str.contains('|'.join(cytologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(cytologist_exact_matches)
mask_cytologist_exclusions = df['speciality'].isin(cytologist_exclusions)

# Final mask: Select cytologist
mask_cytologist_final = mask_cytologist & ~mask_cytologist_exclusions

# Store the original values that will be replaced
original_cytologist_values = df.loc[mask_cytologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_cytologist_final, 'speciality'] = 'Cytologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Cytologist", 'green'))
print(df.loc[mask_cytologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_cytologist_values = df.loc[mask_cytologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Cytologist", "cyan"))
for original_cytologist_value in original_cytologist_values:
    print(f"✅ {original_cytologist_value} → Cytologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Cytologist:", 'red'))
print(grouped_cytologist_values)

# Print summary
matched_count_cytologist = mask_cytologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Cytologist: "
        f"{matched_count_cytologist}",
        'red'))