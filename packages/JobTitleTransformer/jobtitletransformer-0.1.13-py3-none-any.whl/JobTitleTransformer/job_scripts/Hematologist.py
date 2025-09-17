import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Hematologist related titles

hematologist_variants = [
    r"(?i)\bHematologist\b",  # Standard title

    # Common misspellings and case errors
    r"(?i)\bHaematologist\b",
    r"(?i)\bHematoligst\b",
    r"(?i)\bHemotologist\b",
    r"(?i)\bHematlogist\b",
    r"(?i)\bHematolgist\b",
    r"(?i)\bHematoloigst\b",

    # Spanish variants
    r"(?i)\bHematólogo\b",
    r"(?i)\bEspecialista\s?en\s?Hematología\b",

    # Other possible variations
    r"(?i)\bBlood\s?Doctor\b",
    r"(?i)\bHematology\s?Specialist\b",
    r"(?i)\bDoctor\s?of\s?Hematology\b",
    r"(?i)\bHematology\s?Consultant\b",
]

# Exact matches that should be updated
hematologist_exact_matches = {
    "Hematologist",
    "Haematologist",
    "Hematoligst",
    "Hemotologist",
    "Hematlogist",
    "Hematolgist",
    "Hematoloigst",
    # Spanish variants
    "Hematólogo",
    "Especialista en Hematología",
    # Other possible variations
    "Blood Doctor",
    "Hematology Specialist",
    "Doctor of Hematology",
    "Hematology Consultant",
    'Hematology',
}

# Define patterns (these should NOT be changed)
hematologist_exclusions = {
    'Resident',
    'resident',
    'student',
    'Trainee',
    'Resident Doctor',
    'Resident ooPhysician',
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

# Create a mask for Hematologist
mask_hematologist = df['speciality'].str.contains('|'.join(hematologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(hematologist_exact_matches)
mask_hematologist_exclusions = df['speciality'].isin(hematologist_exclusions)

# Final mask: Select Hematologist
mask_hematologist_final = mask_hematologist & ~mask_hematologist_exclusions

# Store the original values that will be replaced
original_hematologist_values = df.loc[mask_hematologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_hematologist_final, 'speciality'] = 'Hematologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Hematologist", 'green'))
print(df.loc[mask_hematologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_hematologist_values = df.loc[mask_hematologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Hematologist", "cyan"))
for original_hematologist_value in original_hematologist_values:
    print(f"✅ {original_hematologist_value} → Hematologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Hematologist:", 'red'))
print(grouped_hematologist_values)

# Print summary
matched_count_hematologist = mask_hematologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Hematologist: "
        f"{matched_count_hematologist}",
        'red'))