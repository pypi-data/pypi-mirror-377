import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Legal Counsel related titles

legal_counsel_variants = [
    r"(?i)\bLegal\s?Counsel\b",
    r"(?i)\bCounselor\b",
    r"(?i)\bLegal\s?Advisor\b",
    r"(?i)\bIn-House\s?Counsel\b",
    r"(?i)\bGeneral\s?Counsel\b",
    r"(?i)\bCorporate\s?Counsel\b",

    # Misspellings and case errors
    r"(?i)\bLegel\s?Counsel\b",
    r"(?i)\bLegel\s?Cousel\b",
    r"(?i)\bLagal\s?Counsel\b",
    r"(?i)\bLega\s?Counsel\b",
    r"(?i)\bLegal\s?Consel\b",

    # Spanish variants
    r"(?i)\bAsesor\s?Legal\b",
    r"(?i)\bConsejero\s?Legal\b",
    r"(?i)\bConsejero\s?Jurídico\b",
    r"(?i)\bAbogado\s?Corporativo\b",
    r"(?i)\bAsesor\s?Corporativo\b",
    r"(?i)\bAsesor\s?In-House\b",

    # Other possible variations
    r"(?i)\bContract\s?Counsel\b",
    r"(?i)\bLitigation\s?Counsel\b",
    r"(?i)\bEmployment\s?Counsel\b",
    r"(?i)\bTax\s?Counsel\b",
    r"(?i)\bLegal\s?Consultant\b",
    r"(?i)\bCompliance\s?Counsel\b",
    r"(?i)\bMergers\s?and\s?Acquisitions\s?Counsel\b",
    r"(?i)Regulatory Affairs",
    r"(?i)\bInternational Affairs Lead\b",
    r"(?i)\bCharge DAffaires\b",
    r"(?i)\bManager - Regulatory Compliance & Clinical Science Liaison\b",
    r"(?i)\bHead Corporate Affairs\b",
    r"(?i)\bAccreditation Officer\b",
    r"(?i)\bTranslater\b",
    r"(?i)\bRegistrar\b",
    r"(?i)\bAuditor\b",
    r"(?i)\bEquity\b",
    r"(?i)\bCompliance\b",
    r"(?i)\bScientific Document Management Associate\b",
    r"(?i)\bTranslator\b",
    r"(?i)\bLegal Assistant\b",
    r"(?i)\bManager of External Affairs\b",
]

# Exact matches that should be updated
legal_counsel_exact_matches = {
    "Legal Counsel",
    "Counselor",
    "Legal Advisor",
    "In-House Counsel",
    "General Counsel",
    "Corporate Counsel",
    # Misspellings and case errors
    "Legel Counsel",
    "Legel Cousel",
    "Lagal Counsel",
    "Lega Counsel",
    "Legal Consel",
    # Spanish variants
    "Asesor Legal",
    "Consejero Legal",
    "Consejero Jurídico",
    "Abogado Corporativo",
    "Asesor Corporativo",
    "Asesor In-House",
    # Other possible variations
    "Contract Counsel",
    "Litigation Counsel",
    "Employment Counsel",
    "Tax Counsel",
    "Legal Consultant",
    "Compliance Counsel",
    "Mergers and Acquisitions Counsel",
    'Medical Writer',
    'Writing',
    'Director Public Affairs',
    'Interpreting',
    'Corporate Advisor',
}

# Define patterns (these should NOT be changed)
legal_counsel_exclusions = {
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
    'Dermatology Health Equity Marketing Lead',
}

# Create a mask for Legal Counsel
mask_legal_counsel = df['speciality'].str.contains('|'.join(legal_counsel_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(legal_counsel_exact_matches)
mask_legal_counsel_exclusions = df['speciality'].isin(legal_counsel_exclusions)

# Final mask: Select Legal Counsel
mask_legal_counsel_final = mask_legal_counsel & ~mask_legal_counsel_exclusions

# Store the original values that will be replaced
original_legal_counsel_values = df.loc[mask_legal_counsel_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_legal_counsel_final, 'speciality'] = 'Legal Counsel'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Legal Counsel", 'green'))
print(df.loc[mask_legal_counsel_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_legal_counsel_values = df.loc[mask_legal_counsel_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Legal Counsel", "cyan"))
for original_legal_counsel_value in original_legal_counsel_values:
    print(f"✅ {original_legal_counsel_value} → Legal Counsel")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Legal Counsel:", 'red'))
print(grouped_legal_counsel_values)

# Print summary
matched_count_legal_counsel = mask_legal_counsel_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Legal Counsel: "
        f"{matched_count_legal_counsel}",
        'red'))