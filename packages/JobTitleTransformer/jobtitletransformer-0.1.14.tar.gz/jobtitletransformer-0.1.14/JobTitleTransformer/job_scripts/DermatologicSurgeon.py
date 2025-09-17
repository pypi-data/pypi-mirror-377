import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Dermatologic Surgeon related titles

dermatologic_surgeon_variants = [
    r"(?i)\bdermatologic\s?surgeon\b",
    r"(?i)\bdermatolog\s?surgeon\b",
    r"(?i)\bdermatologic\s?surgon\b",
    r"(?i)\bdermatolgist\s?surgeon\b",
    r"(?i)\bdermatolog\s?surgeon\b",
    r"(?i)\bsurgeon\s?dermatologico\b",
    r"(?i)\bcirujano\s?dermatologico\b",
    r"(?i)\bcirujano\s?dermatologo\b",
    r"(?i)\bdoctor\s?dermatologic\s?surgeon\b",
    r"(?i)\bdermatologic\s?surgical\s?specialist\b",
    r"(?i)\bboard\s?certified\s?dermatologic\s?surgeon\b",
    r"(?i)\bDermatologic Surgery\b",
    r"(?i)\bDermatological Surgery\b",
    r"(?i)\bDermatologistDermatopathologistDermatologic Surgeon\b",
    r"(?i)\bDermatology & Aesthetic Surgery\b",
    r"(?i)\bCirujana Dermatologa\b",
]

# Exact matches that should be updated
dermatologic_surgeon_exact_matches = {
    "Dermatologic Surgeon",
    "Dermatology Surgeon",
    "Dermatologist Surgeon",
    "Dermatologic Surgeons",
    "Dermatologic Surgoen",
    "Dermatoligic Surgeon",
    "Dermatologic Surgion",
    "DERMATOLOGIC SURGEON",
    "dermatologic surgeon",
    "Dr. Dermatologic Surgeon",
    "Board-Certified Dermatologic Surgeon",
    "Board Certified Dermatologic Surgeon",
    "Cirujano Dermatológico",
    "Cirujano Dermatologista",
    "Cirujano dermatológico",
    "Dr. Cirujano Dermatológico",
    "Dr. [Board-Certified Dermatologic Surgeon]",
    'Clinical Dermatology & Aesthetics',
    'CiruDerm',
}

# Define patterns (these should NOT be changed)
dermatologic_surgeon_exclusions = {
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
    'Aesthetic Resident'
}

# Create a mask for Dermatologic Surgeon
mask_dermatologic_surgeon = df['speciality'].str.contains('|'.join(dermatologic_surgeon_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(dermatologic_surgeon_exact_matches)
mask_dermatologic_surgeon_exclusions = df['speciality'].isin(dermatologic_surgeon_exclusions)

# Final mask: Select Dermatologic Surgeon
mask_dermatologic_surgeon_final = mask_dermatologic_surgeon & ~mask_dermatologic_surgeon_exclusions

# Store the original values that will be replaced
original_dermatologic_surgeon_values = df.loc[mask_dermatologic_surgeon_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_dermatologic_surgeon_final, 'speciality'] = 'Dermatologic Surgeon'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Dermatologic Surgeon", 'green'))
print(df.loc[mask_dermatologic_surgeon_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_dermatologic_surgeon_values = df.loc[mask_dermatologic_surgeon_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Dermatologic Surgeon", "cyan"))
for original_dermatologic_surgeon_value in original_dermatologic_surgeon_values:
    print(f"✅ {original_dermatologic_surgeon_value} → Dermatologic Surgeon")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Dermatologic Surgeon:", 'red'))
print(grouped_dermatologic_surgeon_values)

# Print summary
matched_count_dermatologic_surgeon = mask_dermatologic_surgeon_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Dermatologic Surgeon: "
        f"{matched_count_dermatologic_surgeon}",
        'red'))