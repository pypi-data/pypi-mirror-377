import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Orthodontist related titles

orthodontist_variants = [
    # Standard Titles & Abbreviations
    r"(?i)\bOrthodontist\b",
    r"(?i)\bOrtho\b",
    r"(?i)\bOrthodontic\s?Specialist\b",
    r"(?i)\bDoctor\s?of\s?Orthodontics\b",
    r"(?i)\bDDS\s?Orthodontics\b",
    r"(?i)\bDMD\s?Orthodontics\b",

    # Misspellings & Typographical Errors
    r"(?i)\bOrthodentist\b",
    r"(?i)\bOrthodonist\b",
    r"(?i)\bOrthodantist\b",
    r"(?i)\bOrhtodontist\b",
    r"(?i)\bOrthodentics\b",
    r"(?i)\bOrthodentis\b",
    r"(?i)\bOrthodontics\s?Doctor\b",

    # Case Variations
    r"(?i)\borthodontist\b",
    r"(?i)\bOrthodontIst\b",
    r"(?i)\bORTHODONTIST\b",
    r"(?i)\bOrThOdOnTiSt\b",

    # Spanish Variants
    r"(?i)\bOrtodoncista\b",
    r"(?i)\bDoctor\s?en\s?Ortodoncía\b",
    r"(?i)\bEspecialista\s?en\s?Ortodoncía\b",
    r"(?i)\bCirujano\s?Ortodoncista\b",

    # Other Possible Variations (Including Doctor forms, Specialist forms)
    r"(?i)\bOrthodontic\s?Doctor\b",
    r"(?i)\bOrthodontic\s?Surgeon\b",
    r"(?i)\bOrthodontic\s?Practitioner\b",
    r"(?i)\bSpecialist\s?in\s?Orthodontics\b",
    r"(?i)\bOrthodontics\s?Expert\b",
]

# Exact matches that should be updated
orthodontist_exact_matches = {
    "Orthodontist",
    "Ortho",
    "Orthodontic Specialist",
    "Doctor of Orthodontics",
    "DDS Orthodontics",
    "DMD Orthodontics",
    "Orthodentist",
    "Orthodonist",
    "Orthodantist",
    "Orhtodontist",
    "Orthodentics",
    "Orthodentis",
    "Orthodontics Doctor",
    "Ortodoncista",
    "Doctor en Ortodoncia",
    "Especialista en Ortodoncia",
    "Cirujano Ortodoncista",
    "Orthodontic Doctor",
    "Orthodontic Surgeon",
    "Orthodontic Practitioner",
    "Specialist in Orthodontics",
    "Orthodontics Expert",
    'Other Dentistry Specialty',
}

# # Define patterns (these should NOT be changed)
# orthodontist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

orthodontist_exclusions = {
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

# Create a mask for Orthodontist
mask_orthodontist = df['speciality'].str.contains('|'.join(orthodontist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(orthodontist_exact_matches)

# mask_orthodontist_exclusions = df['speciality'].str.contains(orthodontist_exclusions, case=False, na=False, regex=True)
mask_orthodontist_exclusions = df['speciality'].isin(orthodontist_exclusions)

# Final mask: Select Orthodontist
mask_orthodontist_final = mask_orthodontist & ~mask_orthodontist_exclusions

# Store the original values that will be replaced
original_orthodontist_values = df.loc[mask_orthodontist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_orthodontist_final, 'speciality'] = 'Orthodontist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Orthodontist", 'green'))
print(df.loc[mask_orthodontist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_orthodontist_values = df.loc[mask_orthodontist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Orthodontist", "cyan"))
for original_orthodontist_value in original_orthodontist_values:
    print(f"✅ {original_orthodontist_value} → Orthodontist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Orthodontist:", 'red'))
print(grouped_orthodontist_values)

# Print summary
matched_count_orthodontist = mask_orthodontist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Orthodontist: "
        f"{matched_count_orthodontist}",
        'red'))