import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Pediatrician related titles

pediatrician_variants = [
    # Standard Titles & Variants
    r"(?i)\bPediatrician\b",
    r"(?i)\bPediatrist\b",
    r"(?i)\bPediatrics Specialist\b",
    r"(?i)\bPediatric Doctor\b",
    r"(?i)\bChild Specialist\b",
    r"(?i)\bPediatrics Physician\b",
    r"(?i)\bPediatric Consultant\b",
    r"(?i)\bPediatric Specialist\b",
    r"(?i)\bPediatric Practitioner\b",
    r"(?i)\bPediatric Surgeon\b",
    r"(?i)\bGeneral Pediatrician\b",
    r"(?i)\bPediatrician Consultant\b",
    r"(?i)\bConsultant Pediatrician\b",
    r"(?i)Paediatrics",
    r"(?i)\bPaediatric Surgery\b",
    r"(?i)\bPaediatrician\b",

    # Misspellings & Typographical Errors
    r"(?i)\bPediatrition\b",
    r"(?i)\bPediatrition\b",
    r"(?i)\bPedriatrician\b",
    r"(?i)\bPeditrician\b",
    r"(?i)\bPedatrician\b",
    r"(?i)\bPediatrion\b",
    r"(?i)\bPediatrian\b",

    # Case Variations
    r"(?i)\bpediatrician\b",
    r"(?i)\bPEDIATRICIAN\b",
    r"(?i)\bPeDiAtRiCiAn\b",
    r"(?i)\bPediatriCian\b",

    # Spanish Variants
    r"(?i)\bPediatra\b",
    r"(?i)\bPediatra\s?General\b",
    r"(?i)\bPediatra\s?Especialista\b",
    r"(?i)\bMédico\s?Pediatra\b",
    r"(?i)\bPediatra\s?Consultor\b",
    r"(?i)\bPediatra\s?Infantil\b",
    r"(?i)\bPediatra\s?Pediátrico\b",
    r"(?i)\bPediatra\s?Cirujano\b",
    r"(?i)\bPediatra\s?Generalista\b",

    # Other Possible Variations
    r"(?i)\bPediatric Physician\b",
    r"(?i)\bPediatric Consultant\b",
    r"(?i)\bPediatric Specialist\b",
    r"(?i)\bPediatric Doctor\b",
    r"(?i)\bChild Healthcare Professional\b",
    r"(?i)\bPediatric Surgeon\b",
]

# Exact matches that should be updated
pediatrician_exact_matches = {
    "Pediatrician",
    "Pediatrist",
    "Pediatrics Specialist",
    "Pediatric Doctor",
    "Child Specialist",
    "Pediatrics Physician",
    "Pediatric Consultant",
    "Pediatric Specialist",
    "Pediatric Practitioner",
    "Pediatric Surgeon",
    "General Pediatrician",
    "Pediatrician Consultant",
    "Consultant Pediatrician",
    "Pediatrtion",
    "Pediatrition",
    "Pedriatrician",
    "Peditrician",
    "Pedatrician",
    "Pediatrion",
    "Pediatrian",
    "Pediatra",
    "Pediatra General",
    "Pediatra Especialista",
    "Médico Pediatra",
    "Pediatra Consultor",
    "Pediatra Infantil",
    "Pediatra Pediátrico",
    "Pediatra Cirujano",
    "Pediatra Generalista",
    "Pediatric Physician",
    "Child Healthcare Professional",
}

# # Define patterns (these should NOT be changed)
# pediatrician_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

pediatrician_exclusions = {
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
    'Pediatric Physician Recruiter',
}

# Create a mask for Pediatrician
mask_pediatrician = df['speciality'].str.contains('|'.join(pediatrician_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(pediatrician_exact_matches)

# mask_pediatrician_exclusions = df['speciality'].str.contains(pediatrician_exclusions, case=False, na=False, regex=True)
mask_pediatrician_exclusions = df['speciality'].isin(pediatrician_exclusions)

# Final mask: Select Pediatrician
mask_pediatrician_final = mask_pediatrician & ~mask_pediatrician_exclusions

# Store the original values that will be replaced
original_pediatrician_values = df.loc[mask_pediatrician_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_pediatrician_final, 'speciality'] = 'Pediatrician'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Pediatrician", 'green'))
print(df.loc[mask_pediatrician_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_pediatrician_values = df.loc[mask_pediatrician_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Pediatrician", "cyan"))
for original_pediatrician_value in original_pediatrician_values:
    print(f"✅ {original_pediatrician_value} → Pediatrician")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Pediatrician:", 'red'))
print(grouped_pediatrician_values)

# Print summary
matched_count_pediatrician = mask_pediatrician_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Pediatrician: "
        f"{matched_count_pediatrician}",
        'red'))