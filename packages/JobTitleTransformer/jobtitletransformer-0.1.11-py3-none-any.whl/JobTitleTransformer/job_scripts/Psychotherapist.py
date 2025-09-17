import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Psychotherapist related titles

psychotherapist_variants = [
    # Standard Titles & Variants
    r"(?i)\bPsychotherapist\b",
    r"(?i)\bLicensed Psychotherapist\b",
    r"(?i)\bMental Health Therapist\b",
    r"(?i)\bCounselor\b",
    r"(?i)\bClinical Psychotherapist\b",
    r"(?i)\bPsychapist\b",

    # Misspellings & Typographical Errors
    r"(?i)\bPsychotherpist\b",
    r"(?i)\bPsychotherpistt\b",
    r"(?i)\bPsycotherapist\b",
    r"(?i)\bPsychotheripist\b",
    r"(?i)\bPsychotherist\b",
    r"(?i)\bPsychotheraist\b",
    r"(?i)\bPsycotherapist\b",

    # Case Variations
    r"(?i)\bPSYCHOTHERAPIST\b",
    r"(?i)\bpsychotherapist\b",
    r"(?i)\bPyScHoThErApIsT\b",

    # Spanish Variants
    r"(?i)\bPsicoterapeuta\b",
    r"(?i)\bPsicoterapeuta Clínico\b",
    r"(?i)\bPsicoterapeuta Licenciado\b",
    r"(?i)\bConsejero\b",
    r"(?i)\bPsicoterapeuta de la Salud Mental\b",

    # Hybrid Spanish-English Variants
    r"(?i)\bPsicotherapist\b",
    r"(?i)\bPsycotherapist\b",

    # Other Possible Variations (Doctor Forms, Specialist Forms)
    r"(?i)\bMental Health Counselor\b",
    r"(?i)\bMarriage and Family Therapist\b",
    r"(?i)\bCounseling Psychotherapist\b",
    r"(?i)\bClinical Therapist\b",
    r"(?i)\bPsychiatric Therapist\b",
    r"(?i)\bLicensed Clinical Social Worker\b",
]

# Exact matches that should be updated
psychotherapist_exact_matches = {
    "Psychotherapist",
    "Licensed Psychotherapist",
    "Mental Health Therapist",
    "Counselor",
    "Clinical Psychotherapist",
    "Psychotherpist",
    "Psychotherpistt",
    "Psycotherapist",
    "Psychotheripist",
    "Psychotherist",
    "Psychotheraist",
    "Psicoterapeuta",
    "Terapeuta",
    "Psicoterapeuta Clínico",
    "Psicoterapeuta Licenciado",
    "Consejero",
    "Psicoterapeuta de la Salud Mental",
    "Psicotherapist",
    "Mental Health Counselor",
    "Marriage and Family Therapist",
    "Counseling Psychotherapist",
    "Clinical Therapist",
    "Psychiatric Therapist",
    "Licensed Clinical Social Worker",
}

# # Define patterns (these should NOT be changed)
# psychotherapist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

psychotherapist_exclusions = {
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

# Create a mask for Psychotherapist
mask_psychotherapist = df['speciality'].str.contains('|'.join(psychotherapist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(psychotherapist_exact_matches)

# mask_psychotherapist_exclusions = df['speciality'].str.contains(psychotherapist_exclusions, case=False, na=False, regex=True)
mask_psychotherapist_exclusions = df['speciality'].isin(psychotherapist_exclusions)

# Final mask: Select Psychotherapist
mask_psychotherapist_final = mask_psychotherapist & ~mask_psychotherapist_exclusions

# Store the original values that will be replaced
original_psychotherapist_values = df.loc[mask_psychotherapist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_psychotherapist_final, 'speciality'] = 'Psychotherapist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Psychotherapist", 'green'))
print(df.loc[mask_psychotherapist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_psychotherapist_values = df.loc[mask_psychotherapist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Psychotherapist", "cyan"))
for original_psychotherapist_value in original_psychotherapist_values:
    print(f"✅ {original_psychotherapist_value} → Psychotherapist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Psychotherapist:", 'red'))
print(grouped_psychotherapist_values)

# Print summary
matched_count_psychotherapist = mask_psychotherapist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Psychotherapist: "
        f"{matched_count_psychotherapist}",
        'red'))