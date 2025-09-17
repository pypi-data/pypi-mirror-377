import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Pharmacologist related titles

pharmacologist_variants = [
    # Standard Titles & Variants
    r"(?i)\bPharmacologist\b",
    r"(?i)\bPharmacological Expert\b",
    r"(?i)\bClinical Pharmacologist\b",
    r"(?i)\bPharmacology Specialist\b",
    r"(?i)\bPharmaceutical Scientist\b",
    r"(?i)\bPharmacologist Consultant\b",
    r"(?i)\bConsultant Pharmacologist\b",

    # Misspellings & Typographical Errors
    r"(?i)\bPharmacollogist\b",
    r"(?i)\bPharmocologist\b",
    r"(?i)\bPharmocologist\b",
    r"(?i)\bPharmocologist\b",
    r"(?i)\bPharmacologist\b",
    r"(?i)\bPharmcologist\b",

    # Case Variations
    r"(?i)\bpharmacologist\b",
    r"(?i)\bPHARMACOLOGIST\b",
    r"(?i)\bPhArMaCoLoGiSt\b",
    r"(?i)\bPhArMaCoLoGiSt\b",

    # Spanish Variants
    r"(?i)\bFarmacólogo\b",
    r"(?i)\bFarmacológica\b",
    r"(?i)\bEspecialista\s?Farmacológico\b",
    r"(?i)\bFarmacología\s?Clínica\b",
    r"(?i)\bFarmacología\s?Comunitaria\b",
    r"(?i)\bFarmacología\s?Hospitalaria\b",
    r"(?i)\bFarmacólogo\s?Consultor\b",
    r"(?i)\bConsultor\s?Farmacológico\b",

    # Other Possible Variations
    r"(?i)\bPharmacological Researcher\b",
    r"(?i)\bPharmacologist Specialist\b",
    r"(?i)\bPharmaceutical Expert\b",
    r"(?i)\bPharmacology Researcher\b",
    r"(?i)Pharmacology",
]

# Exact matches that should be updated
pharmacologist_exact_matches = {
    "Pharmacologist",
    "Pharmacological Expert",
    "Clinical Pharmacologist",
    "Pharmacology Specialist",
    "Pharmaceutical Scientist",
    "Pharmacologist Consultant",
    "Consultant Pharmacologist",
    "Pharmacollogist",
    "Pharmocologist",
    "Pharmcologist",
    "Farmacólogo",
    "Farmacológica",
    "Especialista Farmacológico",
    "Farmacología Clínica",
    "Farmacología Comunitaria",
    "Farmacología Hospitalaria",
    "Farmacólogo Consultor",
    "Consultor Farmacológico",
    "Pharmacological Researcher",
    "Pharmacologist Specialist",
    "Pharmaceutical Expert",
    "Pharmacology Researcher",
}

# # Define patterns (these should NOT be changed)
# pharmacologist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

pharmacologist_exclusions = {
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

# Create a mask for Pharmacologist
mask_pharmacologist = df['speciality'].str.contains('|'.join(pharmacologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(pharmacologist_exact_matches)

# mask_pharmacologist_exclusions = df['speciality'].str.contains(pharmacologist_exclusions, case=False, na=False, regex=True)
mask_pharmacologist_exclusions = df['speciality'].isin(pharmacologist_exclusions)

# Final mask: Select Pharmacologist
mask_pharmacologist_final = mask_pharmacologist & ~mask_pharmacologist_exclusions

# Store the original values that will be replaced
original_pharmacologist_values = df.loc[mask_pharmacologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_pharmacologist_final, 'speciality'] = 'Pharmacologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Pharmacologist", 'green'))
print(df.loc[mask_pharmacologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_pharmacologist_values = df.loc[mask_pharmacologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Pharmacologist", "cyan"))
for original_pharmacologist_value in original_pharmacologist_values:
    print(f"✅ {original_pharmacologist_value} → Pharmacologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Pharmacologist:", 'red'))
print(grouped_pharmacologist_values)

# Print summary
matched_count_pharmacologist = mask_pharmacologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Pharmacologist: "
        f"{matched_count_pharmacologist}",
        'red'))