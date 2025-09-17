import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Pathologist related titles

pathologist_variants = [
    # Standard Titles & Variants
    r"(?i)\bPathologist\b",
    r"(?i)\bClinical Pathologist\b",
    r"(?i)\bMedical Pathologist\b",
    r"(?i)\bAnatomic Pathologist\b",
    r"(?i)\bForensic Pathologist\b",
    r"(?i)\bPathology Consultant\b",
    r"(?i)\bConsultant Pathologist\b",
    r"(?i)\bLaboratory Pathologist\b",
    r"(?i)\bHistopathologist\b",
    r"(?i)\bHematopathologist\b",
    r"(?i)\bMolecular Pathologist\b",
    r"(?i)\bGeneral Pathologist\b",
    r"(?i)\bPediatric Pathologist\b",
    r"(?i)\bPathology\b",

    # Misspellings & Typographical Errors
    r"(?i)\bPathologiest\b",
    r"(?i)\bPatholigist\b",
    r"(?i)\bPatologist\b",
    r"(?i)\bPatholigist\b",
    r"(?i)\bPthologist\b",
    r"(?i)\bPatholigist\b",

    # Case Variations
    r"(?i)\bpathologist\b",
    r"(?i)\bPaThOlOgIsT\b",
    r"(?i)\bPATHOLOGIST\b",
    r"(?i)\bPaThOlOgIsT\b",

    # Spanish Variants
    r"(?i)\bPatólogo\b",
    r"(?i)\bPatóloga\b",
    r"(?i)\bPatólogo\s?Clínico\b",
    r"(?i)\bPatólogo\s?Médico\b",
    r"(?i)\bPatólogo\s?Anatómico\b",
    r"(?i)\bPatólogo\s?Forense\b",
    r"(?i)\bConsultor\s?Patólogo\b",
    r"(?i)\bPatólogo\s?Consultor\b",
    r"(?i)\bLaboratorio\s?Patólogo\b",
    r"(?i)\bHematopatólogo\b",
    r"(?i)\bPatólogo\s?Molecular\b",
    r"(?i)\bPatólogo\s?General\b",
    r"(?i)\bPatólogo\s?Pediátrico\b",

    # Other Possible Variations
    r"(?i)\bPathology\s?Consultant\b",
    r"(?i)\bLaboratory\s?Pathologist\b",
    r"(?i)\bPathologist\s?Specialist\b",
    r"(?i)\bCertified\s?Pathologist\b",
    r"(?i)\bSenior\s?Pathologist\b",
    r"(?i)\bJunior\s?Pathologist\b",
    r"(?i)\bExpert\s?Pathologist\b",
    r"(?i)\bMedical\s?Pathology\s?Consultant\b",
]

# Exact matches that should be updated
pathologist_exact_matches = {
    "Pathologist",
    "Clinical Pathologist",
    "Medical Pathologist",
    "Anatomic Pathologist",
    "Forensic Pathologist",
    "Pathology Consultant",
    "Consultant Pathologist",
    "Laboratory Pathologist",
    "Histopathologist",
    "Hematopathologist",
    "Molecular Pathologist",
    "General Pathologist",
    "Pediatric Pathologist",
    "Pathologiest",
    "Patholigist",
    "Patologist",
    "Pthologist",
    "Patólogo",
    "Patóloga",
    "Patólogo Clínico",
    "Patólogo Médico",
    "Patólogo Anatómico",
    "Patólogo Forense",
    "Consultor Patólogo",
    "Patólogo Consultor",
    "Laboratorio Patólogo",
    "Hematopatólogo",
    "Patólogo Molecular",
    "Patólogo General",
    "Patólogo Pediátrico",
    "Pathologist Specialist",
    "Certified Pathologist",
    "Senior Pathologist",
    "Junior Pathologist",
    "Expert Pathologist",
    "Medical Pathology Consultant",
    'Biopathologist Antiaging Medicine',
    'Medica Patologista',
}

# # Define patterns (these should NOT be changed)
# pathologist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

pathologist_exclusions = {
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
    'Client Developer - Pathology & Dermatology',
}

# Create a mask for Pathologist
mask_pathologist = df['speciality'].str.contains('|'.join(pathologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(pathologist_exact_matches)

# mask_pathologist_exclusions = df['speciality'].str.contains(pathologist_exclusions, case=False, na=False, regex=True)
mask_pathologist_exclusions = df['speciality'].isin(pathologist_exclusions)

# Final mask: Select Pathologist
mask_pathologist_final = mask_pathologist & ~mask_pathologist_exclusions

# Store the original values that will be replaced
original_pathologist_values = df.loc[mask_pathologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_pathologist_final, 'speciality'] = 'Pathologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Pathologist", 'green'))
print(df.loc[mask_pathologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_pathologist_values = df.loc[mask_pathologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Pathologist", "cyan"))
for original_pathologist_value in original_pathologist_values:
    print(f"✅ {original_pathologist_value} → Pathologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Pathologist:", 'red'))
print(grouped_pathologist_values)

# Print summary
matched_count_pathologist = mask_pathologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Pathologist: "
        f"{matched_count_pathologist}",
        'red'))