import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Gynecologist Obstetrician related titles

gynecologist_variants = [
    r"(?i)\bGynecologist\s?Obstetrician\b",

    # Common misspellings and case errors
    r"(?i)\bGynaecologist\s?Obstetrician\b",
    r"(?i)\bGynecologist\s?Obstetrician\b",
    r"(?i)\bGynecologis\s?Obstetrician\b",
    r"(?i)\bObstetrician\s?Gynecologist\b",
    r"(?i)\bGynecologist\b",
    r"(?i)\bGynecology\b",
    r"(?i)\bObstetrician\b",
    r"(?i)\bObgyn\b",
    r"(?i)\bGynaecologist\b",

    # Spanish variants
    r"(?i)\bGinecólogo\s?Obstetra\b",
    r"(?i)\bGinecóloga\s?Obstetra\b",
    r"(?i)\bMédico\s?Ginecólogo\s?Obstetra\b",

    # Other possible variations
    r"(?i)\bDoctor\s?Gynecologist\s?Obstetrician\b",
    r"(?i)\bObstetrics\s?Gynecology\s?Specialist\b",
    r"(?i)\bOB/GYN\b",
    r"(?i)\bOB-GYN\b",
    r"(?i)\bBoard-Certified\s?Gynecologist\s?Obstetrician\b",
    r"(?i)Gynecologyst",
    r"(?i)\bMedica Ginecologista\b",
    r"(?i)Ginecologista",
    r"(?i)\bMedico Ginecologista E Obstetra\b",
    r"(?i)Obstetra",
    r"(?i)Gynecologogist",
    r"(?i)Consultantobstetricsgynecology",
    r"(?i)Ob Gyn",
    r"(?i)\bHpv\b",
    r"(?i)Gynaecology",
    r"(?i)Gynecologie",
    r"(?i)Gynecolog",
    r"(?i)Gynecologue",
    r"(?i)\bObs\b",
    r"(?i)Ginecologia",
    r"(?i)\bGynecology Esthetic Medicine\b",
    r"(?i)\bObgy\b",
    r"(?i)\bObstetrics & Gynaecology\b",
    r"(?i)\bObs&Gyne\b",
]

# Exact matches that should be updated
gynecologist_exact_matches = {
    "Gynecologist Obstetrician",
    "Gynaecologist Obstetrician",
    "Gynecologis Obstetrician",
    "Obstetrician Gynecologist",
    "Ginecólogo Obstetra",
    "Ginecóloga Obstetra",
    "Médico Ginecólogo Obstetra",
    # Other possible variations
    "Doctor Gynecologist Obstetrician",
    "Obstetrics Gynecology Specialist",
    "OB/GYN",
    "OB-GYN",
    "Board-Certified Gynecologist Obstetrician",
    'Hpv',
    'HPV',
    'Ob Gyn',
    'GYN',
    'Gyn',
    'obgyn',
    'OB GYN',
    'Gynakologie',
    'GynObst',
    'Rural Obstetrics'
    'Jinekolog',
    'MacDecins GynacCologue Esthetique',
    'Ginecologo',
    'Ginecologa',
    'Obg Spescialist',
    'Gyneco-Oncology',
    'Gin obst',
}

# Define patterns (these should NOT be changed)
gynecologist_exclusions = {
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
    'Obgyn Physician Recruiter',
}

# Create a mask for Gynecologist Obstetrician
mask_gynecologist = df['speciality'].str.contains('|'.join(gynecologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(gynecologist_exact_matches)
mask_gynecologist_exclusions = df['speciality'].isin(gynecologist_exclusions)

# Final mask: Select Gynecologist Obstetrician
mask_gynecologist_final = mask_gynecologist & ~mask_gynecologist_exclusions

# Store the original values that will be replaced
original_gynecologist_values = df.loc[mask_gynecologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_gynecologist_final, 'speciality'] = 'Gynecologist Obstetrician'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Gynecologist Obstetrician", 'green'))
print(df.loc[mask_gynecologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_gynecologist_values = df.loc[mask_gynecologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Gynecologist Obstetrician", "cyan"))
for original_gynecologist_value in original_gynecologist_values:
    print(f"✅ {original_gynecologist_value} → Gynecologist Obstetrician")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Gynecologist Obstetrician:", 'red'))
print(grouped_gynecologist_values)

# Print summary
matched_count_gynecologist = mask_gynecologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Gynecologist Obstetrician: "
        f"{matched_count_gynecologist}",
        'red'))