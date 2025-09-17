import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Laboratory Medicine related titles

laboratory_medicine_variants = [
    r"(?i)\bLaboratory\s?Medicine\b",
    r"(?i)\bLab\s?Medicine\b",

    # Common misspellings and case errors
    r"(?i)\bLabratory\s?Medicine\b",
    r"(?i)\bLabortory\s?Medicine\b",
    r"(?i)\bLaborotory\s?Medicine\b",
    r"(?i)\bLaboratry\s?Medicine\b",
    r"(?i)\bLab Medicine\b",
    r"(?i)\bLabortary\s?Medicine\b",

    # Spanish variants
    r"(?i)\bMedicina\s?de\s?Laboratorio\b",
    r"(?i)\bMédico\s?de\s?Laboratorio\b",
    r"(?i)\bEspecialista\s?en\s?Medicina\s?de\s?Laboratorio\b",
    r"(?i)\bLaboratorio\s?Clínico\b",

    # Other possible variations
    r"(?i)\bLaboratory\s?Medicine\s?Specialist\b",
    r"(?i)\bLaboratory\s?Medicine\s?Physician\b",
    r"(?i)\bLaboratory\s?Medicine\s?Doctor\b",
    r"(?i)\bClinical\s?Laboratory\s?Specialist\b",
    r"(?i)\bBoard\s?Certified\s?Laboratory\s?Medicine\s?Doctor\b",
    r"(?i)\bMedico Laboral\b",
    r"(?i)Laboral",
    r"(?i)\bMagister En Analisis Y Diagnostico De Laboratorio\b",
    r"(?i)\bLaboratory Medicine\b",
    r"(?i)\bLaboratory Specialist\b",
    r"(?i)\bMedical Laboratory Technician\b",
    r"(?i)\bHead Of Laboratory\b",
    r"(?i)\bMagister En Analisis Y Diagnostico De Laboratorio\b",
    r"(?i)\bManager- Laboratory Services\b",
    r"(?i)\bLaboratory Manager\b",
    r"(?i)\bLaboratory Scientist\b",
    r"(?i)\bMedico Laboral\b",
    r"(?i)\bMedical Laboratory ScientistClinical Laboratory Technologist\b",
    r"(?i)\bMedical Laboratory Scientists\b",
    r"(?i)\bPrincipal Investigator & Head Of Laboratory\b",
    r"(?i)\bConstruction Forman Three Year Expriance & Constrction Material Laboratory 8 Years Expriance\b",
    r"(?i)\bLaboratory Technician\b",
    r"(?i)\bHead Of Laboratory Department\b",
    r"(?i)\bMedical Laboratory\b",
]

# Exact matches that should be updated
laboratory_medicine_exact_matches = {
    "Laboratory Medicine",
    "Lab Medicine",
    # Misspellings
    "Labratory Medicine",
    "Labortory Medicine",
    "Laborotory Medicine",
    "Laboratry Medicine",
    "Labortary Medicine",
    # Spanish variants
    "Medicina de Laboratorio",
    "Médico de Laboratorio",
    "Especialista en Medicina de Laboratorio",
    "Laboratorio Clínico",
    # Other possible variations
    "Laboratory Medicine Specialist",
    "Laboratory Medicine Physician",
    "Laboratory Medicine Doctor",
    "Clinical Laboratory Specialist",
    "Board Certified Laboratory Medicine Doctor",
    'Laboratory',
    'laboratory',
    'Lab',
    'lab',
}

# Define patterns (these should NOT be changed)
laboratory_medicine_exclusions = {
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

# Create a mask for Laboratory Medicine
mask_laboratory_medicine = df['speciality'].str.contains('|'.join(laboratory_medicine_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(laboratory_medicine_exact_matches)
mask_laboratory_medicine_exclusions = df['speciality'].isin(laboratory_medicine_exclusions)

# Final mask: Select Laboratory Medicine
mask_laboratory_medicine_final = mask_laboratory_medicine & ~mask_laboratory_medicine_exclusions

# Store the original values that will be replaced
original_laboratory_medicine_values = df.loc[mask_laboratory_medicine_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_laboratory_medicine_final, 'speciality'] = 'Laboratory Medicine'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Laboratory Medicine", 'green'))
print(df.loc[mask_laboratory_medicine_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_laboratory_medicine_values = df.loc[mask_laboratory_medicine_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Laboratory Medicine", "cyan"))
for original_laboratory_medicine_value in original_laboratory_medicine_values:
    print(f"✅ {original_laboratory_medicine_value} → Laboratory Medicine")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Laboratory Medicine:", 'red'))
print(grouped_laboratory_medicine_values)

# Print summary
matched_count_laboratory_medicine = mask_laboratory_medicine_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Laboratory Medicine: "
        f"{matched_count_laboratory_medicine}",
        'red'))