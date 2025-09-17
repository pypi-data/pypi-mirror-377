import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Oncologist related titles

oncologist_variants = [
    # Standard Titles & Abbreviations
    r"(?i)\bOncologist\b",
    r"(?i)\bMedical\s?Oncologist\b",
    r"(?i)\bClinical\s?Oncologist\b",
    r"(?i)\bRadiation\s?Oncologist\b",
    r"(?i)\bSurgical\s?Oncologist\b",
    r"(?i)\bPediatric\s?Oncologist\b",
    r"(?i)\bGynecologic\s?Oncologist\b",
    r"(?i)\bNeuro\s?Oncologist\b",
    r"(?i)\bBreast\s?Oncologist\b",
    r"(?i)\bThoracic\s?Oncologist\b",
    r"(?i)\bGenitourinary\s?Oncologist\b",
    r"(?i)\bGastrointestinal\s?Oncologist\b",

    # Misspellings & Typographical Errors
    r"(?i)\bOncolgist\b",
    r"(?i)\bOncolojist\b",
    r"(?i)\bOnclogist\b",
    r"(?i)\bOncologest\b",
    r"(?i)\bOncologis\b",
    r"(?i)\bOncologits\b",
    r"(?i)\bOnckologist\b",
    r"(?i)\bOnkologist\b",

    # Case Variations
    r"(?i)\boncologist\b",
    r"(?i)\bOncologist\b",
    r"(?i)\bONCOLOGIST\b",
    r"(?i)\bOncoLogist\b",

    # Spanish Variants
    r"(?i)\bOncólogo\b",
    r"(?i)\bMédico\s?Oncólogo\b",
    r"(?i)\bEspecialista\s?en\s?Oncología\b",
    r"(?i)\bOncólogo\s?Médico\b",
    r"(?i)\bOncólogo\s?Clínico\b",
    r"(?i)\bOncólogo\s?Radioterápico\b",
    r"(?i)\bOncólogo\s?Pediátrico\b",
    r"(?i)\bCirujano\s?Oncólogo\b",

    # Other Possible Variations (Including Doctor/Specialist Titles)
    r"(?i)\bOncology\s?Specialist\b",
    r"(?i)\bCancer\s?Specialist\b",
    r"(?i)\bTumor\s?Specialist\b",
    r"(?i)\bOncological\s?Surgeon\b",
    r"(?i)\bOncological\s?Physician\b",
    r"(?i)\bOnco\b",
    r"(?i)\bChief Pediatric Oncology\b",
]

# Exact matches that should be updated
oncologist_exact_matches = {
    "Oncologist",
    "Medical Oncologist",
    "Clinical Oncologist",
    "Radiation Oncologist",
    "Surgical Oncologist",
    "Pediatric Oncologist",
    "Gynecologic Oncologist",
    "Neuro Oncologist",
    "Breast Oncologist",
    "Thoracic Oncologist",
    "Genitourinary Oncologist",
    "Gastrointestinal Oncologist",
    "Oncolgist",
    "Oncolojist",
    "Onclogist",
    "Oncologest",
    "Oncologis",
    "Oncologits",
    "Onckologist",
    "Onkologist",
    "Oncólogo",
    "Médico Oncólogo",
    "Especialista en Oncología",
    "Oncólogo Médico",
    "Oncólogo Clínico",
    "Oncólogo Radioterápico",
    "Oncólogo Pediátrico",
    "Cirujano Oncólogo",
    "Oncology Specialist",
    "Cancer Specialist",
    "Tumor Specialist",
    "Oncological Surgeon",
    "Oncological Physician",
}

# # Define patterns (these should NOT be changed)
# oncologist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

oncologist_exclusions = {
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
    'Resident Physician - Radiation Oncologist',
}

# Create a mask for Oncologist
mask_oncologist = df['speciality'].str.contains('|'.join(oncologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(oncologist_exact_matches)

# mask_oncologist_exclusions = df['speciality'].str.contains(oncologist_exclusions, case=False, na=False, regex=True)
mask_oncologist_exclusions = df['speciality'].isin(oncologist_exclusions)

# Final mask: Select Oncologist
mask_oncologist_final = mask_oncologist & ~mask_oncologist_exclusions

# Store the original values that will be replaced
original_oncologist_values = df.loc[mask_oncologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_oncologist_final, 'speciality'] = 'Oncologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Oncologist", 'green'))
print(df.loc[mask_oncologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_oncologist_values = df.loc[mask_oncologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Oncologist", "cyan"))
for original_oncologist_value in original_oncologist_values:
    print(f"✅ {original_oncologist_value} → Oncologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Oncologist:", 'red'))
print(grouped_oncologist_values)

# Print summary
matched_count_oncologist = mask_oncologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Oncologist: "
        f"{matched_count_oncologist}",
        'red'))