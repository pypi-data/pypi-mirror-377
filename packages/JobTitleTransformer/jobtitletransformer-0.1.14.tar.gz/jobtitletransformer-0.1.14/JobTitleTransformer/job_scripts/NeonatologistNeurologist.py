import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Neonatologist related titles

neonatologist_variants = [
   # Standard Titles & Abbreviations
    r"(?i)\bNeonatologist\b",
    r"(?i)\bNeonatal\s?Doctor\b",
    r"(?i)\bNeonatal\s?Specialist\b",
    r"(?i)\bNeonatology\s?Doctor\b",
    r"(?i)\bNeonatology\s?Specialist\b",
    r"(?i)\bConsultant\s?Neonatologist\b",
    r"(?i)\bSenior\s?Neonatologist\b",
    r"(?i)\bNeonatal\s?Physician\b",
    r"(?i)\bNeonatologist\s?Specialist\b",
    r"(?i)\bNeonatology\b",

    # Misspellings & Typographical Errors
    r"(?i)\bNeonotologist\b",
    r"(?i)\bNeonatoligist\b",
    r"(?i)\bNeonatoligist\b",
    r"(?i)\bNeonatoligist\b",
    r"(?i)\bNeonatogist\b",
    r"(?i)\bNeonoligist\b",
    r"(?i)\bNeonatoligist\b",
    r"(?i)\bNeonotoligist\b",
    r"(?i)\bNenoatologist\b",
    r"(?i)\bNeonologist\b",
    r"(?i)\bNeonlogist\b",
    r"(?i)\bNeonologist\b",

    # Case Variations
    r"(?i)\bneonatologist\b",
    r"(?i)\bNeonatologist\b",
    r"(?i)\bNEONATOLOGIST\b",
    r"(?i)\bNeonaToLogist\b",
    r"(?i)\bNeonAtologist\b",

    # Spanish Variants
    r"(?i)\bNeonatólogo\b",
    r"(?i)\bMédico\s?Neonatólogo\b",
    r"(?i)\bEspecialista\s?en\s?Neonatología\b",
    r"(?i)\bDoctor\s?en\s?Neonatología\b",
    r"(?i)\bConsultor\s?Neonatólogo\b",
    r"(?i)\bNeonatología\b",

    # Other Possible Variations (Including Doctor/Specialist Titles)
    r"(?i)\bNeonatal\s?Physician\b",
    r"(?i)\bNeonatal\s?Expert\b",
    r"(?i)\bPediatric\s?Neonatologist\b",
    r"(?i)\bNewborn\s?Specialist\b",
    r"(?i)\bPremature\s?Care\s?Specialist\b",
    r"(?i)\bNeonatal\s?Intensive\s?Care\s?Doctor\b",
    r"(?i)\bNeonatology\s?Expert\b",
]

# Exact matches that should be updated
neonatologist_exact_matches = {
    "Neonatologist",
    "Neonatal Doctor",
    "Neonatal Specialist",
    "Neonatology Doctor",
    "Neonatology Specialist",
    "Consultant Neonatologist",
    "Senior Neonatologist",
    "Neonatal Physician",
    "Neonatologist Specialist",
    "Neonatology",
    "Neonotologist",
    "Neonatoligist",
    "Neonatoligist",
    "Neonatogist",
    "Neonoligist",
    "Neonotoligist",
    "Nenoatologist",
    "Neonologist",
    "Neonlogist",
    "Neonatólogo",
    "Médico Neonatólogo",
    "Especialista en Neonatología",
    "Doctor en Neonatología",
    "Consultor Neonatólogo",
    "Neonatología",
    "Neonatal Physician",
    "Neonatal Expert",
    "Pediatric Neonatologist",
    "Newborn Specialist",
    "Premature Care Specialist",
    "Neonatal Intensive Care Doctor",
    "Neonatology Expert",
}

# # Define patterns (these should NOT be changed)
# neonatologist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

neonatologist_exclusions = {
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

# Create a mask for Neonatologist
mask_neonatologist = df['speciality'].str.contains('|'.join(neonatologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(neonatologist_exact_matches)

# mask_neonatologist_exclusions = df['speciality'].str.contains(neonatologist_exclusions, case=False, na=False, regex=True)
mask_neonatologist_exclusions = df['speciality'].isin(neonatologist_exclusions)

# Final mask: Select Neonatologist
mask_neonatologist_final = mask_neonatologist & ~mask_neonatologist_exclusions

# Store the original values that will be replaced
original_neonatologist_values = df.loc[mask_neonatologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_neonatologist_final, 'speciality'] = 'Neonatologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Neonatologist", 'green'))
print(df.loc[mask_neonatologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_neonatologist_values = df.loc[mask_neonatologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Neonatologist", "cyan"))
for original_neonatologist_value in original_neonatologist_values:
    print(f"✅ {original_neonatologist_value} → Neonatologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Neonatologist:", 'red'))
print(grouped_neonatologist_values)

# Print summary
matched_count_neonatologist = mask_neonatologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Neonatologist: "
        f"{matched_count_neonatologist}",
        'red'))

# Define regex patterns for Neurologist related titles

neurologist_variants = [
    # Standard Titles & Abbreviations
    r"(?i)\bNeurologist\b",
    r"(?i)\bNeuro\s?Doctor\b",
    r"(?i)\bNeuro\s?Specialist\b",
    r"(?i)\bNeurology\s?Doctor\b",
    r"(?i)\bNeurology\s?Specialist\b",
    r"(?i)\bConsultant\s?Neurologist\b",
    r"(?i)\bSenior\s?Neurologist\b",
    r"(?i)\bNeurological\s?Physician\b",
    r"(?i)\bNeuroscience\b",

    # Misspellings & Typographical Errors
    r"(?i)\bNurologist\b",
    r"(?i)\bNeorologist\b",
    r"(?i)\bNeuroligist\b",
    r"(?i)\bNeurlogist\b",
    r"(?i)\bNeoroligist\b",
    r"(?i)\bNeurollogist\b",
    r"(?i)\bNeurogist\b",
    r"(?i)\bNeuorlogist\b",
    r"(?i)\bNuerologist\b",
    r"(?i)\bNeurologits\b",
    r"(?i)\bNeurlgist\b",
    r"(?i)\bNeurologst\b",
    r"(?i)\bNeroligist\b",
    r"(?i)\bNeurlolgist\b",

    # Case Variations
    r"(?i)\bneurologist\b",
    r"(?i)\bNeurologist\b",
    r"(?i)\bNEUROLOGIST\b",
    r"(?i)\bNeuroLogist\b",
    r"(?i)\bNeurolOgist\b",

    # Spanish Variants
    r"(?i)\bNeurólogo\b",
    r"(?i)\bMédico\s?Neurólogo\b",
    r"(?i)\bEspecialista\s?en\s?Neurología\b",
    r"(?i)\bDoctor\s?en\s?Neurología\b",
    r"(?i)\bConsultor\s?Neurólogo\b",
    r"(?i)\bNeurocientífico\b",

    # Other Possible Variations (Including Doctor/Specialist Titles)
    r"(?i)\bNeuroscientist\b",
    r"(?i)\bNeuro\s?Physician\b",
    r"(?i)\bNeurosurgery\s?Specialist\b",
    r"(?i)\bBrain\s?Specialist\b",
    r"(?i)\bNeuromedicine\s?Expert\b",
    r"(?i)\bNeurology\b",
]

# Exact matches that should be updated
neurologist_exact_matches = {
    "Neurologist",
    "Neuro Doctor",
    "Neuro Specialist",
    "Neurology Doctor",
    "Neurology Specialist",
    "Consultant Neurologist",
    "Senior Neurologist",
    "Neurological Physician",
    "Nurologist",
    "Neorologist",
    "Neuroligist",
    "Neurlogist",
    "Neoroligist",
    "Neurollogist",
    "Neurogist",
    "Neuorlogist",
    "Nuerologist",
    "Neurologits",
    "Neurlgist",
    "Neurologst",
    "Neroligist",
    "Neurlolgist",
    "Neurólogo",
    "Médico Neurólogo",
    "Especialista en Neurología",
    "Doctor en Neurología",
    "Consultor Neurólogo",
    "Neurocientífico",
    "Neuroscientist",
    "Neuro Physician",
    "Neurosurgery Specialist",
    "Brain Specialist",
    "Neuromedicine Expert",
    'Neurosurgeon',
    'Neuro Rehab',
}

# # Define patterns (these should NOT be changed)
# neurologist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

neurologist_exclusions = {
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
    'Physician Assistant Neurology & Pain Management',
}

# Create a mask for Neurologist
mask_neurologist = df['speciality'].str.contains('|'.join(neurologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(neurologist_exact_matches)

# mask_neurologist_exclusions = df['speciality'].str.contains(neurologist_exclusions, case=False, na=False, regex=True)
mask_neurologist_exclusions = df['speciality'].isin(neurologist_exclusions)

# Final mask: Select Neurologist
mask_neurologist_final = mask_neurologist & ~mask_neurologist_exclusions

# Store the original values that will be replaced
original_neurologist_values = df.loc[mask_neurologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_neurologist_final, 'speciality'] = 'Neurologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Neurologist", 'green'))
print(df.loc[mask_neurologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_neurologist_values = df.loc[mask_neurologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Neurologist", "cyan"))
for original_neurologist_value in original_neurologist_values:
    print(f"✅ {original_neurologist_value} → Neurologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Neurologist:", 'red'))
print(grouped_neurologist_values)

# Print summary
matched_count_neurologist = mask_neurologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Neurologist: "
        f"{matched_count_neurologist}",
        'red'))