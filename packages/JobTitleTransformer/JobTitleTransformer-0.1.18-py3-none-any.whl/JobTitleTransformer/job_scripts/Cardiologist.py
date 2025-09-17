import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Cardiologist related titles

cardiologist_variants = [
    r"(?i)\bCardiologist\b",
    r"(?i)\bHeart\s?Specialist\b",
    r"(?i)\bCardiovascular\s?Physician\b",
    r"(?i)\bHeart\s?Doctor\b",
    r"(?i)\bCardiology\s?Specialist\b",
    r"(?i)\bCardiology\s?Physician\b",
    r"(?i)\bDoctor\s?of\s?Cardiology\b",
    r"(?i)\bCardiologist\s?Expert\b",
    r"(?i)\bCardiology\s?Expert\b",
    r"(?i)\bCardiolog\s?Expert\b",
    r"(?i)\bCardiologia Y Estetica\b",
    r"(?i)\bHead Preventive Cardiology\b",
]

# Exact matches that should be updated
cardiologist_exact_matches = {
    'Cardiologist',
    'Heart Specialist',
    'Cardiovascular Physician',
    'Heart Doctor',
    'Cardiology Specialist',
    'Cardiology Physician',
    'Doctor of Cardiology',
    'Cardiologist Expert',
    'Cardiology Expert',

    # Case-related errors
    'cardiologist',
    'heart specialist',
    'cardiovascular physician',
    'heart doctor',
    'cardiology specialist',
    'cardiology physician',
    'doctor of cardiology',
    'cardiologist expert',
    'CARDIOLOGIST',
    'HEART SPECIALIST',
    'CARDIOVASCULAR PHYSICIAN',
    'HEART DOCTOR',
    'CARDIOLOGY SPECIALIST',
    'CARDIOLOGY PHYSICIAN',
    'DOCTOR OF CARDIOLOGY',
    'CARDIOLOGIST EXPERT',

    # Common misspellings
    'Cardioligist',
    'Cardioligist Physician',
    'Cardiologyst',
    'Cardilogist',
    'Cardiologistc',
    'Cardioligyst',
    'Cardiolgist',
    'Cadiologist',
    'Cadiologyst',
    'Cardiologiest',
    'Cardiolgist',

    # Spanish-related exclusions
    'Cardiólogo',
    'Médico Cardiólogo',
    'Especialista en Cardiología',
    'Cardiólogo especialista',
    'Médico de Corazón',
    'Médico Cardiovascular',
    'Especialista en Cardiología Médica',
    'Médico Cardiólogo Experto',
    'Especialista en Enfermedades Cardíacas',
    'Cardiology',
    'CVR',
}

# Define patterns for  & Resident & Professor (these should NOT be changed)
cardiologist_exclusions = {
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
    'Aesthetic Resident',
    'Cardiology Physician Assistant',
 }

# Create a mask for Cardiologist
mask_cardiologist = df['speciality'].str.contains('|'.join(cardiologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(cardiologist_exact_matches)
mask_cardiologist_exclusions = df['speciality'].isin(cardiologist_exclusions)

# Final mask: Select Cardiologist
mask_cardiologist_final = mask_cardiologist & ~mask_cardiologist_exclusions

# Store the original values that will be replaced
original_cardiologist_values = df.loc[mask_cardiologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_cardiologist_final, 'speciality'] = 'Cardiologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Cardiologist", 'green'))
print(df.loc[mask_cardiologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_cardiologist_values = df.loc[mask_cardiologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Cardiologist", "cyan"))
for original_cardiologist_value in original_cardiologist_values:
    print(f"✅ {original_cardiologist_value} → Cardiologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Cardiologist:", 'red'))
print(grouped_cardiologist_values)

# Print summary
matched_count_cardiologist = mask_cardiologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Cardiologist: "
        f"{matched_count_cardiologist}",
        'red'))