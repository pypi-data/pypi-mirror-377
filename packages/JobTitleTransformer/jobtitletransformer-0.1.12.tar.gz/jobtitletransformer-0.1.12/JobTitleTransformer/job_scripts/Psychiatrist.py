import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Psychiatrist related titles

psychiatrist_variants = [
    # Standard Titles & Variants
    r"(?i)\bPsychiatrist\b",
    r"(?i)\bPsychiatric Doctor\b",
    r"(?i)\bDoctor of Psychiatry\b",
    r"(?i)\bMD Psychiatry\b",
    r"(?i)\bMental Health Doctor\b",
    r"(?i)\bPsychiatry Specialist\b",
    r"(?i)\bPsychiatry\b",
    r"(?i)\bEating Disorders\b",

    # Misspellings & Typographical Errors
    r"(?i)\bPsychaitrist\b",
    r"(?i)\bPsychiatristt\b",
    r"(?i)\bPsychitrist\b",
    r"(?i)\bPsyciatrist\b",
    r"(?i)\bPsychyatrist\b",
    r"(?i)\bPsychaitric Doctor\b",
    r"(?i)\bPsychitric Doctor\b",
    r"(?i)\bPsycatrist\b",
    r"(?i)\bPsychatrist\b",
    r"(?i)\bPsichiatrist\b",

    # Case Variations
    r"(?i)\bPSYCHIATRIST\b",
    r"(?i)\bpsychiatrist\b",
    r"(?i)\bPsYcHiAtRiSt\b",

    # Spanish Variants
    r"(?i)\bPsiquiatra\b",
    r"(?i)\bDoctor en Psiquiatría\b",
    r"(?i)\bEspecialista en Psiquiatría\b",
    r"(?i)\bMédico Psiquiatra\b",
    r"(?i)\bMD Psiquiatría\b",

    # Hybrid Spanish-English Variants
    r"(?i)\bPsiquiatrist\b",
    r"(?i)\bPsychiatra\b",

    # Other Possible Variations (Doctor Forms, Specialist Forms)
    r"(?i)\bConsultant Psychiatrist\b",
    r"(?i)\bSenior Psychiatrist\b",
    r"(?i)\bLead Psychiatrist\b",
    r"(?i)\bForensic Psychiatrist\b",
    r"(?i)\bChild Psychiatrist\b",
    r"(?i)\bGeriatric Psychiatrist\b",
    r"(?i)\bNeuropsychiatrist\b",
]

# Exact matches that should be updated
psychiatrist_exact_matches = {
    "Psychiatrist",
    "Psychiatric Doctor",
    "Doctor of Psychiatry",
    "MD Psychiatry",
    "Mental Health Doctor",
    "Psychiatry Specialist",
    "Psychaitrist",
    "Psychiatristt",
    "Psychitrist",
    "Psyciatrist",
    "Psychyatrist",
    "Psychaitric Doctor",
    "Psychitric Doctor",
    "Psycatrist",
    "Psychatrist",
    "Psichiatrist",
    "Psiquiatra",
    "Doctor en Psiquiatría",
    "Especialista en Psiquiatría",
    "Médico Psiquiatra",
    "MD Psiquiatría",
    "Psiquiatrist",
    "Psychiatra",
    "Consultant Psychiatrist",
    "Senior Psychiatrist",
    "Lead Psychiatrist",
    "Forensic Psychiatrist",
    "Child Psychiatrist",
    "Geriatric Psychiatrist",
    "Neuropsychiatrist",
    'Psychiatrie Naturalmedicine',
}

# # Define patterns (these should NOT be changed)
# psychiatrist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

psychiatrist_exclusions = {
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

# Create a mask for Psychiatrist
mask_psychiatrist = df['speciality'].str.contains('|'.join(psychiatrist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(psychiatrist_exact_matches)

# mask_psychiatrist_exclusions = df['speciality'].str.contains(psychiatrist_exclusions, case=False, na=False, regex=True)
mask_psychiatrist_exclusions = df['speciality'].isin(psychiatrist_exclusions)

# Final mask: Select Psychiatrist
mask_psychiatrist_final = mask_psychiatrist & ~mask_psychiatrist_exclusions

# Store the original values that will be replaced
original_psychiatrist_values = df.loc[mask_psychiatrist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_psychiatrist_final, 'speciality'] = 'Psychiatrist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Psychiatrist", 'green'))
print(df.loc[mask_psychiatrist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_psychiatrist_values = df.loc[mask_psychiatrist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Psychiatrist", "cyan"))
for original_psychiatrist_value in original_psychiatrist_values:
    print(f"✅ {original_psychiatrist_value} → Psychiatrist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Psychiatrist:", 'red'))
print(grouped_psychiatrist_values)

# Print summary
matched_count_psychiatrist = mask_psychiatrist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Psychiatrist: "
        f"{matched_count_psychiatrist}",
        'red'))