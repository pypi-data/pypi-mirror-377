import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Company Representative related titles

company_representative_variants = [
    r"(?i)\bCompany\s?Representative\b",
    r"(?i)\bBusiness\s?Representative\b",
    r"(?i)\bCorporate\s?Representative\b",
    r"(?i)\bCompany\s?Rep\b",
    r"(?i)\bCorporate\s?Rep\b",
    r"(?i)\bBusiness\s?Rep\b",
    r"(?i)\bFirm\s?Representative\b",
    r"(?i)\bCommercial\s?Representative\b",
    r"(?i)\bOfficial\s?Representative\b",
    r"(?i)\bMedical Representative\b",
    r"(?i)\bRepresentative\b",
    r"(?i)\bHotelRestaurant Equipment\b",
    r"(?i)\bPhysician Liason\b",
    r"(?i)\bCustomer Service Rep\b",
    r"(?i)\bDmos Responsible\b",
    r"(?i)\bRep Sr Plastic Surgery Us Plastice Surgery\b",
    r"(?i)\bIncorporation Specialist\b",
    r"(?i)\bRep Plastic Surgery Us Plastic Surgery\b",
    r"(?i)\bRep Plastic Surgery Us Plastice Surgery\b",
    r"(?i)\bBrand Advocate\b",
]

# Exact matches that should be updated
company_representative_exact_matches = {
    "Company Representative",
    "Corporate Representative",
    "Business Representative",
    "Company Rep",
    "Corporate Rep",
    "Business Rep",
    "Firm Representative",
    "Commercial Representative",
    "Official Representative",

    # Common misspellings for Company Representative titles
    "Compny Representative",
    "Company Reprsentative",
    "Comapny Representative",
    "Company Reepresentative",
    "Company Represntative",
    "Coprporate Representative",
    "Busines Representative",
    "Company Represenative",

    # Case-related errors for Company Representative
    "company representative",
    "COMPANY REPRESENTATIVE",
    "Company representative",
    "corporate representative",
    "Corporate representative",
    "business representative",
    "Business representative",

    # Variants of Company Representative for different types in Spanish
    "Representante de Empresa",
    "Representante Corporativo",
    "Representante de Negocios",
    "Rep de Empresa",
    "Rep Corporativo",
    "Representante Comercial",
    "Representante Oficial",

    # Other possible variations (Including related terms)
    "Company Delegate",
    "Corporate Delegate",
    "Business Delegate",
    "Enterprise Representative",
    "Industry Representative",
    'Aesthetic Consultant Aesthetic Rep',
    'Customer Service',
    'Demonstrator',
}

# Define patterns (these should NOT be changed)
company_representative_exclusions = {
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
    'Aesthetic Resident'
}

# Create a mask for Company Representative
mask_company_representative = df['speciality'].str.contains('|'.join(company_representative_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(company_representative_exact_matches)
mask_company_representative_exclusions = df['speciality'].isin(company_representative_exclusions)

# Final mask: Select Company Representative
mask_company_representative_final = mask_company_representative & ~mask_company_representative_exclusions

# Store the original values that will be replaced
original_company_representative_values = df.loc[mask_company_representative_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_company_representative_final, 'speciality'] = 'Company Representative'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Company Representative", 'green'))
print(df.loc[mask_company_representative_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_company_representative_values = df.loc[mask_company_representative_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Company Representative", "cyan"))
for original_company_representative_value in original_company_representative_values:
    print(f"✅ {original_company_representative_value} → Company Representative")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Company Representative:", 'red'))
print(grouped_company_representative_values)

# Print summary
matched_count_company_representative = mask_company_representative_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Company Representative: "
        f"{matched_count_company_representative}",
        'red'))