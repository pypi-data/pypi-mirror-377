import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Neurophysiologist related titles

neurophysiologist_variants = [
    # Standard Titles & Abbreviations
    r"(?i)\bNeurophysiologist\b",
    r"(?i)\bNeuro\s?Physiologist\b",
    r"(?i)\bNeuro\s?Physio\b",
    r"(?i)\bNeuro\s?Physiology\s?Specialist\b",
    r"(?i)\bNeurological\s?Physiologist\b",
    r"(?i)\bNeuro\s?Physiology\s?Doctor\b",
    r"(?i)\bConsultant\s?Neurophysiologist\b",
    r"(?i)\bSenior\s?Neurophysiologist\b",

    # Misspellings & Typographical Errors
    r"(?i)\bNeurophisiologist\b",
    r"(?i)\bNeurofysiologist\b",
    r"(?i)\bNeuropysiologist\b",
    r"(?i)\bNeurophysilogist\b",
    r"(?i)\bNeurophysiologst\b",
    r"(?i)\bNeurophysiolgist\b",
    r"(?i)\bNeurophysioloigst\b",
    r"(?i)\bNeuropsysiologist\b",
    r"(?i)\bNeurphysiologist\b",
    r"(?i)\bNeurophysiologits\b",
    r"(?i)\bNeurophysiolosgist\b",

    # Case Variations
    r"(?i)\bneurophysiologist\b",
    r"(?i)\bNeuroPhysiologist\b",
    r"(?i)\bNEUROPHYSIOLOGIST\b",
    r"(?i)\bNeurophysiOLogist\b",

    # Spanish Variants
    r"(?i)\bNeurofisiólogo\b",
    r"(?i)\bMédico\s?Neurofisiólogo\b",
    r"(?i)\bEspecialista\s?en\s?Neurofisiología\b",
    r"(?i)\bDoctor\s?en\s?Neurofisiología\b",
    r"(?i)\bConsultor\s?Neurofisiólogo\b",

    # Other Possible Variations (Including Doctor/Specialist Titles)
    r"(?i)\bNeurodiagnostic\s?Physiologist\b",
    r"(?i)\bNeuro\s?Electrophysiologist\b",
    r"(?i)\bNeuro\s?Electrophysiology\s?Doctor\b",
    r"(?i)\bNeuroscience\s?Physiologist\b",
    r"(?i)\bClinical\s?Neurophysiologist\b",
    r"(?i)\bNeurophysiology\s?Expert\b",
]

# Exact matches that should be updated
neurophysiologist_exact_matches = {
    "Neurophysiologist",
    "Neuro Physiologist",
    "Neuro Physio",
    "Neuro Physiology Specialist",
    "Neurological Physiologist",
    "Neuro Physiology Doctor",
    "Consultant Neurophysiologist",
    "Senior Neurophysiologist",
    "Neurophisiologist",
    "Neurofysiologist",
    "Neuropysiologist",
    "Neurophysilogist",
    "Neurophysiologst",
    "Neurophysiolgist",
    "Neurophysioloigst",
    "Neuropsysiologist",
    "Neurphysiologist",
    "Neurophysiologits",
    "Neurophysiolosgist",
    "Neurofisiólogo",
    "Médico Neurofisiólogo",
    "Especialista en Neurofisiología",
    "Doctor en Neurofisiología",
    "Consultor Neurofisiólogo",
    "Neurodiagnostic Physiologist",
    "Neuro Electrophysiologist",
    "Neuro Electrophysiology Doctor",
    "Neuroscience Physiologist",
    "Clinical Neurophysiologist",
    "Neurophysiology Expert",
}

# # Define patterns (these should NOT be changed)
# neurophysiologist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

neurophysiologist_exclusions = {
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

# Create a mask for Neurophysiologist
mask_neurophysiologist = df['speciality'].str.contains('|'.join(neurophysiologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(neurophysiologist_exact_matches)

# mask_neurophysiologist_exclusions = df['speciality'].str.contains(neurophysiologist_exclusions, case=False, na=False, regex=True)
mask_neurophysiologist_exclusions = df['speciality'].isin(neurophysiologist_exclusions)

# Final mask: Select Neurophysiologist
mask_neurophysiologist_final = mask_neurophysiologist & ~mask_neurophysiologist_exclusions

# Store the original values that will be replaced
original_neurophysiologist_values = df.loc[mask_neurophysiologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_neurophysiologist_final, 'speciality'] = 'Neurophysiologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Neurophysiologist", 'green'))
print(df.loc[mask_neurophysiologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_neurophysiologist_values = df.loc[mask_neurophysiologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Neurophysiologist", "cyan"))
for original_neurophysiologist_value in original_neurophysiologist_values:
    print(f"✅ {original_neurophysiologist_value} → Neurophysiologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Neurophysiologist:", 'red'))
print(grouped_neurophysiologist_values)

# Print summary
matched_count_neurophysiologist = mask_neurophysiologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Neurophysiologist: "
        f"{matched_count_neurophysiologist}",
        'red'))