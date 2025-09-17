import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Biomedical Physician related titles

biomedical_physician_variants = [
    r"(?i)\bBiomedical\s?Physician\b",
    r"(?i)\bBiomedical\s?Doctor\b",
    r"(?i)\bBiomedical\s?Specialist\b",
    r"(?i)\bMedical\s?Doctor\s?Specialist\b",
    r"(?i)\bBiomedical\s?Medicine\s?Physician\b",
    r"(?i)\bBiomed\s?Physician\b",
    r"(?i)\bBiomed\s?Specialist\b",
    r"(?i)\bDoctor\s?of\s?Biomedical\s?Science\b",
    r"(?i)\bAesthetic Biomedicine\b",
    r"(?i)\bBiomedicina Estetica\b",
    r"(?i)\bMedical Doctor- Regenerative Medicine\b",
    r"(?i)\bAesthetics & Regenerative Medicine\b",
]

# Exact matches that should be updated
biomedical_physician_exact_matches = {
    'Biomedical Physician',
    'Biomedical Doctor',
    'Biomedical Specialist',
    'Biomedical physician',
    'Biomed Physician',
    'Biomed Specialist',
    'Doctor of Biomedical Science',
    'Biomedical Medicine Physician',
    'Medical Doctor Specialist',
    'Biomedical Expert',
    'Biomedica',
    'Biomedical',
    'Biomedic',
    'Biomedico',

    # Case-related errors
    'biomedical physician',
    'biomedical doctor',
    'biomedical specialist',
    'biomed physician',
    'biomed specialist',
    'BIOMEDICAL PHYSICIAN',
    'BIOMEDICAL DOCTOR',
    'BIOMEDICAL SPECIALIST',
    'BIOMED PHYSICIAN',
    'BIOMED SPECIALIST',

    # Common misspellings
    'Biomedic Physician',
    'Biomedial Physician',
    'Bimolecular Physician',
    'Biodical Physician',
    'Biomedical Physiscian',
    'Biomedic Doctor',
    'Bimolecular Doctor',
    'Biomedic Specalist',
    'Biomed Specialist',
    'BioMed Doc',
    'Biomendical Physician',

    # Spanish-related exclusions
    'Médico Biomédico',
    'Doctor Biomédico',
    'Especialista en Medicina Biomédica',
    'Especialista Biomédico',
    'Médico especialista en Biomedicina',
    'Médico en Ciencias Biomédicas',
    'Doctor en Ciencias Biomédicas',
    'Médico Biomedicina',
    'Regenerative Medicine',
    'regenerative medicine',
    'Regenerative medicine',
    'Biomedica Esteta',
    'Aesthetic Biomedical',
    'Biomedicine',
    'Regenerative Preventive & Aesthetic Medicine',
    'Aesthetics Degenerative Medicine',
    'Magister Biomedis',
    'Biomedicina',
    'International Leader in Molecular Medicine',
    'Biodoctor',
    'Biomedica esteta',
}

# Define patterns for  & Resident & Professor (these should NOT be changed)
biomedical_physician_exclusions = {
    'Resident',
    'resident',
    'student',
    'Trainee',
    'Resident Doctor',
    'Resident Physician',
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

# Create a mask for Biomedical Physician
mask_biomedical_physician = df['speciality'].str.contains('|'.join(biomedical_physician_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(biomedical_physician_exact_matches)
mask_biomedical_physician_exclusions = df['speciality'].isin(biomedical_physician_exclusions)

# Final mask: Select Biomedical Physician
mask_biomedical_physician_final = mask_biomedical_physician & ~mask_biomedical_physician_exclusions

# Store the original values that will be replaced
original_biomedical_physician_values = df.loc[mask_biomedical_physician_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_biomedical_physician_final, 'speciality'] = 'Biomedical Physician'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Biomedical Physician", 'green'))
print(df.loc[mask_biomedical_physician_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_biomedical_physician_values = df.loc[mask_biomedical_physician_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Biomedical Physician", "cyan"))
for original_biomedical_physician_value in original_biomedical_physician_values:
    print(f"✅ {original_biomedical_physician_value} → Biomedical Physician")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Biomedical Physician:", 'red'))
print(grouped_biomedical_physician_values)

# Print summary
matched_count_biomedical_physician = mask_biomedical_physician_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Biomedical Physician: "
        f"{matched_count_biomedical_physician}",
        'red'))