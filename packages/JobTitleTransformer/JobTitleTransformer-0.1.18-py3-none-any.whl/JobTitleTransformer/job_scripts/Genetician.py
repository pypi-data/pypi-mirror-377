import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Genetician related titles

genetician_variants = [
    r"(?i)\bGenetician\b",
    r"(?i)\bGenetician\s?Specialist\b",
    r"(?i)\bBoard\s?Certified\s?Genetician\b",
    r"(?i)\bCertified\s?Genetician\b",

    # Spanish variants
    r"(?i)\bGenetista\b",
    r"(?i)\bEspecialista\s?en\s?Genética\b",
    r"(?i)\bGenetista\s?Médico\b",

    # Other possible variations
    r"(?i)\bDoctor\s?Genetician\b",
    r"(?i)\bDoctor\s?en\s?Genética\b",
    r"(?i)\bGenetics\s?Specialist\b",
    r"(?i)\bGenetics\s?Doctor\b",
    r"(?i)\bGenetic\s?Physician\b",
    r"(?i)\bLicensed\s?Genetician\b",
    r"(?i)\bGeneticista\b",
]

# Exact matches that should be updated
genetician_exact_matches = {
    "Genetician",
    "Genetician Specialist",
    "Board Certified Genetician",
    "Certified Genetician",
    # Spanish form matches
    "Genetista",
    "Especialista en Genética",
    "Genetista Médico",
    # Other possible variations
    "Doctor Genetician",
    "Doctor en Genética",
    "Genetics Specialist",
    "Genetics Doctor",
    "Genetic Physician",
    "Licensed Genetician",
}

# Define patterns (these should NOT be changed)
genetician_exclusions = {
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

# Create a mask for Genetician
mask_genetician = df['speciality'].str.contains('|'.join(genetician_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(genetician_exact_matches)
mask_genetician_exclusions = df['speciality'].isin(genetician_exclusions)

# Final mask: Select Genetician
mask_genetician_final = mask_genetician & ~mask_genetician_exclusions

# Store the original values that will be replaced
original_genetician_values = df.loc[mask_genetician_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_genetician_final, 'speciality'] = 'Genetician'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Genetician", 'green'))
print(df.loc[mask_genetician_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_genetician_values = df.loc[mask_genetician_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Genetician", "cyan"))
for original_genetician_value in original_genetician_values:
    print(f"✅ {original_genetician_value} → Genetician")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Genetician:", 'red'))
print(grouped_genetician_values)

# Print summary
matched_count_genetician = mask_genetician_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Genetician: "
        f"{matched_count_genetician}",
        'red'))