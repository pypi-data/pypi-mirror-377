import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Stomatologist related titles

stomatologist_variants = [
    # Standard Titles & Variants
    r"(?i)\bStomatologist\b",  # General term for Stomatologist

    # Misspellings & Typographical Errors
    r"(?i)\bStomatoligist\b",  # Common misspelling
    r"(?i)\bStomotologist\b",  # Typo with swapped letters
    r"(?i)\bStomotoligist\b",  # Misspelling with typo and extra 'l'
    r"(?i)\bStomatoligist\b",  # Extra 'i' in misspelling
    r"(?i)\bStomatlogist\b",  # Misspelling with missing 'o'

    # Case Variations
    r"(?i)\bSTOMATOLOGIST\b",  # Uppercase variant
    r"(?i)\bstomatologist\b",  # Lowercase variant
    r"(?i)\bStOmAtOlOgIsT\b",  # Mixed case variant

    # Spanish Variants
    r"(?i)\bEstomatólogo\b",  # General term for Stomatologist in Spanish

    # Hybrid Spanish-English Variants
    r"(?i)\bStomatólogo Médico\b",  # Hybrid term

    # Other Possible Variations (Doctor Forms, Specialist Forms)
    r"(?i)\bOral Medicine & Pathology\b",
    r"(?i)Stomatologue",
    r"(?i)Stomatology",
]

# Exact matches that should be updated
stomatologist_exact_matches = {
    "Stomatologist",
    "Stomatoligist",
    "Stomotologist",
    "Stomotoligist",
    "Stomatlogist",
    "STOMATOLOGIST",
    "stomatologist",
    "StOmAtOlOgIsT",
    "Estomatólogo",
    "Stomatólogo Médico",
    # Other Possible Variations (Doctor Forms, Specialist Forms)
}

# # Define patterns (these should NOT be changed)
# stomatologist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

stomatologist_exclusions = {
    'Resident', 'resident', 'student', 'Trainee', 'Resident Doctor', 'Resident ooPhysician',
    'Intern', 'intern', 'Medical Intern', 'Fellow', 'fellow', 'Clinical Fellow', 'Medical Student',
    'Clinical Trainee', 'Trainee Doctor', 'Trainee Physician', 'Junior Doctor', 'Postgraduate Trainee',
    'Aesthetic Fellow', 'Aesthetic Trainee', 'Aesthetic Medicine Fellow', 'Aesthetic Resident'
}

# Create a mask for Stomatologist
mask_stomatologist = df['speciality'].str.contains('|'.join(stomatologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(stomatologist_exact_matches)

# mask_stomatologist_exclusions = df['speciality'].str.contains(stomatologist_exclusions, case=False, na=False, regex=True)
mask_stomatologist_exclusions = df['speciality'].isin(stomatologist_exclusions)

# Final mask: Select Stomatologist
mask_stomatologist_final = mask_stomatologist & ~mask_stomatologist_exclusions

# Store the original values that will be replaced
original_stomatologist_values = df.loc[mask_stomatologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_stomatologist_final, 'speciality'] = 'Stomatologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Stomatologist", 'green'))
print(df.loc[mask_stomatologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_stomatologist_values = df.loc[mask_stomatologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Stomatologist", "cyan"))
for original_stomatologist_value in original_stomatologist_values:
    print(f"✅ {original_stomatologist_value} → Stomatologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Stomatologist:", 'red'))
print(grouped_stomatologist_values)

# Print summary
matched_count_stomatologist = mask_stomatologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Stomatologist: "
        f"{matched_count_stomatologist}",
        'red'))