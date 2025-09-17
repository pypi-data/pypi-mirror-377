import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Oculoplastic Surgeon related titles

oculoplastic_surgeon_variants = [
    # Standard Titles & Abbreviations
    r"(?i)\bOculoplastic\s?Surgeon\b",
    r"(?i)\bOculoplastics\s?Surgeon\b",
    r"(?i)\bOculo-Plastic\s?Surgeon\b",
    r"(?i)\bOphthalmic\s?Plastic\s?Surgeon\b",
    r"(?i)\bOrbital\s?Surgeon\b",
    r"(?i)\bOculofacial\s?Surgeon\b",
    r"(?i)\bEyelid\s?Surgeon\b",
    r"(?i)\bFacial\s?Oculoplastic\s?Surgeon\b",
    r"(?i)\bOculoplastic\s?Specialist\b",
    r"(?i)\bOculoplasty Surgeon\b",
    r"(?i)\bOphthalmologistOculoplastic Surgeon\b",
    r"(?i)\bOphthalmoplastic Surgery\b",
    r"(?i)\bOculoplastic\b",

    # Misspellings & Typographical Errors
    r"(?i)\bOcculoplastic\s?Surgeon\b",
    r"(?i)\bOculaplastic\s?Surgeon\b",
    r"(?i)\bOculoplastik\s?Surgeon\b",
    r"(?i)\bOculoplastic\s?Surgon\b",
    r"(?i)\bOculoplastic\s?Surgin\b",
    r"(?i)\bOculoplastic\s?Surjeon\b",
    r"(?i)\bOculoplastic\s?Surgan\b",
    r"(?i)\bOculoplastic\s?Surgion\b",
    r"(?i)\bOculoplastic\s?Suergeon\b",
    r"(?i)\bOculoplastic\s?Srurgeon\b",
    r"(?i)\bOculoplastic\s?Surrgeon\b",

    # Case Variations
    r"(?i)\boculoplastic surgeon\b",
    r"(?i)\bOculoplastic surgeon\b",
    r"(?i)\boculoplastic Surgeon\b",
    r"(?i)\bOCULOPLASTIC SURGEON\b",
    r"(?i)\bOculoPlastic Surgeon\b",

    # Spanish Variants
    r"(?i)\bCirujano\s?Oculoplástico\b",
    r"(?i)\bEspecialista\s?Oculoplástico\b",
    r"(?i)\bMédico\s?Cirujano\s?Oculoplástico\b",
    r"(?i)\bDoctor\s?en\s?Cirugía\s?Oculoplástica\b",
    r"(?i)\bCirujano\s?Plástico\s?Oftálmico\b",

    # Other Possible Variations (Including Doctor/Specialist Titles)
    r"(?i)\bEyelid\s?Plastic\s?Surgeon\b",
    r"(?i)\bOrbital\s?Facial\s?Plastic\s?Surgeon\b",
    r"(?i)\bOphthalmic\s?Cosmetic\s?Surgeon\b",
    r"(?i)\bPeriorbital\s?Surgeon\b",
    r"(?i)\bOculoplastics\b",
    r"(?i)\bAesthetic Medicine Oculoplasty  Ophtalmology\b",
    r"(?i)\bOculofacial Surgery\b",
]

# Exact matches that should be updated
oculoplastic_surgeon_exact_matches = {
    "Oculoplastic Surgeon",
    "Oculoplastics Surgeon",
    "Oculo-Plastic Surgeon",
    "Ophthalmic Plastic Surgeon",
    "Orbital Surgeon",
    "Oculofacial Surgeon",
    "Eyelid Surgeon",
    "Facial Oculoplastic Surgeon",
    "Oculoplastic Specialist",
    "Occuloplastic Surgeon",
    "Oculaplastic Surgeon",
    "Oculoplastik Surgeon",
    "Oculoplastic Surgon",
    "Oculoplastic Surgin",
    "Oculoplastic Surjeon",
    "Oculoplastic Surgan",
    "Oculoplastic Surgion",
    "Oculoplastic Suergeon",
    "Oculoplastic Srurgeon",
    "Oculoplastic Surrgeon",
    "Cirujano Oculoplástico",
    "Especialista Oculoplástico",
    "Médico Cirujano Oculoplástico",
    "Doctor en Cirugía Oculoplástica",
    "Cirujano Plástico Oftálmico",
    "Eyelid Plastic Surgeon",
    "Orbital Facial Plastic Surgeon",
    "Ophthalmic Cosmetic Surgeon",
    "Periorbital Surgeon",
}

# # Define patterns (these should NOT be changed)
# oculoplastic_surgeon_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

oculoplastic_surgeon_exclusions = {
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

# Create a mask for Oculoplastic Surgeon
mask_oculoplastic_surgeon = df['speciality'].str.contains('|'.join(oculoplastic_surgeon_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(oculoplastic_surgeon_exact_matches)

# mask_oculoplastic_surgeon_exclusions = df['speciality'].str.contains(oculoplastic_surgeon_exclusions, case=False, na=False, regex=True)
mask_oculoplastic_surgeon_exclusions = df['speciality'].isin(oculoplastic_surgeon_exclusions)

# Final mask: Select Oculoplastic Surgeon
mask_oculoplastic_surgeon_final = mask_oculoplastic_surgeon & ~mask_oculoplastic_surgeon_exclusions

# Store the original values that will be replaced
original_oculoplastic_surgeon_values = df.loc[mask_oculoplastic_surgeon_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_oculoplastic_surgeon_final, 'speciality'] = 'Oculoplastic Surgeon'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Oculoplastic Surgeon", 'green'))
print(df.loc[mask_oculoplastic_surgeon_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_oculoplastic_surgeon_values = df.loc[mask_oculoplastic_surgeon_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Oculoplastic Surgeon", "cyan"))
for original_oculoplastic_surgeon_value in original_oculoplastic_surgeon_values:
    print(f"✅ {original_oculoplastic_surgeon_value} → Oculoplastic Surgeon")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Oculoplastic Surgeon:", 'red'))
print(grouped_oculoplastic_surgeon_values)

# Print summary
matched_count_oculoplastic_surgeon = mask_oculoplastic_surgeon_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Oculoplastic Surgeon: "
        f"{matched_count_oculoplastic_surgeon}",
        'red'))