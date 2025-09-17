import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Photographer related titles

photographer_variants = [
    # Standard Titles & Variants
    r"(?i)\bPhotographer\b",
    r"(?i)\bProfessional Photographer\b",
    r"(?i)\bPhotographer Specialist\b",
    r"(?i)\bPhotography Expert\b",
    r"(?i)\bPhotography Consultant\b",
    r"(?i)\bConsultant Photographer\b",
    r"(?i)\bPhotographic Artist\b",

    # Misspellings & Typographical Errors
    r"(?i)\bFotographer\b",
    r"(?i)\bPhographer\b",
    r"(?i)\bPhotogarpher\b",
    r"(?i)\bPhotographer\b",
    r"(?i)\bPhotograhper\b",

    # Case Variations
    r"(?i)\bphotographer\b",
    r"(?i)\bPHOTOGRAPHER\b",
    r"(?i)\bPhOtOgRaPhEr\b",
    r"(?i)\bPhoToGrApHeR\b",

    # Spanish Variants
    r"(?i)\bFotógrafo\b",
    r"(?i)\bFotógrafa\b",
    r"(?i)\bFotógrafo Profesional\b",
    r"(?i)\bEspecialista en Fotografía\b",
    r"(?i)\bExperto en Fotografía\b",
    r"(?i)\bConsultor de Fotografía\b",
    r"(?i)\bConsultor Fotográfico\b",
    r"(?i)\bArtista Fotográfico\b",

    # Other Possible Variations
    r"(?i)\bPhotographic Specialist\b",
    r"(?i)\bPhotographic Consultant\b",
    r"(?i)\bPhotography Artist\b",
    r"(?i)\bPhotography Professional\b",
]

# Exact matches that should be updated
photographer_exact_matches = {
    "Photographer",
    "Professional Photographer",
    "Photographer Specialist",
    "Photography Expert",
    "Photography Consultant",
    "Consultant Photographer",
    "Photographic Artist",
    "Fotographer",
    "Phographer",
    "Photogarpher",
    "Photograhper",
    "Fotógrafo",
    "Fotógrafa",
    "Fotógrafo Profesional",
    "Especialista en Fotografía",
    "Experto en Fotografía",
    "Consultor de Fotografía",
    "Consultor Fotográfico",
    "Artista Fotográfico",
    "Photographic Specialist",
    "Photographic Consultant",
    "Photography Artist",
    "Photography Professional",
}

# # Define patterns (these should NOT be changed)
# photographer_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

photographer_exclusions = {
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

# Create a mask for Photographer
mask_photographer = df['speciality'].str.contains('|'.join(photographer_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(photographer_exact_matches)

# mask_photographer_exclusions = df['speciality'].str.contains(photographer_exclusions, case=False, na=False, regex=True)
mask_photographer_exclusions = df['speciality'].isin(photographer_exclusions)

# Final mask: Select Photographer
mask_photographer_final = mask_photographer & ~mask_photographer_exclusions

# Store the original values that will be replaced
original_photographer_values = df.loc[mask_photographer_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_photographer_final, 'speciality'] = 'Photographer'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Photographer", 'green'))
print(df.loc[mask_photographer_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_photographer_values = df.loc[mask_photographer_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Photographer", "cyan"))
for original_photographer_value in original_photographer_values:
    print(f"✅ {original_photographer_value} → Photographer")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Photographer:", 'red'))
print(grouped_photographer_values)

# Print summary
matched_count_photographer = mask_photographer_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Photographer: "
        f"{matched_count_photographer}",
        'red'))