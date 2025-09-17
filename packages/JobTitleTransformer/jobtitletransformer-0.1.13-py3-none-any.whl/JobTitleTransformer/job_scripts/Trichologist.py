import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Trichologist related titles

trichologist_variants = [
    # Standard Titles & Variants
    r"(?i)\bTrichologist\b",  # General term for Trichologist
    r"(?i)\bHair Specialist\b",  # Common alternative for trichologist
    r"(?i)\bHair Doctor\b",  # Informal term for trichologist
    r"(?i)\bScalp Specialist\b",  # Related to scalp care and treatment
    r"(?i)\bScalp Care Master\b",
    r"(?i)\bHair Science\b",
    r"(?i)Trichology",

    # Misspellings & Typographical Errors
    r"(?i)\bTricholgist\b",  # Common misspelling
    r"(?i)\bTricholist\b",  # Another common misspelling
    r"(?i)\bTricholigist\b",  # Another misspelling
    r"(?i)\bTrichologyst\b",  # Adding unnecessary 'y' at the end
    r"(?i)\bTrichollogist\b",  # Extra 'l' typo

    # Case Variations
    r"(?i)\bTRICHOLOGIST\b",  # Uppercase variant
    r"(?i)\btrichologist\b",  # Lowercase variant
    r"(?i)\bTrIcHoLoGiSt\b",  # Mixed case variant

    # Spanish Variants
    r"(?i)\bTricólogo\b",  # General term for trichologist in Spanish
    r"(?i)\bEspecialista en Cabello\b",  # Hair Specialist in Spanish
    r"(?i)\bEspecialista en Cuero Cabelludo\b",  # Scalp Specialist in Spanish

    # Hybrid Spanish-English Variants
    r"(?i)\bTrichologist Especialista en Cabello\b",  # Hybrid term
    r"(?i)\bTricólogo Hair Specialist\b",  # Hybrid term

    # Other Possible Variations (Doctor Forms, Specialist Forms)
    r"(?i)\bHair Care Doctor\b",  # General medical term for hair-related care
    r"(?i)\bHair and Scalp Specialist\b",  # Comprehensive term for both hair and scalp specialists
    r"(?i)\bScalp Care Physician\b",  # Doctor specializing in scalp care
]

# Exact matches that should be updated
trichologist_exact_matches = {
    "Trichologist",
    "Hair Specialist",
    "Hair Doctor",
    "Scalp Specialist",
    "Tricholgist",
    "Tricholist",
    "Tricholigist",
    "Trichologyst",
    "Trichollogist",
    "TRICHOLOGIST",
    "trichologist",
    "TrIcHoLoGiSt",
    "Tricólogo",
    "Especialista en Cabello",
    "Especialista en Cuero Cabelludo",
    "Trichologist Especialista en Cabello",
    "Tricólogo Hair Specialist",
    "Hair Care Doctor",
    "Hair and Scalp Specialist",
    "Scalp Care Physician",
    'Facial Aesthetics & Hair Loss',
    'Hair Loss',
}

# # Define patterns (these should NOT be changed)
# trichologist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

trichologist_exclusions = {
    'Resident', 'resident', 'student', 'Trainee', 'Resident Doctor', 'Resident ooPhysician',
    'Intern', 'intern', 'Medical Intern', 'Fellow', 'fellow', 'Clinical Fellow', 'Medical Student',
    'Clinical Trainee', 'Trainee Doctor', 'Trainee Physician', 'Junior Doctor', 'Postgraduate Trainee',
    'Aesthetic Fellow', 'Aesthetic Trainee', 'Aesthetic Medicine Fellow', 'Aesthetic Resident'
}

# Create a mask for Trichologist
mask_trichologist = df['speciality'].str.contains('|'.join(trichologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(trichologist_exact_matches)

# mask_trichologist_exclusions = df['speciality'].str.contains(trichologist_exclusions, case=False, na=False, regex=True)
mask_trichologist_exclusions = df['speciality'].isin(trichologist_exclusions)

# Final mask: Select Trichologist
mask_trichologist_final = mask_trichologist & ~mask_trichologist_exclusions

# Store the original values that will be replaced
original_trichologist_values = df.loc[mask_trichologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_trichologist_final, 'speciality'] = 'Trichologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Trichologist", 'green'))
print(df.loc[mask_trichologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_trichologist_values = df.loc[mask_trichologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Trichologist", "cyan"))
for original_trichologist_value in original_trichologist_values:
    print(f"✅ {original_trichologist_value} → Trichologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Trichologist:", 'red'))
print(grouped_trichologist_values)

# Print summary
matched_count_trichologist = mask_trichologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Trichologist: "
        f"{matched_count_trichologist}",
        'red'))