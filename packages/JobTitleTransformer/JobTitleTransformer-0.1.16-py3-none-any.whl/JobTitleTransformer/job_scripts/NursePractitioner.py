import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Nurse Practitioner (NP) related titles

NP_variants = [
    # Standard Titles & Abbreviations
    r"(?i)\bNurse\s?Practitioner\b",
    r"(?i)\bNurse\s?Practitioner\s?\(NP\)\b",
    r"(?i)\bNP\b",
    r"(?i)\bNurse Practitioner NP\b",
    r"(?i)\bN P\b",
    r"(?i)\bn p\b",
    r"(?i)\bANP\b",
    r"(?i)\bFamily\s?Nurse\s?Practitioner\b",
    r"(?i)\bFNP\b",
    r"(?i)\bAdult\s?Nurse\s?Practitioner\b",
    r"(?i)\bPediatric\s?Nurse\s?Practitioner\b",
    r"(?i)\bPsychiatric\s?Nurse\s?Practitioner\b",
    r"(?i)\bGeriatric\s?Nurse\s?Practitioner\b",
    r"(?i)\bNurse Injector\b",
    r"(?i)\bCosmetic Nurse\b",
    r"(?i)\bStaff Nurse\b",
    r"(?i)\bNurse Prescriber\b",
    r"(?i)\bNursing\b",
    r"(?i)\bAesthetic Nurse PractitionerPrescriber\b",
    r"(?i)\bAesthetic Nurse SpecialistOwnee\b",
    r"(?i)\bAesthetic PracticionerNurse\b",
    r"(?i)\bCertified Nurse Midwifery\b",
    r"(?i)\bNuse\b",
    r"(?i)\bEsthetic Nurse\b",
    r"(?i)\bSpec  Nurse\b",
    r"(?i)\bStaffnurse\b",
    r"(?i)\bIndependent Nurse Presceriber\b",
    r"(?i)\bNursingGluta Infusions\b",

    # Misspellings & Typographical Errors
    r"(?i)\bNurs\s?Practitioner\b",
    r"(?i)\bNurse\s?Practioner\b",
    r"(?i)\bNurse\s?Pracktitioner\b",
    r"(?i)\bNurse\s?Practitonner\b",
    r"(?i)\bNurse\s?Practitoner\b",
    r"(?i)\bNurse\s?Pracktitioner\s?\(NP\)\b",
    r"(?i)\bNurse\s?Prakittioner\b",
    r"(?i)\bNurse\s?Practitionar\b",
    r"(?i)\bNurce\s?Practitioner\b",
    r"(?i)\bNurse\s?Prakitoner\b",

    # Case Variations
    r"(?i)\bnurse practitioner\b",
    r"(?i)\bNurse practitioner\b",
    r"(?i)\bnurse Practitioner\b",
    r"(?i)\bNURSE PRACTITIONER\b",
    r"(?i)\bNurse PRACTITIONER\b",
    r"(?i)\bnurse PRACTITIONER\b",

    # Spanish Variants
    r"(?i)\bEnfermero\s?Practicante\b",
    r"(?i)\bEnfermera\s?Practicante\b",
    r"(?i)\bPracticante\s?de\s?Enfermería\b",
    r"(?i)\bEspecialista\s?en\s?Enfermería\b",
    r"(?i)\bEnfermero\s?de\s?Atención\s?Primaria\b",

    # Other Possible Variations (Including Doctor/Specialist Forms)
    r"(?i)\bNurse\s?Clinician\b",
    r"(?i)\bSenior\s?Nurse\s?Practitioner\b",
    r"(?i)\bBoard\s?Certified\s?Nurse\s?Practitioner\b",
    r"(?i)\bCertified\s?Nurse\s?Practitioner\b",
    r"(?i)\bOwnerNurse Practitioner\b",
]

# Exact matches that should be updated
NP_exact_matches = {
    "Nurse Practitioner",
    "Nurse Practitioner (NP)",
    "NP",
    "Family Nurse Practitioner",
    "FNP",
    "Adult Nurse Practitioner",
    "Pediatric Nurse Practitioner",
    "Psychiatric Nurse Practitioner",
    "Geriatric Nurse Practitioner",
    "Nurs Practitioner",
    "Nurse Practioner",
    "Nurse Pracktitioner",
    "Nurse Practitonner",
    "Nurse Practitoner",
    "Nurse Pracktitioner (NP)",
    "Nurse Prakittioner",
    "Nurse Practitionar",
    "Nurce Practitioner",
    "Nurse Prakitoner",
    "Enfermero Practicante",
    "Enfermera Practicante",
    "Practicante de Enfermería",
    "Especialista en Enfermería",
    "Enfermero de Atención Primaria",
    "Nurse Clinician",
    "Senior Nurse Practitioner",
    "Board Certified Nurse Practitioner",
    "Certified Nurse Practitioner",
    "Injector",
    "Aesthetic PracticionerNurse",
    'Nurse Pracitioner',
    'Nurse Practicioner',
    'Nurs Practitionar',
    'Nrs Practitioner',
    'Cosmetologist & Studing Nurse',
    'Cosmetology Nurse',
    'Specialist Nurse',
    'Nurse Antiaging',
    'Nurse PractitionerMedical Director',
    'Lic  Enfermeria',
    'Wound Care Nurse',
    'DNM',
}

# # Define patterns (these should NOT be changed)
NP_exclusions = r'\b(?:ARNP)|(?:Advanced)|(?:Registered)|(?:Rn)|(?:RN)\b'

# NP_exclusions = {
#     'Resident', 'resident', 'student', 'Trainee', 'Resident Doctor', 'Resident ooPhysician',
#     'Intern', 'intern', 'Medical Intern', 'Fellow', 'fellow', 'Clinical Fellow', 'Medical Student',
#     'Clinical Trainee', 'Trainee Doctor', 'Trainee Physician', 'Junior Doctor', 'Postgraduate Trainee',
#     'Aesthetic Fellow', 'Aesthetic Trainee', 'Aesthetic Medicine Fellow', 'Aesthetic Resident'
# }

# Create a mask for Nurse Practitioner (NP)
mask_NP = df['speciality'].str.contains('|'.join(NP_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(NP_exact_matches)

mask_NP_exclusions = df['speciality'].str.contains(NP_exclusions, case=False, na=False, regex=True)
# mask_NP_exclusions = df['speciality'].isin(NP_exclusions)

# Final mask: Select Nurse Practitioner (NP)
mask_NP_final = mask_NP & ~mask_NP_exclusions

# Store the original values that will be replaced
original_NP_values = df.loc[mask_NP_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_NP_final, 'speciality'] = 'Nurse Practitioner (NP)'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Nurse Practitioner (NP)", 'green'))
print(df.loc[mask_NP_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_NP_values = df.loc[mask_NP_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Nurse Practitioner (NP)", "cyan"))
for original_NP_value in original_NP_values:
    print(f"✅ {original_NP_value} → Nurse Practitioner (NP)")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Nurse Practitioner (NP):", 'red'))
print(grouped_NP_values)

# Print summary
matched_count_NP = mask_NP_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Nurse Practitioner (NP): "
        f"{matched_count_NP}",
        'red'))