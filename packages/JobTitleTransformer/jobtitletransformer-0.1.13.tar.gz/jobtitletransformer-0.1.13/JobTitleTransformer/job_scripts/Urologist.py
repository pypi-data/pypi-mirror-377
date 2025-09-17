import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Urologist related titles

urologist_variants = [
    # Standard Titles & Variants
    r"(?i)\bUrologist\b",  # General term for Urologist
    r"(?i)\bUrology Specialist\b",  # Alternative term for urologist
    r"(?i)\bUrinary Tract Specialist\b",  # Specific to urinary tract care
    r"(?i)\bKidney Specialist\b",  # Common term for urologist specializing in kidneys
    r"(?i)\bBladder Specialist\b",  # Specialist focused on bladder
    r"(?i)\bMale Reproductive Health Specialist\b",  # Urologists focusing on male reproductive health

    # Misspellings & Typographical Errors
    r"(?i)\bUrolgist\b",  # Common misspelling
    r"(?i)\bUrolgist\b",  # Typo with missing 'o'
    r"(?i)\bUroligist\b",  # Typo with extra 'i'
    r"(?i)\bUrolgists\b",  # Plural form with typo
    r"(?i)\bUroloist\b",  # Typo swapping 'g' and 'i'

    # Case Variations
    r"(?i)\bUROLOGIST\b",  # Uppercase variant
    r"(?i)\burologist\b",  # Lowercase variant
    r"(?i)\bUroLoGiSt\b",  # Mixed case variant

    # Spanish Variants
    r"(?i)\bUrólogo\b",  # General term for Urologist in Spanish
    r"(?i)\bEspecialista en Urología\b",  # Urology Specialist in Spanish
    r"(?i)\bEspecialista en Tracto Urinario\b",  # Urinary Tract Specialist in Spanish
    r"(?i)\bEspecialista en Riñón\b",  # Kidney Specialist in Spanish
    r"(?i)\bEspecialista en Vejiga\b",  # Bladder Specialist in Spanish
    r"(?i)\bEspecialista en Salud Reproductiva Masculina\b",  # Male Reproductive Health Specialist in Spanish

    # Hybrid Spanish-English Variants
    r"(?i)\bUrologist Especialista en Urología\b",  # Hybrid term
    r"(?i)\bUrólogo Kidney Specialist\b",  # Hybrid term

    # Other Possible Variations (Doctor Forms, Specialist Forms)
    r"(?i)\bUrinary Care Physician\b",  # Medical variant for urologist
    r"(?i)\bReproductive Health Doctor\b",  # Specialist for reproductive health
    r"(?i)\bBladder Surgeon\b",  # Surgeons focusing on bladder treatment
    r"(?i)\bKidney Care Doctor\b",  # Variant focused on kidney care
    r"(?i)\bConsultant Urological Surgeon\b",
    r"(?i)\bUrology\b",
]

# Exact matches that should be updated
urologist_exact_matches = {
    "Urologist",
    "Urology Specialist",
    "Urinary Tract Specialist",
    "Kidney Specialist",
    "Bladder Specialist",
    "Male Reproductive Health Specialist",
    "Urolgist",
    "Uroligist",
    "Urolgists",
    "Uroloist",
    "UROLOGIST",
    "urologist",
    "UroLoGiSt",
    "Urólogo",
    "Especialista en Urología",
    "Especialista en Tracto Urinario",
    "Especialista en Riñón",
    "Especialista en Vejiga",
    "Especialista en Salud Reproductiva Masculina",
    "Urologist Especialista en Urología",
    "Urólogo Kidney Specialist",
    "Urinary Care Physician",
    "Reproductive Health Doctor",
    "Bladder Surgeon",
    "Kidney Care Doctor",
}

# # Define patterns (these should NOT be changed)
# urologist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

urologist_exclusions = {
    'Resident', 'resident', 'student', 'Trainee', 'Resident Doctor', 'Resident ooPhysician',
    'Intern', 'intern', 'Medical Intern', 'Fellow', 'fellow', 'Clinical Fellow', 'Medical Student',
    'Clinical Trainee', 'Trainee Doctor', 'Trainee Physician', 'Junior Doctor', 'Postgraduate Trainee',
    'Aesthetic Fellow', 'Aesthetic Trainee', 'Aesthetic Medicine Fellow', 'Aesthetic Resident'
}

# Create a mask for Urologist
mask_urologist = df['speciality'].str.contains('|'.join(urologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(urologist_exact_matches)

# mask_urologist_exclusions = df['speciality'].str.contains(urologist_exclusions, case=False, na=False, regex=True)
mask_urologist_exclusions = df['speciality'].isin(urologist_exclusions)

# Final mask: Select Urologist
mask_urologist_final = mask_urologist & ~mask_urologist_exclusions

# Store the original values that will be replaced
original_urologist_values = df.loc[mask_urologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_urologist_final, 'speciality'] = 'Urologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Urologist", 'green'))
print(df.loc[mask_urologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_urologist_values = df.loc[mask_urologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Urologist", "cyan"))
for original_urologist_value in original_urologist_values:
    print(f"✅ {original_urologist_value} → Urologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Urologist:", 'red'))
print(grouped_urologist_values)

# Print summary
matched_count_urologist = mask_urologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Urologist: "
        f"{matched_count_urologist}",
        'red'))