import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Vascular Surgeon related titles

vascular_variants = [
    # Standard Titles & Variants
    r"(?i)\bVascular Surgeon\b",  # General term for Vascular Surgeon
    r"(?i)\bVascular Specialist\b",  # Variant term for vascular specialists
    r"(?i)\bVein Specialist\b",  # Specialist focusing on veins
    r"(?i)\bArterial Specialist\b",  # Specialist focusing on arteries
    r"(?i)\bBlood Vessel Surgeon\b",  # Alternative term for vascular surgeon

    # Misspellings & Typographical Errors
    r"(?i)\bVascualr Surgeon\b",  # Common misspelling
    r"(?i)\bVaskular Surgeon\b",  # Typo swapping letters
    r"(?i)\bVasular Surgeon\b",  # Missing one 'c'
    r"(?i)\bVascular Surgeoon\b",  # Double 'o' mistake
    r"(?i)\bVasculer Surgeon\b",  # Common typo with 'e' instead of 'a'

    # Case Variations
    r"(?i)\bVASCULAR SURGEON\b",  # Uppercase variant
    r"(?i)\bvascular surgeon\b",  # Lowercase variant
    r"(?i)\bVaScUlAr SuRgEoN\b",  # Mixed case variant

    # Spanish Variants
    r"(?i)\bCirujano Vascular\b",  # Vascular Surgeon in Spanish
    r"(?i)\bEspecialista en Vasos Sanguíneos\b",  # Blood Vessel Specialist in Spanish
    r"(?i)\bEspecialista en Venas\b",  # Vein Specialist in Spanish
    r"(?i)\bEspecialista en Arterias\b",  # Arterial Specialist in Spanish
    r"(?i)\bCirujano de Arterias y Venas\b",  # Arteries and Veins Surgeon in Spanish

    # Hybrid Spanish-English Variants
    r"(?i)\bVascular Surgeon Cirujano Vascular\b",  # Hybrid term
    r"(?i)\bVein Specialist Cirujano de Venas\b",  # Hybrid term

    # Other Possible Variations (Doctor Forms, Specialist Forms)
    r"(?i)\bArterial Surgeon\b",  # Arterial-focused surgeon
    r"(?i)\bVein Surgeon\b",  # Vein-focused surgeon
    r"(?i)\bPeripheral Vascular Surgeon\b",  # Specialist in peripheral vascular surgery
    r"(?i)\bConsultantVascular Surgery\b",
    r"(?i)\bVasc Surgery\b",
    r"(?i)\bMd Vascular Surgery\b",
    r"(?i)\bVascular Consultant\b",
    r"(?i)\bVascular Medicine Specialist\b",
    r"(?i)\bVascular Disease Doctor\b",
    r"(?i)\bEndovascular Specialist\b",
]

# Exact matches that should be updated
vascular_exact_matches = {
    "Vascular Surgeon",
    'Vascular Doctor',
    'Vascular Consultant',
    'Vascular Disease Doctor',
    'Endovascular Specialist',
    "Vascular Specialist",
    "Vein Specialist",
    "Arterial Specialist",
    "Blood Vessel Surgeon",
    "Vascualr Surgeon",
    "Vaskular Surgeon",
    "Vasular Surgeon",
    "Vascular Surgeoon",
    "Vasculer Surgeon",
    "VASCULAR SURGEON",
    "vascular surgeon",
    "VaScUlAr SuRgEoN",
    "Cirujano Vascular",
    "Especialista en Vasos Sanguíneos",
    "Especialista en Venas",
    "Especialista en Arterias",
    "Cirujano de Arterias y Venas",
    "Vascular Surgeon Cirujano Vascular",
    "Vein Specialist Cirujano de Venas",
    "Arterial Surgeon",
    "Vein Surgeon",
    "Peripheral Vascular Surgeon",
    'Vascular Medicine Specialist',
    'Vascular Specialist Doctor',
    'Especialista en Enfermedades Vasculares',
    'Especialista Endovascular',
    'Medecin Vasculaire Et Esthetique',
}

# # Define patterns (these should NOT be changed)
# vascular_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

vascular_exclusions = {
    'Resident', 'resident', 'student', 'Trainee', 'Resident Doctor', 'Resident ooPhysician',
    'Intern', 'intern', 'Medical Intern', 'Fellow', 'fellow', 'Clinical Fellow', 'Medical Student',
    'Clinical Trainee', 'Trainee Doctor', 'Trainee Physician', 'Junior Doctor', 'Postgraduate Trainee',
    'Aesthetic Fellow', 'Aesthetic Trainee', 'Aesthetic Medicine Fellow', 'Aesthetic Resident'
}

# Create a mask for Vascular Surgeon
mask_vascular = df['speciality'].str.contains('|'.join(vascular_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(vascular_exact_matches)

# mask_vascular_exclusions = df['speciality'].str.contains(vascular_exclusions, case=False, na=False, regex=True)
mask_vascular_exclusions = df['speciality'].isin(vascular_exclusions)

# Final mask: Select Vascular Surgeon
mask_vascular_final = mask_vascular & ~mask_vascular_exclusions

# Store the original values that will be replaced
original_vascular_values = df.loc[mask_vascular_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_vascular_final, 'speciality'] = 'Vascular Surgeon'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Vascular Surgeon", 'green'))
print(df.loc[mask_vascular_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_vascular_values = df.loc[mask_vascular_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Vascular Surgeon", "cyan"))
for original_vascular_value in original_vascular_values:
    print(f"✅ {original_vascular_value} → Vascular Surgeon")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Vascular Surgeon:", 'red'))
print(grouped_vascular_values)

# Print summary
matched_count_vascular = mask_vascular_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Vascular Surgeon: "
        f"{matched_count_vascular}",
        'red'))