import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for biologist_biochemist related titles

biologist_biochemist_variants = [
    r"(?i)\bBiologist\b",
    r"(?i)\bBiochemist\b",
    r"(?i)\bBiologist\s?Doctor\b",
    r"(?i)\bBiochemist\s?Doctor\b",
    r"(?i)\bBiologist\s?Specialist\b",
    r"(?i)\bBiochemist\s?Specialist\b",
    r"(?i)\bBiologist\s?Expert\b",
    r"(?i)\bBiochemist\s?Expert\b",
    r"(?i)\bBiology\s?Doctor\b",
    r"(?i)\bBiochemistry\s?Doctor\b",
    r"(?i)\bBiology\s?Specialist\b",
    r"(?i)\bBiochemistry\s?Specialist\b",
    r"(?i)\bFormulator\b",
    r"(?i)\bBiologist/Biochemist\b",
    r"(?i)\bBiologistBiochemist\b",
    r"(?i)\bBiologia Molecular E Estetica\b",
    r"(?i)\bBiotechnology Skincare\b",
    r"(?i)\bMicrobiome\b",
    r"(?i)\bBioanalytiker\b",
    r"(?i)\bBioquimica\b",
    r"(?i)\bBitoulogue\b",
    r"(?i)\bChemistry\b",
]

# Exact matches that should be updated
biologist_biochemist_exact_matches = {
    'Biologist',
    'Biochemist',
    'Biologist Doctor',
    'Biochemist Doctor',
    'Biologist/Biochemist',
    'BiologistBiochemist',
    'Formulator',
    'Biologist Specialist',
    'Biochemist Specialist',
    'Biologist Expert',
    'BiologistBiochemist',
    'Biochemist Expert',
    'Biology Doctor',
    'Biochemistry Doctor',
    'Biology Specialist',
    'Biochemistry Specialist',
    'Biology Physician',
    'Biochemistry Physician',
    'Biochemist MD',
    'Biologist MD',
    'PhD Biologist',
    'PhD Biochemist',

    # Case-related errors
    'biologist',
    'biochemist',
    'BIOLOGIST',
    'BIOCHEMIST',
    'BiOlOgIsT',
    'BiOcHeMiSt',
    'biology doctor',
    'biochemistry doctor',
    'biology specialist',
    'biochemistry specialist',

    # Common misspellings
    'Bioligist',
    'Bilogist',
    'Biochemest',
    'Biochemis',
    'Biologyist',
    'Bilogist',
    'Biologist Doctorate',
    'Biochemist Docter',
    'Bilogist Doctor',
    'Bioochemist',
    'Biyochemist',

    # Spanish-related exclusions
    'Biólogo',
    'Bióloga',
    'Bioquímico',
    'Bioquímica',
    'Doctor en Biología',
    'Doctor en Bioquímica',
    'Especialista en Biología',
    'Especialista en Bioquímica',
    'Médico Biólogo',
    'Médico Bioquímico',
    'Biólogo especialista',
    'Bioquímico especialista',
    'G MBiologist',
    'Medecin Biologiste',
    'Medical Biotechnologist',
    'Biolog',
}

# Define patterns for  & Resident & Professor (these should NOT be changed)
biologist_biochemist_exclusions = {
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

# Create a mask for Biologist Biochemist
mask_biologist_biochemist = df['speciality'].str.contains('|'.join(biologist_biochemist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(biologist_biochemist_exact_matches)
mask_biologist_biochemist_exclusions = df['speciality'].isin(biologist_biochemist_exclusions)

# Final mask: Select Biologist Biochemist
mask_biologist_biochemist_final = mask_biologist_biochemist & ~mask_biologist_biochemist_exclusions

# Store the original values that will be replaced
original_biologist_biochemist_values = df.loc[mask_biologist_biochemist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_biologist_biochemist_final, 'speciality'] = 'Biologist Biochemist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Biologist Biochemist", 'green'))
print(df.loc[mask_biologist_biochemist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_biologist_biochemist_values = df.loc[mask_biologist_biochemist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Biologist Biochemist", "cyan"))
for original_biologist_biochemist_value in original_biologist_biochemist_values:
    print(f"✅ {original_biologist_biochemist_value} → Biologist Biochemist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Biologist Biochemist:", 'red'))
print(grouped_biologist_biochemist_values)

# Print summary
matched_count_biologist_biochemist = mask_biologist_biochemist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Biologist Biochemist: "
        f"{matched_count_biologist_biochemist}",
        'red'))