import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Facial Plastic Surgeon related titles

facial_plastic_surgeon_variants = [
    r"(?i)\bFacial\s?Plastic\s?Surgeon\b",
    r"(?i)\bFacial\s?Aesthetic\s?Surgeon\b",
    r"(?i)\bFacial\s?Reconstructive\s?Surgeon\b",
    r"(?i)\bFacial\s?Cosmetic\s?Surgeon\b",
    r"(?i)\bAesthetic\s?Facial\s?Surgeon\b",
    r"(?i)\bCosmetic\s?Facial\s?Surgeon\b",

    # Spanish variants
    r"(?i)\bCirujano\s?Plástico\s?Facial\b",
    r"(?i)\bCirujano\s?Estético\s?Facial\b",
    r"(?i)\bCirujano\s?Reconstructivo\s?Facial\b",
    r"(?i)\bCirujano\s?Cosmético\s?Facial\b",
    r"(?i)\bEspecialista\s?en\s?Cirugía\s?Plástica\s?Facial\b",
    r"(?i)\bCirujano\s?Facial\s?Estético\b",
    r"(?i)\bCirujano\s?Facial\s?Cosmético\b",

    # Other possible variations
    r"(?i)\bDoctor\s?in\s?Facial\s?Plastic\s?Surgery\b",
    r"(?i)\bBoard\s?Certified\s?Facial\s?Plastic\s?Surgeon\b",
    r"(?i)\bCertified\s?Facial\s?Plastic\s?Surgeon\b",
    r"(?i)\bCosmetic\s?Plastic\s?Surgeon\s?Specialist\b",
    r"(?i)\bFacial\s?Reconstructive\s?Surgeon\s?Specialist\b",
    r"(?i)\bAesthetic\s?Plastic\s?Surgeon\b",
    r"(?i)\bFacial\s?Surgery\s?Specialist\b",
    r"(?i)\bPlastic\s?Surgical\s?Specialist\b",
    r"(?i)\bFacial Plastic Surgery\b",
    r"(?i)\bOculofacial Plastics\b",
    r"(?i)\bCx Plastico Facial\b",
    r"(?i)\bRhinoplasty\b",
    r"(?i)\bPlastic Surgeon   Facial Plastic Surgeon\b",
    r"(?i)\bBreast & Facial Surgery\b",
    r"(?i)\bCirujano Facial\b",
]

# Exact matches that should be updated
facial_plastic_surgeon_exact_matches = {
    "Facial Plastic Surgeon",
    "Facial Aesthetic Surgeon",
    "Facial Reconstructive Surgeon",
    "Facial Cosmetic Surgeon",
    "Aesthetic Facial Surgeon",
    "Cosmetic Facial Surgeon",
    # Spanish form matches
    "Cirujano Plástico Facial",
    "Cirujano Estético Facial",
    "Cirujano Reconstructivo Facial",
    "Cirujano Cosmético Facial",
    "Especialista en Cirugía Plástica Facial",
    "Cirujano Facial Estético",
    "Cirujano Facial Cosmético",
    # Other possible variations
    "Doctor in Facial Plastic Surgery",
    "Board Certified Facial Plastic Surgeon",
    "Certified Facial Plastic Surgeon",
    "Cosmetic Plastic Surgeon Specialist",
    "Facial Reconstructive Surgeon Specialist",
    "Aesthetic Plastic Surgeon",
    "Facial Surgery Specialist",
    "Plastic Surgical Specialist",
    "Facial Aesthetics",
    'Facial Plastics',
}

# Define patterns (these should NOT be changed)
facial_plastic_surgeon_exclusions = {
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

# Create a mask for Facial Plastic Surgeon
mask_facial_plastic_surgeon = df['speciality'].str.contains('|'.join(facial_plastic_surgeon_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(facial_plastic_surgeon_exact_matches)
mask_facial_plastic_surgeon_exclusions = df['speciality'].isin(facial_plastic_surgeon_exclusions)

# Final mask: Select Facial Plastic Surgeon
mask_facial_plastic_surgeon_final = mask_facial_plastic_surgeon & ~mask_facial_plastic_surgeon_exclusions

# Store the original values that will be replaced
original_facial_plastic_surgeon_values = df.loc[mask_facial_plastic_surgeon_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_facial_plastic_surgeon_final, 'speciality'] = 'Facial Plastic Surgeon'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Facial Plastic Surgeon", 'green'))
print(df.loc[mask_facial_plastic_surgeon_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_facial_plastic_surgeon_values = df.loc[mask_facial_plastic_surgeon_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Facial Plastic Surgeon", "cyan"))
for original_facial_plastic_surgeon_value in original_facial_plastic_surgeon_values:
    print(f"✅ {original_facial_plastic_surgeon_value} → Facial Plastic Surgeon")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Facial Plastic Surgeon:", 'red'))
print(grouped_facial_plastic_surgeon_values)

# Print summary
matched_count_facial_plastic_surgeon = mask_facial_plastic_surgeon_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Facial Plastic Surgeon: "
        f"{matched_count_facial_plastic_surgeon}",
        'red'))