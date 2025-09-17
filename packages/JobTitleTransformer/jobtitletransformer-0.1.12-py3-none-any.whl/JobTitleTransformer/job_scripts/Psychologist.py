import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Psychologist related titles

psychologist_variants = [
    # Standard Titles & Variants
    r"(?i)\bPsychologist\b",
    r"(?i)\bClinical Psychologist\b",
    r"(?i)\bLicensed Psychologist\b",
    r"(?i)\bPsychology Specialist\b",
    r"(?i)\bBehavioral Psychologist\b",
    r"(?i)\bMental Health Psychologist\b",

    # Misspellings & Typographical Errors
    r"(?i)\bPshychologist\b",
    r"(?i)\bPsychologst\b",
    r"(?i)\bPsycholigist\b",
    r"(?i)\bPsycholgist\b",
    r"(?i)\bPsycologist\b",
    r"(?i)\bPsychollogist\b",
    r"(?i)\bPsychologgist\b",
    r"(?i)\bPsychologisst\b",
    r"(?i)\bPsichologist\b",

    # Case Variations
    r"(?i)\bPSYCHOLOGIST\b",
    r"(?i)\bpsychologist\b",
    r"(?i)\bPsYcHoLoGiSt\b",

    # Spanish Variants
    r"(?i)\bPsicólogo\b",
    r"(?i)\bPsicóloga\b",
    r"(?i)\bDoctor en Psicología\b",
    r"(?i)\bEspecialista en Psicología\b",
    r"(?i)\bMédico Psicólogo\b",
    r"(?i)\bPsicólogo Clínico\b",
    r"(?i)\bPsicólogo de la Salud\b",

    # Hybrid Spanish-English Variants
    r"(?i)\bPsicologyst\b",
    r"(?i)\bPsychologa\b",

    # Other Possible Variations (Doctor Forms, Specialist Forms)
    r"(?i)\bConsultant Psychologist\b",
    r"(?i)\bSenior Psychologist\b",
    r"(?i)\bLead Psychologist\b",
    r"(?i)\bForensic Psychologist\b",
    r"(?i)\bChild Psychologist\b",
    r"(?i)\bGeriatric Psychologist\b",
    r"(?i)\bNeuropsychologist\b",
    r"(?i)\bPsychology\b",
    r"(?i)\bChild & Adolescent Neuropsichiatry\b",
]

# Exact matches that should be updated
psychologist_exact_matches = {
    "Psychologist",
    "Clinical Psychologist",
    "Licensed Psychologist",
    "Psychology Specialist",
    "Behavioral Psychologist",
    "Mental Health Psychologist",
    "Pshychologist",
    "Psychologst",
    "Psycholigist",
    "Psycholgist",
    "Psycologist",
    "Psychollogist",
    "Psychologgist",
    "Psychologisst",
    "Psichologist",
    "Psicólogo",
    "Psicóloga",
    "Doctor en Psicología",
    "Especialista en Psicología",
    "Médico Psicólogo",
    "Psicólogo Clínico",
    "Psicólogo de la Salud",
    "Psicologyst",
    "Psychologa",
    "Consultant Psychologist",
    "Senior Psychologist",
    "Lead Psychologist",
    "Forensic Psychologist",
    "Child Psychologist",
    "Geriatric Psychologist",
    "Neuropsychologist",
}

# # Define patterns (these should NOT be changed)
# psychologist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

psychologist_exclusions = {
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

# Create a mask for Psychologist
mask_psychologist = df['speciality'].str.contains('|'.join(psychologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(psychologist_exact_matches)

# mask_psychologist_exclusions = df['speciality'].str.contains(psychologist_exclusions, case=False, na=False, regex=True)
mask_psychologist_exclusions = df['speciality'].isin(psychologist_exclusions)

# Final mask: Select Psychologist
mask_psychologist_final = mask_psychologist & ~mask_psychologist_exclusions

# Store the original values that will be replaced
original_psychologist_values = df.loc[mask_psychologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_psychologist_final, 'speciality'] = 'Psychologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Psychologist", 'green'))
print(df.loc[mask_psychologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_psychologist_values = df.loc[mask_psychologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Psychologist", "cyan"))
for original_psychologist_value in original_psychologist_values:
    print(f"✅ {original_psychologist_value} → Psychologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Psychologist:", 'red'))
print(grouped_psychologist_values)

# Print summary
matched_count_psychologist = mask_psychologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Psychologist: "
        f"{matched_count_psychologist}",
        'red'))