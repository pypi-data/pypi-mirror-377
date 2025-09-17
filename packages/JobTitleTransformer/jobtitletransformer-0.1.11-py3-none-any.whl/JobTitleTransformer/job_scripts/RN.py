import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Registered Nurse (RN) related titles

RN_variants = [
    # Standard Titles & Variants
    r"(?i)\bRegistered Nurse\b",
    r"(?i)\bRegistered Nurse (RN)\b",
    r"(?i)\bRN\b",
    r"(?i)\bNurse (Registered)\b",
    r"(?i)\bRegistered Nurse Practitioner\b",
    r"(?i)\bRegistered Professional Nurse\b",
    r"(?i)\bNursing Specialist\b",
    r"(?i)\bRegistered Nurse RN\b",
    r"(?i)\bR N\b",
    r"(?i)\bRm\b",
    r"(?i)\bRegister Nurse\b",
    r"(?i)\bRegistered Cosmetic Nurse\b",
    r"(?i)\bRegistered Nursing\b",
    r"(?i)\bRegistered Staff Nurse\b",
    r"(?i)\bInjection\b",
    r"(?i)\bChargenurse\b",
    r"(?i)\bAdvanced Practice Registered Nurse\b",
    r"(?i)\bInfirmiere Auxiliaire\b",
    r"(?i)\bRegisterednurse\b",
    r"(?i)\bPrescribing Nurse\b",
    r"(?i)\bRegistered General Nurse\b",
    r"(?i)\bOperatsionnaia Medsestra\b",
    r"(?i)\bInfirmiere\b",
    r"(?i)\bMidwife\b",
    r"(?i)\bEnfermeira\b",
    r"(?i)\bEnfermagem Estetica\b",
    r"(?i)\bEmergencyroomnurse\b",
    r"(?i)\bRnPmhnp\b",

    # Misspellings & Typographical Errors
    r"(?i)\bRegistred Nurse\b",
    r"(?i)\bRegisted Nurse\b",
    r"(?i)\bRegitered Nurse\b",
    r"(?i)\bResgistered Nurse\b",
    r"(?i)\bRegistred Nurce\b",
    r"(?i)\bRergistered Nurse\b",
    r"(?i)\bRegistered Nure\b",
    r"(?i)\bRegistered Nuerse\b",

    # Case Variations
    r"(?i)\bREGISTERED NURSE\b",
    r"(?i)\bREGISTERED NURSE (RN)\b",
    r"(?i)\bregistered nurse\b",
    r"(?i)\bREGISTERED nurse\b",

    # Spanish Variants
    r"(?i)\bEnfermera Registrada\b",
    r"(?i)\bEnfermera Profesional Registrada\b",
    r"(?i)\bEnfermera (RN)\b",
    r"(?i)\bEnfermera Especialista\b",
    r"(?i)\bEnfermera Registrada (RN)\b",
    r"(?i)\bEnfermera de Cuidados Críticos\b",

    # Hybrid Spanish-English Variants
    r"(?i)\bRegistered Enfermera\b",
    r"(?i)\bNurse Registrada (RN)\b",

    # Other Possible Variations (Doctor Forms, Specialist Forms)
    r"(?i)\bNurse Practitioner (Registered)\b",
    r"(?i)\bNurse Consultant\b",
    r"(?i)\bCertified Registered Nurse (CRN)\b",
    r"(?i)\bRegistered Nursing Assistant\b",
    r"(?i)\bNurse Educator\b",
    r"(?i)\bNursing Supervisor\b",
    r"(?i)\bCommunity Nurse\b",
    r"(?i)\bCritical Care Nurse (RN)\b",
    r"(?i)\bEmergency Nurse (RN)\b",
    r"(?i)\bCosmetic NurseRegistered Nurse\b",
]

# Exact matches that should be updated
RN_exact_matches = {
    "Registered Nurse",
    "Registered Nurse (RN)",
    "RN",
    "Nurse (Registered)",
    "Registered Nurse Practitioner",
    "Registered Professional Nurse",
    "Nursing Specialist",
    "Registred Nurse",
    "Registed Nurse",
    "Regitered Nurse",
    "Resgistered Nurse",
    "Registred Nurce",
    "Rergistered Nurse",
    "Registered Nure",
    "Registered Nuerse",
    "Enfermera Registrada",
    "Enfermera Profesional Registrada",
    "Enfermera (RN)",
    "Enfermera Especialista",
    "Enfermera Registrada (RN)",
    "Enfermera de Cuidados Críticos",
    "Registered Enfermera",
    "Nurse Registrada (RN)",
    "Nurse Practitioner (Registered)",
    "Nurse Consultant",
    "Certified Registered Nurse (CRN)",
    "Registered Nursing Assistant",
    "Nurse Educator",
    "Nursing Supervisor",
    "Community Nurse",
    "Critical Care Nurse (RN)",
    "Emergency Nurse (RN)",
    "Aesthetic Nurse",
    "Registered Nurse RN",
    'Registered NurseClinical Director',
    'Rgn',
    'Aesthetic RNOwner',
    'Advanced Practice Aesthetic RN',
    'Certified Aesthetic Nurse Specialist Independent Contractor',
    'Emt',
    'Aesthetic Nurse & Clinic CEO',
    'Aesthetic nurse',
    'Enfermera',
}

# # Define patterns (these should NOT be changed)
RN_exclusions = r'\b(?:ARNP)|(?:Arpn)|(?:Advanced)|(?:Licensed)\b'

# RN_exclusions = {
#     'Resident', 'resident', 'student', 'Trainee', 'Resident Doctor', 'Resident ooPhysician',
#     'Intern', 'intern', 'Medical Intern', 'Fellow', 'fellow', 'Clinical Fellow', 'Medical Student',
#     'Clinical Trainee', 'Trainee Doctor', 'Trainee Physician', 'Junior Doctor', 'Postgraduate Trainee',
#     'Aesthetic Fellow', 'Aesthetic Trainee', 'Aesthetic Medicine Fellow', 'Aesthetic Resident'
# }

# Create a mask for Registered Nurse (RN)
mask_RN = df['speciality'].str.contains('|'.join(RN_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(RN_exact_matches)

mask_RN_exclusions = df['speciality'].str.contains(RN_exclusions, case=False, na=False, regex=True)
# mask_RN_exclusions = df['speciality'].isin(RN_exclusions)

# Final mask: Select Registered Nurse (RN)
mask_RN_final = mask_RN & ~mask_RN_exclusions

# Store the original values that will be replaced
original_RN_values = df.loc[mask_RN_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_RN_final, 'speciality'] = 'Registered Nurse (RN)'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Registered Nurse (RN)", 'green'))
print(df.loc[mask_RN_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_RN_values = df.loc[mask_RN_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Registered Nurse (RN)", "cyan"))
for original_RN_value in original_RN_values:
    print(f"✅ {original_RN_value} → Registered Nurse (RN)")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Registered Nurse (RN):", 'red'))
print(grouped_RN_values)

# Print summary
matched_count_RN = mask_RN_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Registered Nurse (RN): "
        f"{matched_count_RN}",
        'red'))