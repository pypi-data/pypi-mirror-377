import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for andrologist related titles
andrologist_variants = [
    r"(?i)\bAndrologist\b",
    r"(?i)\bAndrology Specialist\b",
    r"(?i)\bAndrology Doctor\b",
    r"(?i)\bAndrology Consultant\b",
    r"(?i)\bAndrology Expert\b",
    r"(?i)\bMale Reproductive Specialist\b",
    r"(?i)\bMen’s Health Specialist\b",
    r"(?i)\bMale Fertility Doctor\b",
    r"(?i)\bAndrology Researcher\b",
]

# Exact matches that should be updated
andrologist_exact_matches = {
    'Andrologist',
    'Andrology Specialist',
    'Andrology Doctor',
    'Andrology Consultant',
    'Andrology Expert',
    'Male Reproductive Specialist',
    'Men’s Health Specialist',
    'Male Fertility Doctor',
    'Andrology Researcher',
    'Clinical Andrologist',
    'Reproductive Andrologist',
    'Surgical Andrologist',
    'Medical Andrologist',

    # Case-related errors
    'andrologist',
    'ANDROLOGIST',
    'AnDrOlOgIsT',
    'ANDROLOgist',
    'aNDROLOGIST',

    # Common misspellings
    'Androlgist',
    'Androlgist',
    'Andorlogist',
    'Andoroligst',
    'Andorologist',
    'Androlgist',
    'Andorlogy Specialist',
    'Androlagist',
    'Androlegist',

    # Spanish-related exclusions
    'Andrólogo',
    'Especialista en Andrología',
    'Médico Andrólogo',
    'Consultor en Andrología',
    'Investigador en Andrología',
    'Experto en Andrología',
    'Doctor en Andrología',
    'Especialista en Salud Masculina',
    'Especialista en Reproducción Masculina',
}

# Define patterns for  & Resident & Professor (these should NOT be changed)
andrologist_exclusions = {
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

# Create a mask for Andrologist
mask_andrologist = df['speciality'].str.contains('|'.join(andrologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(andrologist_exact_matches)
mask_andrologist_exclusions = df['speciality'].isin(andrologist_exclusions)

# Final mask: Select Andrologist
mask_andrologist_final = mask_andrologist & ~mask_andrologist_exclusions

# Store the original values that will be replaced
original_andrologist_values = df.loc[mask_andrologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_andrologist_final, 'speciality'] = 'Andrologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Andrologist", 'green'))
print(df.loc[mask_andrologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_andrologist_values = df.loc[mask_andrologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Andrologist", "cyan"))
for original_andrologist_value in original_andrologist_values:
    print(f"✅ {original_andrologist_value} → Andrologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Andrologist:", 'red'))
print(grouped_andrologist_values)

# Print summary
matched_count_andrologist = mask_andrologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Andrologist: "
        f"{matched_count_andrologist}",
        'red'))