import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Influencer related titles

influencer_variants = [
    r"(?i)\bInfluencer\b",  # Standard title

    # Common misspellings and case errors
    r"(?i)\bInfluancer\b",
    r"(?i)\bInflluencer\b",
    r"(?i)\bInfluenser\b",
    r"(?i)\bInfluncer\b",
    r"(?i)\bInfulencer\b",

    # Spanish variants
    r"(?i)\bInfluenciador\b",
    r"(?i)\bInfluenciadora\b",
    r"(?i)\bCreador\s?de\s?Contenido\b",
    r"(?i)\bCreadora\s?de\s?Contenido\b",
    r"(?i)\bFigura\s?Pública\b",
    r"(?i)\bLíder\s?de\s?Opinión\b",

    # Other possible variations
    r"(?i)\bContent\s?Creator\b",
    r"(?i)\bSocial\s?Media\s?Influencer\b",
    r"(?i)\bDigital\s?Influencer\b",
    r"(?i)\bBrand\s?Ambassador\b",
    r"(?i)\bOnline\s?Personality\b",
    r"(?i)\bKOL\b",
    r"(?i)\bThought\s?Leader\b",
    r"(?i)\bBlogger\b",
    r"(?i)\bOnline\b",
    r"(?i)\bOnline Work\b",
    r"(?i)\bTiktok Earning\b",
]

# Exact matches that should be updated
influencer_exact_matches = {
    "Influencer",
    "Influancer",
    "Inflluencer",
    "Influenser",
    "Influncer",
    "Infulencer",
    # Spanish variants
    "Influenciador",
    "Influenciadora",
    "Creador de Contenido",
    "Creadora de Contenido",
    "Figura Pública",
    "Líder de Opinión",
    # Other possible variations
    "Content Creator",
    "Social Media Influencer",
    "Digital Influencer",
    "Brand Ambassador",
    "Online Personality",
    "KOL",
    "Thought Leader",
    'Public Figure Aesthetic Sexologist',
    'Human Right ActivismHumanitarian Actor',
}

# Define patterns (these should NOT be changed)
influencer_exclusions = {
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
    'Thought Leader Liaison Strategic Marketing Immunology Dermatology',
}

# Create a mask for Influencer
mask_influencer = df['speciality'].str.contains('|'.join(influencer_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(influencer_exact_matches)
mask_influencer_exclusions = df['speciality'].isin(influencer_exclusions)

# Final mask: Select Influencer
mask_influencer_final = mask_influencer & ~mask_influencer_exclusions

# Store the original values that will be replaced
original_influencer_values = df.loc[mask_influencer_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_influencer_final, 'speciality'] = 'Influencer'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Influencer", 'green'))
print(df.loc[mask_influencer_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_influencer_values = df.loc[mask_influencer_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Influencer", "cyan"))
for original_influencer_value in original_influencer_values:
    print(f"✅ {original_influencer_value} → Influencer")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Influencer:", 'red'))
print(grouped_influencer_values)

# Print summary
matched_count_influencer = mask_influencer_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Influencer: "
        f"{matched_count_influencer}",
        'red'))