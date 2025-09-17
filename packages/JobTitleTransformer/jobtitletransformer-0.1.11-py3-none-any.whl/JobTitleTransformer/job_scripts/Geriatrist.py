import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Geriatrist related titles

geriatrist_variants = [
    r"(?i)\bGeriatrist\b",

    # Common misspellings and case errors
    r"(?i)\bGeritrist\b",
    r"(?i)\bGeriatrist\b",
    r"(?i)\bGeriatirist\b",
    r"(?i)\bGeriatrician\b",

    # Spanish variants
    r"(?i)\bGeriatra\b",
    r"(?i)\bEspecialista\s?en\s?Geriatría\b",
    r"(?i)\bMédico\s?Geriatra\b",

    # Other possible variations
    r"(?i)\bDoctor\s?Geriatrist\b",
    r"(?i)\bDoctor\s?en\s?Geriatría\b",
    r"(?i)\bGeriatric\s?Specialist\b",
    r"(?i)\bGeriatric\s?Physician\b",
    r"(?i)\bLicensed\s?Geriatrist\b",
    r"(?i)Geriatrics",
]

# Exact matches that should be updated
geriatrist_exact_matches = {
    "Geriatrist",
    "Geritrist",
    "Geriatirist",
    "Geriatrician",
    "Geriatra",
    "Especialista en Geriatría",
    "Médico Geriatra",
    # Other possible variations
    "Doctor Geriatrist",
    "Doctor en Geriatría",
    "Geriatric Specialist",
    "Geriatric Physician",
    "Licensed Geriatrist",
    'Geriatry Antiaging Laser',
}

# Define patterns (these should NOT be changed)
geriatrist_exclusions = {
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

# Create a mask for Geriatrist
mask_geriatrist = df['speciality'].str.contains('|'.join(geriatrist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(geriatrist_exact_matches)
mask_geriatrist_exclusions = df['speciality'].isin(geriatrist_exclusions)

# Final mask: Select Geriatrist
mask_geriatrist_final = mask_geriatrist & ~mask_geriatrist_exclusions

# Store the original values that will be replaced
original_geriatrist_values = df.loc[mask_geriatrist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_geriatrist_final, 'speciality'] = 'Geriatrist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Geriatrist", 'green'))
print(df.loc[mask_geriatrist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_geriatrist_values = df.loc[mask_geriatrist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Geriatrist", "cyan"))
for original_geriatrist_value in original_geriatrist_values:
    print(f"✅ {original_geriatrist_value} → Geriatrist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Geriatrist:", 'red'))
print(grouped_geriatrist_values)

# Print summary
matched_count_geriatrist = mask_geriatrist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Geriatrist: "
        f"{matched_count_geriatrist}",
        'red'))