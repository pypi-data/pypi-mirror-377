import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Hair Transplant Surgeon related titles

hair_transplant_variants = [
    r"(?i)\bHair\s?Transplant\s?Surgeon\b",
    r"(?i)\bHair\s?Transplant\b",
    r"(?i)\bHair Transplant\b",
    r"(?i)\bHair Surgery\b",
    r"(?i)\bHair Restoration\b",
    r"(?i)\bCirujana Capilar\b",

    # Common misspellings and case errors
    r"(?i)\bHair\s?Transplante\s?Surgeon\b",
    r"(?i)\bHair\s?Transplant\s?Surgen\b",
    r"(?i)\bHair\s?Transplant\s?Surgon\b",
    r"(?i)\bHair\s?Transplant\s?Surgeon\b",

    # Spanish variants
    r"(?i)\bCirujano\s?de\s?Trasplante\s?Capilar\b",
    r"(?i)\bCirujano\s?de\s?Implante\s?Capilar\b",

    # Other possible variations
    r"(?i)\bDoctor\s?Hair\s?Transplant\s?Surgeon\b",
    r"(?i)\bBoard-Certified\s?Hair\s?Transplant\s?Surgeon\b",
    r"(?i)\bHair\s?Restoration\s?Surgeon\b",
    r"(?i)\bHair\s?Transplant\s?Specialist\b",
]

# Exact matches that should be updated
hair_transplant_exact_matches = {
    "Hair Transplant Surgeon",
    "Hair Transplante Surgeon",
    "Hair Transplant Surgen",
    "Hair Transplant Surgon",
    "Cirujano de Trasplante Capilar",
    "Cirujano de Implante Capilar",
    # Other possible variations
    "Doctor Hair Transplant Surgeon",
    "Board-Certified Hair Transplant Surgeon",
    "Hair Restoration Surgeon",
    "Hair Transplant Specialist",
    'Greviste Manifestant',
}

# Define patterns (these should NOT be changed)
hair_transplant_exclusions = {
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

# Create a mask for Hair Transplant Surgeon
mask_hair_transplant = df['speciality'].str.contains('|'.join(hair_transplant_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(hair_transplant_exact_matches)
mask_hair_transplant_exclusions = df['speciality'].isin(hair_transplant_exclusions)

# Final mask: Select Hair Transplant Surgeon
mask_hair_transplant_final = mask_hair_transplant & ~mask_hair_transplant_exclusions

# Store the original values that will be replaced
original_hair_transplant_values = df.loc[mask_hair_transplant_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_hair_transplant_final, 'speciality'] = 'Hair Transplant Surgeon'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Hair Transplant Surgeon", 'green'))
print(df.loc[mask_hair_transplant_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_hair_transplant_values = df.loc[mask_hair_transplant_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Hair Transplant Surgeon", "cyan"))
for original_hair_transplant_value in original_hair_transplant_values:
    print(f"✅ {original_hair_transplant_value} → Hair Transplant Surgeon")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Hair Transplant Surgeon:", 'red'))
print(grouped_hair_transplant_values)

# Print summary
matched_count_hair_transplant = mask_hair_transplant_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Hair Transplant Surgeon: "
        f"{matched_count_hair_transplant}",
        'red'))