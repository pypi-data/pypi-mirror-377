import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Practice Manager related titles

practice_manager_variants = [
    # Standard Titles & Variants
    r"(?i)\bPractice Manager\b",
    r"(?i)\bMedical Practice Manager\b",
    r"(?i)\bHealthcare Practice Manager\b",
    r"(?i)\bPractice Operations Manager\b",
    r"(?i)\bMedical Office Manager\b",
    r"(?i)\bPm\b",
    r"(?i)\bPractice Admin\b",
    r"(?i)\bPractice Administrator\b",
    r"(?i)\bPractice Head\b",
    r"(?i)\bPractice Growth & Profitability\b",
    r"(?i)\bPractice Development Manager\b",
    r"(?i)\bSenior Service Specialist\b",
    r"(?i)\bPractice Development\b",
    r"(?i)\bPractice Coordinator\b",

    # Misspellings & Typographical Errors
    r"(?i)\bPractise Manager\b",
    r"(?i)\bPractice Manger\b",
    r"(?i)\bPractic Manager\b",
    r"(?i)\bPractise Manger\b",
    r"(?i)\bPractioner Manager\b",
    r"(?i)\bPractice Maneger\b",

    # Case Variations
    r"(?i)\bpractice manager\b",
    r"(?i)\bPRACTICE MANAGER\b",
    r"(?i)\bPrAcTiCe MaNaGeR\b",

    # Spanish Variants
    r"(?i)\bGerente de Práctica\b",
    r"(?i)\bGerente de Oficina Médica\b",
    r"(?i)\bGerente de Consultorio Médico\b",
    r"(?i)\bAdministrador de Consultorio Médico\b",

    # Other Possible Variations
    r"(?i)\bHealthcare Administrator\b",
    r"(?i)\bMedical Office Administrator\b",
    r"(?i)\bPractice Operations Coordinator\b",
    r"(?i)\bPractice Operations Director\b",
    r"(?i)\bHealthcare Facility Manager\b",
    r"(?i)\bHealthcare Facility Manager\b",
    r"(?i)\bPratiche\b",
    r"(?i)\bOffice Manager Medical Affairs Administration\b",
    r"(?i)\bPractice Management\b",
]

# Exact matches that should be updated
practice_manager_exact_matches = {
    "Practice Manager",
    "Medical Practice Manager",
    "Healthcare Practice Manager",
    "Practice Operations Manager",
    "Medical Office Manager",
    "Practise Manager",
    "Practice Manger",
    "Practic Manager",
    "Practise Manger",
    "Practioner Manager",
    "Practice Maneger",
    "Gerente de Práctica",
    "Gerente de Oficina Médica",
    "Gerente de Consultorio Médico",
    "Administrador de Consultorio Médico",
    "Healthcare Administrator",
    "Medical Office Administrator",
    "Practice Operations Coordinator",
    "Practice Operations Director",
    "Healthcare Facility Manager",
    'Management',
    'CeoPractice Manager',
    'Aesthetics Program Manager - Physician Advocate',
    'Training Manager',
    'Clinical Training Director',
    'Practice Director',
    'Director Of Aesthetic Training',
    'Foundation Training',
    'OwnerPractice Manager',
    'Pracitce Manager',
    'Practice Makkar',
    'Prcactice Manager',
    'RNPractice Manager',
    'RN Administrator',
    'Practice admin',
    'Practice Administrator',
    'Director Training & Development',
    'Director of Training & Technical Support',
    'Director Of Physician Network Development & Practice Acquisitions',
    'Director Of Physician Practices',
    'Director Physician Practices',
    'Physician Practice Liaison',
    'Program Manager & Senior Acquisitions Physician',
    'Program Manager & Tpmg Health & Wellness Physician',
    'Program Manager Community Relations & Outreach Physician',
    'Program Manager General Surgery Residency Program',
    'Director of Aesthetics & Customer Service',
}

# # Define patterns (these should NOT be changed)
# practice_manager_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

practice_manager_exclusions = {
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

# Create a mask for Practice Manager
mask_practice_manager = df['speciality'].str.contains('|'.join(practice_manager_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(practice_manager_exact_matches)

# mask_practice_manager_exclusions = df['speciality'].str.contains(practice_manager_exclusions, case=False, na=False, regex=True)
mask_practice_manager_exclusions = df['speciality'].isin(practice_manager_exclusions)

# Final mask: Select Practice Manager
mask_practice_manager_final = mask_practice_manager & ~mask_practice_manager_exclusions

# Store the original values that will be replaced
original_practice_manager_values = df.loc[mask_practice_manager_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_practice_manager_final, 'speciality'] = 'Practice Manager'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Practice Manager", 'green'))
print(df.loc[mask_practice_manager_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_practice_manager_values = df.loc[mask_practice_manager_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Practice Manager", "cyan"))
for original_practice_manager_value in original_practice_manager_values:
    print(f"✅ {original_practice_manager_value} → Practice Manager")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Practice Manager:", 'red'))
print(grouped_practice_manager_values)

# Print summary
matched_count_practice_manager = mask_practice_manager_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Practice Manager: "
        f"{matched_count_practice_manager}",
        'red'))