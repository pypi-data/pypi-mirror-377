import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Lawyer related titles

lawyer_variants = [
    r"(?i)\bLawyer\b",
    r"(?i)\bAttorney\b",
    r"(?i)\bLegal\s?Advisor\b",
    r"(?i)\bSolicitor\b",

    # Common misspellings and case errors
    r"(?i)\bLwyer\b",
    r"(?i)\bLawer\b",
    r"(?i)\bLoyer\b",
    r"(?i)\bAtorney\b",
    r"(?i)\bAttorny\b",

    # Spanish variants
    r"(?i)\bAbogado\b",
    r"(?i)\bAbogada\b",
    r"(?i)\bAbogado/a\b",
    r"(?i)\bAbogado/a de defensa\b",
    r"(?i)\bAbogado/a corporativo\b",
    r"(?i)\bLicenciado en Derecho\b",

    # Other possible variations
    r"(?i)\bCriminal\s?Lawyer\b",
    r"(?i)\bCivil\s?Lawyer\b",
    r"(?i)\bCorporate\s?Lawyer\b",
    r"(?i)\bFamily\s?Lawyer\b",
    r"(?i)\bPersonal\s?Injury\s?Lawyer\b",
    r"(?i)\bLaw\b",
]

# Exact matches that should be updated
lawyer_exact_matches = {
    "Lawyer",
    "Attorney",
    "Legal Advisor",
    "Solicitor",
    # Misspellings
    "Lwyer",
    "Lawer",
    "Loyer",
    "Atorney",
    "Attorny",
    # Spanish variants
    "Abogado",
    "Abogada",
    "Abogado/a",
    "Abogado/a de defensa",
    "Abogado/a corporativo",
    "Licenciado en Derecho",
    # Other possible variations
    "Criminal Lawyer",
    "Civil Lawyer",
    "Corporate Lawyer",
    "Family Lawyer",
    "Personal Injury Lawyer",
}

# Define patterns (these should NOT be changed)
lawyer_exclusions = {
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

# Create a mask for Lawyer
mask_lawyer = df['speciality'].str.contains('|'.join(lawyer_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(lawyer_exact_matches)
mask_lawyer_exclusions = df['speciality'].isin(lawyer_exclusions)

# Final mask: Select Lawyer
mask_lawyer_final = mask_lawyer & ~mask_lawyer_exclusions

# Store the original values that will be replaced
original_lawyer_values = df.loc[mask_lawyer_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_lawyer_final, 'speciality'] = 'Lawyer'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Lawyer", 'green'))
print(df.loc[mask_lawyer_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_lawyer_values = df.loc[mask_lawyer_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Lawyer", "cyan"))
for original_lawyer_value in original_lawyer_values:
    print(f"✅ {original_lawyer_value} → Lawyer")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Lawyer:", 'red'))
print(grouped_lawyer_values)

# Print summary
matched_count_lawyer = mask_lawyer_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Lawyer: "
        f"{matched_count_lawyer}",
        'red'))