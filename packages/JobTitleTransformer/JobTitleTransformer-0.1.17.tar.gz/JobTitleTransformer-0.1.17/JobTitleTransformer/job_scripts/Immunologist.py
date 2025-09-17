import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Immunologist related titles

immunologist_variants = [
    r"(?i)\bImmunologist\b",

    # Common misspellings and case errors
    r"(?i)\bImunologist\b",
    r"(?i)\bImmnuologist\b",
    r"(?i)\bImmunoligist\b",
    r"(?i)\bImmunollogist\b",
    r"(?i)\bImmunolgist\b",
    r"(?i)\bVirologist\b",

    # Spanish variants
    r"(?i)\bInmunólogo\b",
    r"(?i)\bInmunóloga\b",
    r"(?i)\bEspecialista\s?en\s?Inmunología\b",

    # Other possible variations
    r"(?i)\bImmunology\s?Specialist\b",
    r"(?i)\bDoctor\s?of\s?Immunology\b",
    r"(?i)\bClinical\s?Immunologist\b",
    r"(?i)\bResearch\s?Immunologist\b",
    r"(?i)\bAllergy\s?and\s?Immunology\s?Specialist\b",
    r"(?i)\bImmunology\b",
    r"(?i)\bAllergy Immunology\b",
    r"(?i)\bAllergy\b",
]

# Exact matches that should be updated
immunologist_exact_matches = {
    "Immunologist",
    "Imunologist",
    "Immnuologist",
    "Immunoligist",
    "Immunollogist",
    "Immunolgist",
    # Spanish variants
    "Inmunólogo",
    "Inmunóloga",
    "Especialista en Inmunología",
    # Other possible variations
    "Immunology Specialist",
    "Doctor of Immunology",
    "Clinical Immunologist",
    "Research Immunologist",
    "Allergy and Immunology Specialist",
}

# Define patterns (these should NOT be changed)
immunologist_exclusions = {
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
    'Field Director- Immunology & Dermatology',
    'Senior Sales Immunology- Dermatology',
    'District Western Pa Immunology Dermatology Franchise Senior District Sales Manager',
    'Medical Science Executive & Dermatology Immunology Liaison',
    'Immunology Specialty Sales-Dermatology',
    'Immunology Sales Janssen Biotech Inc Dermatology At Johnson & Johnson Specialist',
    'Thought Leader Liaison Strategic Marketing Immunology Dermatology',
    'Sales Executive & Immunology Dermatology Specialist',
    'Immunology Sales Dermatology Specialist',
    'Immunology Sales -Dermatology Specialist',
}

# Create a mask for Immunologist
mask_immunologist = df['speciality'].str.contains('|'.join(immunologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(immunologist_exact_matches)
mask_immunologist_exclusions = df['speciality'].isin(immunologist_exclusions)

# Final mask: Select Immunologist
mask_immunologist_final = mask_immunologist & ~mask_immunologist_exclusions

# Store the original values that will be replaced
original_immunologist_values = df.loc[mask_immunologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_immunologist_final, 'speciality'] = 'Immunologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Immunologist", 'green'))
print(df.loc[mask_immunologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_immunologist_values = df.loc[mask_immunologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Immunologist", "cyan"))
for original_immunologist_value in original_immunologist_values:
    print(f"✅ {original_immunologist_value} → Immunologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Immunologist:", 'red'))
print(grouped_immunologist_values)

# Print summary
matched_count_immunologist = mask_immunologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Immunologist: "
        f"{matched_count_immunologist}",
        'red'))