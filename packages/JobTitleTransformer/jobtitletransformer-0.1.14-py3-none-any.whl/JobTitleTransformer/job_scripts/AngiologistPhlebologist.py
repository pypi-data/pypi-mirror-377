import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for angiologist_phlebologist related titles
angiologist_phlebologist_variants = [
    r"(?i)\bAngiologist\b",
    r"(?i)\bPhlebologist\b",
    r"(?i)\bAngiologist Specialist\b",
    r"(?i)\bPhlebologist Specialist\b",
    r"(?i)\bVenous Disease Specialist\b",
    r"(?i)\bAngiologist Consultant\b",
    r"(?i)\bPhlebologist Consultant\b",
    r"(?i)\bAngiology - Aesthetic Medicine\b",
    r"(?i)\bAesthetic & Phlebolgy\b",
    r"(?i)\bPhlebotomist\b",
]

# Exact matches that should be updated
angiologist_phlebologist_exact_matches = {
    'Angiologist',
    'Phlebologist',
    'Angiologist Specialist',
    'Phlebologist Specialist',
    'Venous Disease Specialist',
    'Angiologist Consultant',
    'Phlebologist Consultant',
    'Phlebologist Specialist Doctor',

    # Case-related errors
    'angiologist',
    'phlebologist',
    'ANGIOLOGIST',
    'PHLEBOLOGIST',
    'AnGiOlOgIsT',
    'PhLeBoLoGiSt',

    # Common misspellings
    'Angilogist',
    'Phlebologist',
    'Angiolgist',
    'Phlebollogist',
    'Phlebologiist',
    'Phlebologistt',
    'Angiologyst',
    'Phlebolgist',
    'Angiologyst Specialist',
    'Phlebology Specialist',

    # Spanish-related exclusions
    'Angiólogo',
    'Flebólogo',
    'Especialista en Angiología',
    'Especialista en Flebología',
    'Médico Angiólogo',
    'Médico Flebólogo',
    'Especialista en Enfermedades Venosas',
    'Consultor de Angiología',
    'Consultor de Flebología',
}

# Define patterns for  & Resident & Professor (these should NOT be changed)
angiologist_phlebologist_exclusions = {
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

# Create a mask for Angiologist Phlebologist
mask_angiologist_phlebologist = df['speciality'].str.contains('|'.join(angiologist_phlebologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(angiologist_phlebologist_exact_matches)
mask_angiologist_phlebologist_exclusions = df['speciality'].isin(angiologist_phlebologist_exclusions)

# Final mask: Select Angiologist Phlebologist
mask_angiologist_phlebologist_final = mask_angiologist_phlebologist & ~mask_angiologist_phlebologist_exclusions

# Store the original values that will be replaced
original_angiologist_phlebologist_values = df.loc[mask_angiologist_phlebologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_angiologist_phlebologist_final, 'speciality'] = 'Angiologist Phlebologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Angiologist Phlebologist", 'green'))
print(df.loc[mask_angiologist_phlebologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_angiologist_phlebologist_values = df.loc[mask_angiologist_phlebologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Angiologist Phlebologist", "cyan"))
for original_angiologist_phlebologist_value in original_angiologist_phlebologist_values:
    print(f"✅ {original_angiologist_phlebologist_value} → Angiologist Phlebologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Angiologist Phlebologist:", 'red'))
print(grouped_angiologist_phlebologist_values)

# Print summary
matched_count_angiologist_phlebologist = mask_angiologist_phlebologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Angiologist Phlebologist: "
        f"{matched_count_angiologist_phlebologist}",
        'red'))