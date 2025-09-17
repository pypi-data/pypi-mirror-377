import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Orthopedist related titles

orthopedist_variants = [
    # Standard Titles & Abbreviations
    r"(?i)\bOrthopedist\b",
    r"(?i)\bOrthopedic\s?Doctor\b",
    r"(?i)\bOrthopedic\s?Surgeon\b",
    r"(?i)\bOrtho\s?Doctor\b",
    r"(?i)\bOrtho\s?Specialist\b",
    r"(?i)\bOrthopedics\s?Practitioner\b",
    r"(?i)\bOrthopedics\s?Consultant\b",
    r"(?i)\bMD\s?Orthopedics\b",
    r"(?i)\bDMD\s?Orthopedics\b",
    r"(?i)\bProsthetist & Orthotist\b",
    r"(?i)\bTraumatology\b",

    # Misspellings & Typographical Errors
    r"(?i)\bOrthopaedist\b",
    r"(?i)\bOrtopedist\b",
    r"(?i)\bOrthopediest\b",
    r"(?i)\bOrthepedist\b",
    r"(?i)\bOrthopeedist\b",
    r"(?i)\bOrthopedics\s?Doctor\b",

    # Case Variations
    r"(?i)\borthopedist\b",
    r"(?i)\bOrthopedIst\b",
    r"(?i)\bORTHOPEDIST\b",
    r"(?i)\bOrThOpEdIsT\b",

    # Spanish Variants
    r"(?i)\bOrtopedista\b",
    r"(?i)\bDoctor\s?en\s?Ortopedia\b",
    r"(?i)\bCirujano\s?Ortopédico\b",
    r"(?i)\bEspecialista\s?en\s?Ortopedia\b",

    # Other Possible Variations (Including Doctor forms, Specialist forms)
    r"(?i)\bOrthopedic\s?Expert\b",
    r"(?i)\bOrthopedic\s?Consultant\b",
    r"(?i)\bSpecialist\s?in\s?Orthopedics\b",
    r"(?i)\bOrthopedics\s?Surgeon\b",
]

# Exact matches that should be updated
orthopedist_exact_matches = {
    "Orthopedist",
    "Orthopedic Doctor",
    "Orthopedic Surgeon",
    "Ortho Doctor",
    "Ortho Specialist",
    "Orthopedics Practitioner",
    "Orthopedics Consultant",
    "MD Orthopedics",
    "DMD Orthopedics",
    "Orthopaedist",
    "Ortopedist",
    "Orthopediest",
    "Orthepedist",
    "Orthopeedist",
    "Orthopedics Doctor",
    "Ortopedista",
    "Doctor en Ortopedia",
    "Cirujano Ortopédico",
    "Especialista en Ortopedia",
    "Orthopedic Expert",
    "Orthopedic Consultant",
    "Specialist in Orthopedics",
    "Orthopedics Surgeon",
    'Orthopedic',
    'orthopedic',
    'Orthopedics',
    'orthopedics',
    'Consultant Orthopaedics',
    'Consultant Trauma & Orthopaedic Surgery',
    'KieferorthopadieAsthetik',
    'Orthopaedics',
}

# # Define patterns (these should NOT be changed)
# orthopedist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

orthopedist_exclusions = {
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

# Create a mask for Orthopedist
mask_orthopedist = df['speciality'].str.contains('|'.join(orthopedist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(orthopedist_exact_matches)

# mask_orthopedist_exclusions = df['speciality'].str.contains(orthopedist_exclusions, case=False, na=False, regex=True)
mask_orthopedist_exclusions = df['speciality'].isin(orthopedist_exclusions)

# Final mask: Select Orthopedist
mask_orthopedist_final = mask_orthopedist & ~mask_orthopedist_exclusions

# Store the original values that will be replaced
original_orthopedist_values = df.loc[mask_orthopedist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_orthopedist_final, 'speciality'] = 'Orthopedist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Orthopedist", 'green'))
print(df.loc[mask_orthopedist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_orthopedist_values = df.loc[mask_orthopedist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Orthopedist", "cyan"))
for original_orthopedist_value in original_orthopedist_values:
    print(f"✅ {original_orthopedist_value} → Orthopedist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Orthopedist:", 'red'))
print(grouped_orthopedist_values)

# Print summary
matched_count_orthopedist = mask_orthopedist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Orthopedist: "
        f"{matched_count_orthopedist}",
        'red'))