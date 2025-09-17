import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Owner related titles

owner_variants = [
    # Standard Titles & Variants
    r"(?i)\bOwner\b",
    r"(?i)\bBusiness\s?Owner\b",
    r"(?i)\bCompany\s?Owner\b",
    r"(?i)\bFounder\b",
    r"(?i)\bCo\s?-?\s?Owner\b",
    r"(?i)\bEntrepreneur\b",
    r"(?i)\bSole\s?Proprietor\b",
    r"(?i)\bManaging\s?Owner\b",
    r"(?i)\bPrincipal\s?Owner\b",
    r"(?i)\bOwner\s?and\s?CEO\b",
    r"(?i)\bOwner\s?and\s?Founder\b",
    r"(?i)\bOwner\s?Operator\b",
    r"(?i)\bSelf\s?-?\s?Employed\b",
    r"(?i)\bIndependent\s?Business\s?Owner\b",
    r"(?i)\bManaging Partner\b",
    r"(?i)\bProprietor\b",
    r"(?i)\bPartners\b",
    r"(?i)\bMedico Proprietario\b",
    r"(?i)Proprietario",
    r"(?i)\bOwnerGeneral Manager\b",
    r"(?i)\bEntrepreneure Independante\b",
    r"(?i)\bOwners\b",
    r"(?i)\bBusiness Woman\b",
    r"(?i)\bOwnerBarbara JS Chocolates\b",
    r"(?i)\bPropietariaEnfermera Cosmetologa\b",
    r"(?i)\bOwnerbuyer\b",
    r"(?i)\bOwnere\b",
    r"(?i)\bOwnerCrnp\b",
    r"(?i)\bInjectorOwner\b",
    r"(?i)\bDirectorOwner\b",
    r"(?i)\bOwnerPhysician Associate\b",

    # Misspellings & Typographical Errors
    r"(?i)\bOner\b",
    r"(?i)\bOnwer\b",
    r"(?i)\bOwneer\b",
    r"(?i)\bOwnr\b",
    r"(?i)\bOwwner\b",
    r"(?i)\bOwnwer\b",

    # Case Variations
    r"(?i)\bowner\b",
    r"(?i)\bOwNeR\b",
    r"(?i)\bOWNER\b",
    r"(?i)\bOwNer\b",

    # Spanish Variants
    r"(?i)\bPropietario\b",
    r"(?i)\bDueño\b",
    r"(?i)\bTitular\b",
    r"(?i)\bFundador\b",
    r"(?i)\bEmprendedor\b",
    r"(?i)\bAutónomo\b",
    r"(?i)\bGerente\s?Propietario\b",
    r"(?i)\bDueño\s?de\s?Negocio\b",
    r"(?i)\bPropietario\s?de\s?Empresa\b",

    # Other Possible Variations
    r"(?i)\bBusiness\s?Founder\b",
    r"(?i)\bBusiness\s?Partner\b",
    r"(?i)\bBusiness\s?Owner\s?Operator\b",
    r"(?i)\bCompany\s?Director\b",
    r"(?i)\bEnterprise\s?Owner\b",
    r"(?i)\bStart-up\s?Founder\b",
    r"(?i)\bAesthetic Provider\b",
    r"(?i)\bBoss\b",
]

# Exact matches that should be updated
owner_exact_matches = {
    "Owner",
    "Business Owner",
    "Company Owner",
    "Founder",
    "Co-Owner",
    "Entrepreneur",
    "Sole Proprietor",
    "Managing Owner",
    "Principal Owner",
    "Owner and CEO",
    "Owner and Founder",
    "Owner Operator",
    "Self-Employed",
    "Independent Business Owner",
    "Oner",
    "Onwer",
    "Owneer",
    "Ownr",
    "Owwner",
    "Ownwer",
    "Propietario",
    "Dueño",
    "Titular",
    "Fundador",
    "Emprendedor",
    "Autónomo",
    "Gerente Propietario",
    "Dueño de Negocio",
    "Propietario de Empresa",
    "Business Founder",
    "Business Partner",
    "Business Owner Operator",
    "Company Director",
    "Enterprise Owner",
    "Start-up Founder",
    "Partner",
    'OwnerDirector',
    'CeoOwner',
    'OwnerCeoPresidentManaging Director',
    'OwnerExecutive Consultant',
    'OwnerLead Injector',
    'OwnerManaging Director',
    'OwnerNurse Injector',
    'Ownerhospital Director',
    'OwnerFounder',
    'Senior Partner',
    'Partner Innovation&Development',
    'PartnerOwner',
    'OwnerPresidentCeo',
    'SocioPropietarioEmpresario',
    'Bisnesman',
    'Inventor',
    'PodiatristOwner',
    'MDOWNER',
    'Ownerpractitioner',
    'RNOwner',
    'RNowner',
    'Nurse PractitionerOwner',
    'ARNPOwner',
    'SOCIA PROPRIETARIA',
}

# # Define patterns (these should NOT be changed)
# owner_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

owner_exclusions = {
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
    'Physician & Owner',
    'Oral & Facial Surgeon & & Owner',
    'Physician & Founder',
    'Plastic Surgeon Owner',
    'Physician Co-Owner',
    'Owner Physician',
    'Owner & Physician',
    'Periodontist & Dental Implant Surgeon & Owner',
    'Physician & Founder Interventional Cardiology',
    'Family Practice Physician Owner',
    'Physician-Owner',
    'Owner Plastic Surgeon',
    'Physician Founder',
    'Physician Medical Director & Owner',
    'Plastic Surgeon & Owner',
    'Plastic Surgeon & Co-Founder',
    'Physician Owner',
    'Physician & Co-Founder',
}

# Create a mask for Owner
mask_owner = df['speciality'].str.contains('|'.join(owner_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(owner_exact_matches)

# mask_owner_exclusions = df['speciality'].str.contains(owner_exclusions, case=False, na=False, regex=True)
mask_owner_exclusions = df['speciality'].isin(owner_exclusions)

# Final mask: Select Owner
mask_owner_final = mask_owner & ~mask_owner_exclusions

# Store the original values that will be replaced
original_owner_values = df.loc[mask_owner_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_owner_final, 'speciality'] = 'Owner'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Owner", 'green'))
print(df.loc[mask_owner_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_owner_values = df.loc[mask_owner_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Owner", "cyan"))
for original_owner_value in original_owner_values:
    print(f"✅ {original_owner_value} → Owner")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Owner:", 'red'))
print(grouped_owner_values)

# Print summary
matched_count_owner = mask_owner_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Owner: "
        f"{matched_count_owner}",
        'red'))