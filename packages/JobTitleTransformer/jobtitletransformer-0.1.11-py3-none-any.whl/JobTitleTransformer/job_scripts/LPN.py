import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Licensed Practical Nurse (LPN) related titles

LPN_variants = [
    r"(?i)\bLicensed\s?Practical\s?Nurse\s?(LPN)?\b",
    r"(?i)\bPractical\s?Nurse\s?(LPN)?\b"
    r"(?i)\bLPN\b",
    r"(?i)\bLicensed\s?Nurse\s?(LPN)?\b",
    r"(?i)\b(LPN)\b",
    r"(?i)\bNursing\s?Assistant\s?(LPN)?\b",

    # Misspellings and case errors
    r"(?i)\bLicensd\s?Practical\s?Nurse\b",
    r"(?i)\bLicsensed\s?Practical\s?Nurse\b",
    r"(?i)\bLicensed\s?Pratical\s?Nurse\b",
    r"(?i)\bLicenced\s?Practical\s?Nurse\b",
    r"(?i)\bLicensed\s?Practical\s?Ners\b",
    r"(?i)\bLiceneced\s?Practical\s?Nurse\b",

    # Spanish variants
    r"(?i)\bEnfermero\s?Práctico\s?Licenciado\b",
    r"(?i)\bEnfermera\s?Práctica\s?Licenciada\b",
    r"(?i)\bEnfermero\s?Práctico\s?(LPN)?\b",
    r"(?i)\bEnfermera\s?Práctica\s?(LPN)?\b",
    r"(?i)\bAuxiliar\s?De\s?Enfermería\s?Licenciado\b",

    # Other possible variations
    r"(?i)\bLicensed\s?Practical\s?Nursing\s?Assistant\b",
    r"(?i)\bLPN\s?Assistant\b",
    r"(?i)\bLicensed\s?Practical\s?Health\s?Assistant\b",
    r"(?i)\bLPN\s?Nurse\b",
    r"(?i)\bPractical\s?Nursing\s?Technician\b",
    r"(?i)\bLPN\s?Technician\b",
    r"(?i)\bPractical\s?Nurse\s?Technician\b",

    r"(?i)\bLPN\b",
    r"(?i)\bLicensed Practical Nurse\b",
]

# Exact matches that should be updated
LPN_exact_matches = {
    "Licensed Practical Nurse (LPN)",
    "Licensed Practical Nurse",
    "LPN",
    "Practical Nurse (LPN)",
    "Licensed Nurse (LPN)",
    "Registered Nurse (LPN)",
    "Nurse (LPN)",
    "Nursing Assistant (LPN)",
    # Misspellings and case errors
    "Licensd Practical Nurse",
    "Licsensed Practical Nurse",
    "Licensed Pratical Nurse",
    "Licenced Practical Nurse",
    "Licensed Practical Ners",
    "Liceneced Practical Nurse",
    # Spanish variants
    "Enfermero Práctico Licenciado",
    "Enfermera Práctica Licenciada",
    "Enfermero Práctico (LPN)",
    "Enfermera Práctica (LPN)",
    "Auxiliar De Enfermería Licenciado",
    # Other possible variations
    "Licensed Practical Nursing Assistant",
    "LPN Assistant",
    "Licensed Practical Health Assistant",
    "LPN Nurse",
    "Practical Nursing Technician",
    "LPN Technician",
    "Practical Nurse Technician",
    'Registered Practical Nurse',
}

# Define patterns (these should NOT be changed)
LPN_exclusions = {
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

# Create a mask for Licensed Practical Nurse (LPN)
mask_LPN = df['speciality'].str.contains('|'.join(LPN_variants), case = False, na = False, regex = True) | \
                            df['speciality'].isin(LPN_exact_matches)
mask_LPN_exclusions = df['speciality'].isin(LPN_exclusions)

# Final mask: Select Licensed Practical Nurse (LPN)
mask_LPN_final = mask_LPN & ~mask_LPN_exclusions

# Store the original values that will be replaced
original_LPN_values = df.loc[mask_LPN_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_LPN_final, 'speciality'] = 'Licensed Practical Nurse (LPN)'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Licensed Practical Nurse (LPN)", 'green'))
print(df.loc[mask_LPN_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_LPN_values = df.loc[mask_LPN_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Licensed Practical Nurse (LPN)", "cyan"))
for original_LPN_value in original_LPN_values:
    print(f"✅ {original_LPN_value} → Licensed Practical Nurse (LPN)")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Licensed Practical Nurse (LPN):", 'red'))
print(grouped_LPN_values)

# Print summary
matched_count_LPN = mask_LPN_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Licensed Practical Nurse (LPN): "
        f"{matched_count_LPN}",
        'red'))