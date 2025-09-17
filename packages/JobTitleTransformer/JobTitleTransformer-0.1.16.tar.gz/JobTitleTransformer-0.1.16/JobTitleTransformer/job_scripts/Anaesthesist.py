import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Anaesthesist related titles
anaesthesist_variants = [
    r"(?i)\bAnaesthesist\b",
    r"(?i)\bAnaesthetist\b",
    r"(?i)\bAnesthesist\b",
    r"(?i)\bAnesthetist\b",
    r"(?i)\bAnasthesist\b",
    r"(?i)\bAnasthitist\b",
    r"(?i)\bAnaesthesiology\b",
    r"(?i)\bAnaesthesia Specialist\b",
    r"(?i)\bAnaesthesia Doctor\b",
    r"(?i)\bAnesthetic Medicine\b",
    r"(?i)Anestesiologist",
    r"(?i)Anesthesia",
    r"(?i)Anesthesiste",
    r"(?i)Anesthesiology",
    r"(?i)Anestesia",
    r"(?i)Anaesthesiologist",
    r"(?i)Aneasthetic",
    r"(?i)Anasthesie",
]

# Exact matches that should be updated
anaesthesist_exact_matches = {
    'Anaesthesist',
    'Anaesthetist',
    'Anesthesist',
    'Anesthetist',
    'Anasthesist',
    'Anasthitist',
    'Anaesthesiology',
    'Anaesthesia Specialist',
    'Anaesthesia Doctor',
    'Anaesthetist Specialist',
    'Anaesthesist Doctor',
    'Anaesthesia Expert',
    'Anesthesiology Specialist',

    # Case-related exclusions
    'anaesthesist',
    'ANAESTHESIST',
    'ANAESTHETIST',
    'anesthesist',
    'ANESTHESIST',
    'AnESTHESIst',
    'anESTHESIST',
    'anAesthesIst',
    'aNAesthesist',

    # Spanish related exclusions
    'Anestesista',
    'Médico Anestesista',
    'Especialista en Anestesia',
    'Anestesista Médico',
    'Especialista en Anestesiología',
    'Médico Anestesiólogo',
    'Especialista en Anestesista',
    'Médico Anestésico',
    'Anestesista General',
    'Anestesiólogo',
    'Anestesista de Salud',
    'Anestesia General',
    'Médico en Anestesia',
    'Especialista en Anestesia General',
    'Anaesthesia',
    'Interventional Pain',
    'Interventional Pain Physician',
    'Pain Management Physician',
    'Pain Physician & Ambulatory Surgical Center Medical Director',
}

# Define patterns for  & Resident & Professor (these should NOT be changed)
anaesthesist_exclusions = {
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
    'Professor Of Anesthesia',
    'Physician Recruiter - Anesthesiology Family & Internal Medicine Consultant',
}

# Create a mask for Anaesthesist
mask_anaesthesist = df['speciality'].str.contains('|'.join(anaesthesist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(anaesthesist_exact_matches)
mask_anaesthesist_exclusions = df['speciality'].isin(anaesthesist_exclusions)

# Final mask: Select Anaesthesist
mask_anaesthesist_final = mask_anaesthesist & ~mask_anaesthesist_exclusions

# Store the original values that will be replaced
original_anaesthesist_values = df.loc[mask_anaesthesist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_anaesthesist_final, 'speciality'] = 'Anaesthesist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Anaesthesist", 'green'))
print(df.loc[mask_anaesthesist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_anaesthesist_values = df.loc[mask_anaesthesist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Anaesthesist", "cyan"))
for original_anaesthesist_value in original_anaesthesist_values:
    print(f"✅ {original_anaesthesist_value} → Anaesthesist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Anaesthesist:", 'red'))
print(grouped_anaesthesist_values)

# Print summary
matched_count_anaesthesist = mask_anaesthesist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Anaesthesist: "
        f"{matched_count_anaesthesist}",
        'red'))