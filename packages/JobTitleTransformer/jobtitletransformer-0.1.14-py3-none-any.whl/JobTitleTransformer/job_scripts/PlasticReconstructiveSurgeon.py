import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Plastic and Reconstructive Surgeon related titles

reconstructive_variants = [
    # Standard Titles & Variants
    r"(?i)\bPlastic and Reconstructive Surgeon\b",
    r"(?i)\bReconstructive Surgeon\b",
    r"(?i)\bAesthetic and Reconstructive Surgeon\b",
    r"(?i)\bCosmetic and Reconstructive Surgeon\b",
    r"(?i)\bReconstructive and Aesthetic Surgeon\b",
    r"(?i)Plastic & Reconstructive Surgery",
    r"(?i)\bOncoplastic Surgeon\b",
    r"(?i)\bPlastic Rekonstructive & Aesthetic Surgery\b",
    r"(?i)\bPlastic Reconstructive Aesthetic Surgery\b",
    r"(?i)\bChirurgie Plastique Et Reparatrice\b",

    # Misspellings & Typographical Errors
    r"(?i)\bPlasic and Reconstructive Surgeon\b",
    r"(?i)\bPlastic and Reconstuctive Surgeon\b",
    r"(?i)\bPlastic and Reconstructive Surgeoon\b",
    r"(?i)\bPlstic and Reconstructive Surgeon\b",
    r"(?i)\bPlstic and Reconstructive Surgon\b",
    r"(?i)\bPlastic and Reconstructuve Surgeon\b",

    # Case Variations
    r"(?i)\bplastic and reconstructive surgeon\b",
    r"(?i)\bPLASTIC AND RECONSTRUCTIVE SURGEON\b",
    r"(?i)\bPlAsTiC aND ReCoNsTrUcTiVe SuRgEoN\b",

    # Spanish Variants
    r"(?i)\bCirujano Plástico y Reconstructivo\b",
    r"(?i)\bCirujano Estético y Reconstructivo\b",
    r"(?i)\bCirujano Reconstructivo\b",

    # Other Possible Variations
    r"(?i)\bCosmetic Reconstructive Surgeon\b",
    r"(?i)\bReconstructive Surgery Specialist\b",
    r"(?i)\bReconstructive and Cosmetic Surgeon\b",
    r"(?i)\bPlastic & Reconstractive Surgeon\b",
    r"(?i)\bArmonizacion Orofacial\b",
    r"(?i)\bPlastic Aesthetic & Reconstructive Surgery\b",
    r"(?i)\bPlastic Reconstructive & Aesthetic Surgeon\b",
    r"(?i)\bPlastic Rekonstructive & Aesthetic Surgery\b",
    r"(?i)\bPlastic Reconstructive & Aesthetic Surgery\b",
    r"(?i)\bPlastic Reconstructive Aesthetic Surgery\b",
    r"(?i)\bSpecialist In Facial Harmonization\b",
]

# Exact matches that should be updated
reconstructive_exact_matches = {
    "Plastic and Reconstructive Surgeon",
    "Reconstructive Surgeon",
    "Aesthetic and Reconstructive Surgeon",
    "Cosmetic and Reconstructive Surgeon",
    "Reconstructive and Aesthetic Surgeon",
    "Plasic and Reconstructive Surgeon",
    "Plastic and Reconstuctive Surgeon",
    "Plastic and Reconstructive Surgeoon",
    "Plstic and Reconstructive Surgeon",
    "Plstic and Reconstructive Surgon",
    "Plastic and Reconstructuve Surgeon",
    "Cirujano Plástico y Reconstructivo",
    "Cirujano Estético y Reconstructivo",
    "Cirujano Reconstructivo",
    "Cosmetic Reconstructive Surgeon",
    "Reconstructive Surgery Specialist",
    "Reconstructive and Cosmetic Surgeon",
    'Plastic & Reconstrucitve Surgery',
    'Cirujana Plastica Y Reconstructiva'
}

# # Define patterns (these should NOT be changed)
# reconstructive_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

reconstructive_exclusions = {
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
    'A Professor Plastic & Reconstructive Surgery',
}

# Create a mask for Plastic and Reconstructive Surgeon
mask_reconstructive = df['speciality'].str.contains('|'.join(reconstructive_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(reconstructive_exact_matches)

# mask_reconstructive_exclusions = df['speciality'].str.contains(reconstructive_exclusions, case=False, na=False, regex=True)
mask_reconstructive_exclusions = df['speciality'].isin(reconstructive_exclusions)

# Final mask: Select Plastic and Reconstructive Surgeon
mask_reconstructive_final = mask_reconstructive & ~mask_reconstructive_exclusions

# Store the original values that will be replaced
original_reconstructive_values = df.loc[mask_reconstructive_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_reconstructive_final, 'speciality'] = 'Plastic and Reconstructive Surgeon'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Plastic and Reconstructive Surgeon", 'green'))
print(df.loc[mask_reconstructive_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_reconstructive_values = df.loc[mask_reconstructive_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Plastic and Reconstructive Surgeon", "cyan"))
for original_reconstructive_value in original_reconstructive_values:
    print(f"✅ {original_reconstructive_value} → Plastic and Reconstructive Surgeon")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Plastic and Reconstructive Surgeon:", 'red'))
print(grouped_reconstructive_values)

# Print summary
matched_count_reconstructive = mask_reconstructive_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Plastic and Reconstructive Surgeon: "
        f"{matched_count_reconstructive}",
        'red'))