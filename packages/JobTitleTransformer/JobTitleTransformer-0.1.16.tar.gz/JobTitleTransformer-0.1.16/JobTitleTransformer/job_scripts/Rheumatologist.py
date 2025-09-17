import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Rheumatologist related titles

rheumatologist_variants = [
    # Standard Titles & Variants
    r"(?i)\bRheumatologist\b",
    r"(?i)\bRheumatology Specialist\b",
    r"(?i)\bRheumatology Consultant\b",
    r"(?i)\bRheumatic Disease Specialist\b",
    r"(?i)\bRheumatology Physician\b",
    r"(?i)\bRheumatology Doctor\b",

    # Misspellings & Typographical Errors
    r"(?i)\bRheumatoligist\b",
    r"(?i)\bRheumatologistt\b",
    r"(?i)\bRheumatoligistt\b",
    r"(?i)\bReumatologist\b",
    r"(?i)\bRheumatoligst\b",
    r"(?i)\bRheumatogist\b",

    # Case Variations
    r"(?i)\bRHEUMATOLOGIST\b",
    r"(?i)\bRheumatologist\b",
    r"(?i)\bRHEUMATOLOGISTt\b",
    r"(?i)\brheumatologist\b",

    # Spanish Variants
    r"(?i)\bReumatólogo\b",
    r"(?i)\bEspecialista en Reumatología\b",
    r"(?i)\bMédico Reumatólogo\b",
    r"(?i)\bMédico Especialista en Reumatología\b",
    r"(?i)\bEspecialista en Enfermedades Reumáticas\b",
    r"(?i)\bReumatólogo Clínico\b",
    r"(?i)\bReumatología\b",

    # Hybrid Spanish-English Variants
    r"(?i)\bRheumatologist Especialista\b",
    r"(?i)\bRheumatology Reumatólogo\b",

    # Other Possible Variations (Doctor Forms, Specialist Forms)
    r"(?i)\bRheumatology Specialist\b",
    r"(?i)\bRheumatic Disease Doctor\b",
    r"(?i)\bRheumatology Physician\b",
    r"(?i)\bRheumatology Consultant\b",
    r"(?i)\bReumatic Disease Consultant\b",
    r"(?i)\bArthritis Specialist\b",
    r"(?i)\bChronic Pain Specialist\b",
]

# Exact matches that should be updated
rheumatologist_exact_matches = {
    "Rheumatologist",
    "Rheumatology Specialist",
    "Rheumatology Consultant",
    "Rheumatic Disease Specialist",
    "Rheumatology Physician",
    "Rheumatology Doctor",
    "Rheumatoligist",
    "Rheumatologistt",
    "Rheumatoligistt",
    "Reumatologist",
    "Rheumatoligst",
    "Rheumatogist",
    "RHEUMATOLOGIST",
    "RHEUMATOLOGISTt",
    "rheumatologist",
    "Reumatólogo",
    "Especialista en Reumatología",
    "Médico Reumatólogo",
    "Médico Especialista en Reumatología",
    "Especialista en Enfermedades Reumáticas",
    "Reumatólogo Clínico",
    "Reumatología",
    "Rheumatologist Especialista",
    "Rheumatology Reumatólogo",
    "Rheumatic Disease Doctor",
    "Reumatic Disease Consultant",
    "Arthritis Specialist",
    "Chronic Pain Specialist",
    'RHEUMATOLOGY',
}

# # Define patterns (these should NOT be changed)
# rheumatologist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

rheumatologist_exclusions = {
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

# Create a mask for Rheumatologist
mask_rheumatologist = df['speciality'].str.contains('|'.join(rheumatologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(rheumatologist_exact_matches)

# mask_rheumatologist_exclusions = df['speciality'].str.contains(rheumatologist_exclusions, case=False, na=False, regex=True)
mask_rheumatologist_exclusions = df['speciality'].isin(rheumatologist_exclusions)

# Final mask: Select Rheumatologist
mask_rheumatologist_final = mask_rheumatologist & ~mask_rheumatologist_exclusions

# Store the original values that will be replaced
original_rheumatologist_values = df.loc[mask_rheumatologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_rheumatologist_final, 'speciality'] = 'Rheumatologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Rheumatologist", 'green'))
print(df.loc[mask_rheumatologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_rheumatologist_values = df.loc[mask_rheumatologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Rheumatologist", "cyan"))
for original_rheumatologist_value in original_rheumatologist_values:
    print(f"✅ {original_rheumatologist_value} → Rheumatologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Rheumatologist:", 'red'))
print(grouped_rheumatologist_values)

# Print summary
matched_count_rheumatologist = mask_rheumatologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Rheumatologist: "
        f"{matched_count_rheumatologist}",
        'red'))