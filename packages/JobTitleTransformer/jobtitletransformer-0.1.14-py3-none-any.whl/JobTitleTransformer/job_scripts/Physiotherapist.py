import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Physiotherapist related titles

physiotherapist_variants = [
    # Standard Titles & Variants
    r"(?i)\bPhysiotherapist\b",
    r"(?i)\bPhysical Therapist\b",
    r"(?i)\bPhysiotherapy Specialist\b",
    r"(?i)\bPhysiotherapist Specialist\b",
    r"(?i)\bPhysiotherapist Practitioner\b",
    r"(?i)\bPhysical Therapy Specialist\b",
    r"(?i)\bPhysiapist\b",
    r"(?i)\bHealth Therapist\b",
    r"(?i)\bFisioterapia Dermatofuncional E Gestora De Clinica\b",
    r"(?i)\bPhysiology\b",

    # Misspellings & Typographical Errors
    r"(?i)\bPhysiotherpist\b",
    r"(?i)\bPhysiotherapis\b",
    r"(?i)\bPhysiotherapst\b",
    r"(?i)\bPhysiotheraprist\b",
    r"(?i)\bPhysioterapist\b",
    r"(?i)\bPhysiotherpist\b",

    # Case Variations
    r"(?i)\bphysiotherapist\b",
    r"(?i)\bPHYSIOTHERAPIST\b",
    r"(?i)\bPhYsIoThErApIsT\b",
    r"(?i)\bPhysiotherapist\b",

    # Spanish Variants
    r"(?i)\bFisioterapeuta\b",
    r"(?i)\bTerapeuta Físico\b",
    r"(?i)\bEspecialista en Fisioterapia\b",
    r"(?i)\bFisioterapeuta Especialista\b",
    r"(?i)\bFisioterapeuta Clínico\b",
    r"(?i)\bFisioterapeuta Profesional\b",

    # Other Possible Variations
    r"(?i)\bPhysical Rehabilitation Specialist\b",
    r"(?i)\bPhysical Therapy Professional\b",
    r"(?i)\bRehabilitation Therapist\b",
    r"(?i)\bPhysical Care Specialist\b",
]

# Exact matches that should be updated
physiotherapist_exact_matches = {
    "Physiotherapist",
    "Physical Therapist",
    "Physiotherapy Specialist",
    "Physiotherapist Specialist",
    "Physiotherapist Practitioner",
    "Physical Therapy Specialist",
    "Physiotherpist",
    "Physiotherapis",
    "Physiotherapst",
    "Physiotheraprist",
    "Physioterapist",
    "Fisioterapeuta",
    "Terapeuta Físico",
    "Especialista en Fisioterapia",
    "Fisioterapeuta Especialista",
    "Fisioterapeuta Clínico",
    "Fisioterapeuta Profesional",
    "Physical Rehabilitation Specialist",
    "Physical Therapy Professional",
    "Rehabilitation Therapist",
    "Physical Care Specialist",
    'Doctor Of Physical Therapy',
}

# # Define patterns (these should NOT be changed)
# physiotherapist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

physiotherapist_exclusions = {
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

# Create a mask for Physiotherapist
mask_physiotherapist = df['speciality'].str.contains('|'.join(physiotherapist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(physiotherapist_exact_matches)

# mask_physiotherapist_exclusions = df['speciality'].str.contains(physiotherapist_exclusions, case=False, na=False, regex=True)
mask_physiotherapist_exclusions = df['speciality'].isin(physiotherapist_exclusions)

# Final mask: Select Physiotherapist
mask_physiotherapist_final = mask_physiotherapist & ~mask_physiotherapist_exclusions

# Store the original values that will be replaced
original_physiotherapist_values = df.loc[mask_physiotherapist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_physiotherapist_final, 'speciality'] = 'Physiotherapist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Physiotherapist", 'green'))
print(df.loc[mask_physiotherapist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_physiotherapist_values = df.loc[mask_physiotherapist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Physiotherapist", "cyan"))
for original_physiotherapist_value in original_physiotherapist_values:
    print(f"✅ {original_physiotherapist_value} → Physiotherapist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Physiotherapist:", 'red'))
print(grouped_physiotherapist_values)

# Print summary
matched_count_physiotherapist = mask_physiotherapist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Physiotherapist: "
        f"{matched_count_physiotherapist}",
        'red'))