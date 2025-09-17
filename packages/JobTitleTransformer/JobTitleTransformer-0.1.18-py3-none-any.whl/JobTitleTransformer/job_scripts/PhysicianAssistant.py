import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Physician Assistant related titles

PA_variants = [
    # Standard Titles & Variants
    r"(?i)\bPhysician Assistant\b",
    r"(?i)\bPhysician's Assistant\b",
    r"(?i)\bPhysician Assistant Specialist\b",
    r"(?i)\bPA\b",
    r"(?i)\bPhysician's Associate\b",
    r"(?i)\bMedical Assistant\b",  # Depending on context, could refer to the same
    r"(?i)\bPhysician Assistant Professional\b",
    r"(?i)\bP A/P A -C\b",
    r"(?i)\bP AP A -C\b",
    r"(?i)\bAsistente Medico Estetico\b",
    r"(?i)\bAssistante Medecine Esthetique\b",
    r"(?i)\bAuxiliar Medicina Estetica\b",
    r"(?i)\bGeneral Koordinator\b",
    r"(?i)\bMd Assistant\b",
    r"(?i)\bAssiant\b",
    r"(?i)\bAsistent\b",
    r"(?i)\bAssistante Medicale\b",
    r"(?i)\bAsistente\b",
    r"(?i)\bAssistante\b",
    r"(?i)\bPhysician Associate\b",
    r"(?i)\bOperation Associate\b",
    r"(?i)\bPersonal Assistant To Dr\b",

    # Misspellings & Typographical Errors
    r"(?i)\bPhyscian Assistant\b",
    r"(?i)\bPhysician Assitant\b",
    r"(?i)\bPhysician Asistant\b",
    r"(?i)\bPhysican Assistant\b",

    # Case Variations
    r"(?i)\bphysician assistant\b",
    r"(?i)\bPHYSICIAN ASSISTANT\b",
    r"(?i)\bPhYsIcIaN AsSiStAnT\b",
    r"(?i)\bPhysician AssistanT\b",

    # Spanish Variants
    r"(?i)\bAsistente Médico\b",
    r"(?i)\bAsistente de Médico\b",
    r"(?i)\bAsistente de Medicina\b",
    r"(?i)\bAsociado Médico\b",
    r"(?i)\bAsistente de Médico Profesional\b",

    # Other Possible Variations
    r"(?i)\bMedical Physician Assistant\b",
    r"(?i)\bHealth Practitioner Assistant\b",
    r"(?i)\bClinical Physician Assistant\b",
    r"(?i)\bPhysician's Healthcare Assistant\b",
    r"(?i)\bCoordinator Tsfp\b",
    r"(?i)\bPlastic Surgery Medical Assistant\b",
    r"(?i)\bPlastic Surgery Pa\b",
    r"(?i)\bAssistante Medecine Esthetique\b",
    r"(?i)\bPhysician Assistant\b",
    r"(?i)\bP AP A -C\b",
    r"(?i)\bPhysician Associate\b",
    r"(?i)\bAssistant Camera Operator\b",
    r"(?i)\bPersonal Assistant\b",
    r"(?i)\bPa\b",
    r"(?i)\bAssiant\b",
    r"(?i)\bPa-C\b",
    r"(?i)\bMd Assistant\b",
    r"(?i)\bAsistent\b",
    r"(?i)\bPlastic Surgery Medical Assistant\b",
    r"(?i)\bCertified Medical Assistant\b",
    r"(?i)\bAssistante Medecine Esthetique\b",
    r"(?i)\bAssistante Medicale\b",
    r"(?i)\bDoctor Asistent\b",
    r"(?i)\bMedical Assistant\b",
    r"(?i)\bMedical Care Assistant\b",
    r"(?i)\bMedicalScientific Assistant\b",
    r"(?i)\bMpas Pa-C\b",
    r"(?i)\bExeccutive Assistant\b",
    r"(?i)\bOperation Associate\b",
    r"(?i)\bPa C\b",
    r"(?i)\bGeneral Koordinator\b",
    r"(?i)\bSurgical Assistant\b",
    r"(?i)\bPlastic Surgery Pa\b",
    r"(?i)\bAsistente Medico Estetico\b",
    r"(?i)\bRn Pa\b",
    r"(?i)\bAesthetic Pa\b",
    r"(?i)\bAesthetic Dermatology Pa\b",
    r"(?i)\bCoordinator Tsfp\b",
    r"(?i)\bImd-Pa\b",
    r"(?i)\bAssistant Planner\b",
    r"(?i)\bAsistente De Gerencia\b",
    r"(?i)\bPersonal Assistant To Dr\b",
    r"(?i)\bAssistant Bu\b",
    r"(?i)\bNpd Assistant\b",
    r"(?i)\bAssistant To The Management\b",
    r"(?i)\bPolar & Care Assistant\b",
    r"(?i)\bPhysician Assistant Injector\b",
    r"(?i)\bSpecial Assistant\b",
    r"(?i)\bResearch Assistant\b",
    r"(?i)\bAssistant Practitioner\b",
]

# Exact matches that should be updated
PA_exact_matches = {
    "Physician Assistant",
    "Physician's Assistant",
    "Physician Assistant Specialist",
    "PA",
    "Physician's Associate",
    "Medical Assistant",
    "Physician Assistant Professional",
    "Physcian Assistant",
    "Physician Assitant",
    "Physician Asistant",
    "Physican Assistant",
    "Asistente Médico",
    "Asistente de Médico",
    "Asistente de Medicina",
    "Asociado Médico",
    "Asistente de Médico Profesional",
    "Medical Physician Assistant",
    "Health Practitioner Assistant",
    "Clinical Physician Assistant",
    "Physician's Healthcare Assistant",
    "P AP A -C",
    'Assistant',
    'assistant',
    'Physician AssistantFounder',
    'Physician AssistantOwner',
    'Physicians Assitant',
    'Physician Coordinator',
    'Orthopedic Physician S Assistant',
    'DMS PAC CAC',
}

# # Define patterns (these should NOT be changed)
# PA_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

PA_exclusions = {
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

# Create a mask for Physician Assistant
mask_PA = df['speciality'].str.contains('|'.join(PA_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(PA_exact_matches)

# mask_PA_exclusions = df['speciality'].str.contains(PA_exclusions, case=False, na=False, regex=True)
mask_PA_exclusions = df['speciality'].isin(PA_exclusions)

# Final mask: Select Physician Assistant
mask_PA_final = mask_PA & ~mask_PA_exclusions

# Store the original values that will be replaced
original_PA_values = df.loc[mask_PA_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_PA_final, 'speciality'] = 'Physician Assistant'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Physician Assistant", 'green'))
print(df.loc[mask_PA_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_PA_values = df.loc[mask_PA_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Physician Assistant", "cyan"))
for original_PA_value in original_PA_values:
    print(f"✅ {original_PA_value} → Physician Assistant")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Physician Assistant:", 'red'))
print(grouped_PA_values)

# Print summary
matched_count_PA = mask_PA_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Physician Assistant: "
        f"{matched_count_PA}",
        'red'))