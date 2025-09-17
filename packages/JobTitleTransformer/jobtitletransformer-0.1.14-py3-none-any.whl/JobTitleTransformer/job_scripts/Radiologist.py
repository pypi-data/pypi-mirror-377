import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Radiologist related titles

radiologist_variants = [
    # Standard Titles & Variants
    r"(?i)\bRadiologist\b",
    r"(?i)\bMedical Radiologist\b",
    r"(?i)\bRadiology Specialist\b",
    r"(?i)\bDiagnostic Radiologist\b",
    r"(?i)\bRadiology Consultant\b",
    r"(?i)\bInterventional Radiologist\b",
    r"(?i)\bNeuro Radiologist\b",
    r"(?i)\bSr  Radiographer\b",
    r"(?i)\bRadiology\b",
    r"(?i)\bUltrasound\b",

    # Misspellings & Typographical Errors
    r"(?i)\bRadioligist\b",
    r"(?i)\bRadialogist\b",
    r"(?i)\bRaadiologist\b",
    r"(?i)\bRaadiologyst\b",
    r"(?i)\bRadilogist\b",
    r"(?i)\bRaddiologist\b",
    r"(?i)\bRaodiologist\b",
    r"(?i)\bRadiolgist\b",

    # Case Variations
    r"(?i)\bRADIOLOGIST\b",
    r"(?i)\bradiologist\b",
    r"(?i)\bRaDiOlOgIsT\b",
    r"(?i)\bRADIOLIGIST\b",

    # Spanish Variants
    r"(?i)\bRadiólogo\b",
    r"(?i)\bEspecialista en Radiología\b",
    r"(?i)\bRadiólogo Clínico\b",
    r"(?i)\bRadiólogo de Diagnóstico\b",
    r"(?i)\bRadiólogo Intervencionista\b",
    r"(?i)\bRadiólogo Neurobiólogo\b",
    r"(?i)\bRadiólogo General\b",
    r"(?i)\bRadiólogo Oncológico\b",

    # Hybrid Spanish-English Variants
    r"(?i)\bRadiologist en diagnóstico\b",
    r"(?i)\bRadiologist Intervencionista\b",

    # Other Possible Variations (Doctor Forms, Specialist Forms)
    r"(?i)\bDiagnostic Imaging Specialist\b",
    r"(?i)\bRadiology Technician\b",
    r"(?i)\bImaging Specialist\b",
    r"(?i)\bX-ray Specialist\b",
    r"(?i)\bCT Scan Specialist\b",
    r"(?i)\bMRI Specialist\b",
    r"(?i)\bInterventional Imaging Specialist\b",
]

# Exact matches that should be updated
radiologist_exact_matches = {
    "Radiologist",
    "Medical Radiologist",
    "Radiology Specialist",
    "Diagnostic Radiologist",
    "Radiology Consultant",
    "Interventional Radiologist",
    "Neuro Radiologist",
    "Radioligist",
    "Radialogist",
    "Raadiologist",
    "Raadiologyst",
    "Radilogist",
    "Raddiologist",
    "Raodiologist",
    "Radiolgist",
    "Radiólogo",
    "Especialista en Radiología",
    "Radiólogo Clínico",
    "Radiólogo de Diagnóstico",
    "Radiólogo Intervencionista",
    "Radiólogo Neurobiólogo",
    "Radiólogo General",
    "Radiólogo Oncológico",
    "Radiologist en diagnóstico",
    "Radiologist Intervencionista",
    "Diagnostic Imaging Specialist",
    "Radiology Technician",
    "Imaging Specialist",
    "X-ray Specialist",
    "CT Scan Specialist",
    "MRI Specialist",
    "Interventional Imaging Specialist",
    'RadiographerAesthetics',
}

# # Define patterns (these should NOT be changed)
# radiologist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

radiologist_exclusions = {
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

# Create a mask for Radiologist
mask_radiologist = df['speciality'].str.contains('|'.join(radiologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(radiologist_exact_matches)

# mask_radiologist_exclusions = df['speciality'].str.contains(radiologist_exclusions, case=False, na=False, regex=True)
mask_radiologist_exclusions = df['speciality'].isin(radiologist_exclusions)

# Final mask: Select Radiologist
mask_radiologist_final = mask_radiologist & ~mask_radiologist_exclusions

# Store the original values that will be replaced
original_radiologist_values = df.loc[mask_radiologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_radiologist_final, 'speciality'] = 'Radiologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Radiologist", 'green'))
print(df.loc[mask_radiologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_radiologist_values = df.loc[mask_radiologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Radiologist", "cyan"))
for original_radiologist_value in original_radiologist_values:
    print(f"✅ {original_radiologist_value} → Radiologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Radiologist:", 'red'))
print(grouped_radiologist_values)

# Print summary
matched_count_radiologist = mask_radiologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Radiologist: "
        f"{matched_count_radiologist}",
        'red'))