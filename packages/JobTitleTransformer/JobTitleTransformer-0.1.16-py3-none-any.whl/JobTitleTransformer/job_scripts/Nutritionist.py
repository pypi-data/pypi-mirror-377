import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Nutritionist related titles

nutritionist_variants = [
    # Standard Titles & Abbreviations
    r"(?i)\bNutritionist\b",
    r"(?i)\bRegistered\s?Dietitian\b",
    r"(?i)\bDietitian\b",
    r"(?i)\bClinical\s?Nutritionist\b",
    r"(?i)\bCertified\s?Nutritionist\b",
    r"(?i)\bSports\s?Nutritionist\b",
    r"(?i)\bFunctional\s?Nutritionist\b",
    r"(?i)\bHolistic\s?Nutritionist\b",
    r"(?i)\bNutritional\s?Therapist\b",
    r"(?i)\bDietary\s?Consultant\b",
    r"(?i)Nutrition",
    r"(?i)\bMedica Nutrologa\b",
    r"(?i)Nutrologa",
    r"(?i)\bNutraceutical Professional\b",
    r"(?i)\bLic  Nutricion Y Estetica\b",
    r"(?i)\bDietician Acne & Skinhealth\b",
    r"(?i)\bNutrologo\b",

    # Misspellings & Typographical Errors
    r"(?i)\bNutricionist\b",
    r"(?i)\bNutrisionist\b",
    r"(?i)\bNutritonist\b",
    r"(?i)\bNutritianist\b",
    r"(?i)\bNutricianist\b",
    r"(?i)\bNutrishionist\b",
    r"(?i)\bNutricionista\b",
    r"(?i)\bNutritionest\b",
    r"(?i)\bNutriconist\b",

    # Case Variations
    r"(?i)\bnutritionist\b",
    r"(?i)\bNutritionist\b",
    r"(?i)\bNUTRITIONIST\b",
    r"(?i)\bNutritionIST\b",

    # Spanish Variants
    r"(?i)\bNutricionista\b",
    r"(?i)\bEspecialista\s?en\s?Nutrición\b",
    r"(?i)\bDietista\b",
    r"(?i)\bExperto\s?en\s?Nutrición\b",
    r"(?i)\bConsultor\s?de\s?Nutrición\b",

    # Other Possible Variations (Including Doctor/Specialist Forms)
    r"(?i)\bDoctor\s?of\s?Nutrition\b",
    r"(?i)\bPhD\s?in\s?Nutrition\b",
    r"(?i)\bFood\s?Scientist\b",
    r"(?i)\bHealth\s?Coach\b",
    r"(?i)\bIntegrative\s?Nutritionist\b",
    r"(?i)\bNutritional\s?Health\s?Consultant\b",
    r"(?i)\bSupplements\b",
    r"(?i)\bDieticionist\b",
]

# Exact matches that should be updated
nutritionist_exact_matches = {
    "Nutritionist",
    "Registered Dietitian",
    "Dietitian",
    "Clinical Nutritionist",
    "Certified Nutritionist",
    "Sports Nutritionist",
    "Functional Nutritionist",
    "Holistic Nutritionist",
    "Nutritional Therapist",
    "Dietary Consultant",
    "Nutricionist",
    "Nutrisionist",
    "Nutritonist",
    "Nutritianist",
    "Nutricianist",
    "Nutrishionist",
    "Nutricionista",
    "Nutritionest",
    "Nutriconist",
    "Especialista en Nutrición",
    "Dietista",
    "Experto en Nutrición",
    "Consultor de Nutrición",
    "Doctor of Nutrition",
    "PhD in Nutrition",
    "Food Scientist",
    "Health Coach",
    "Integrative Nutritionist",
    "Nutritional Health Consultant",
}

# # Define patterns (these should NOT be changed)
# nutritionist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

nutritionist_exclusions = {
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

# Create a mask for Nutritionist
mask_nutritionist = df['speciality'].str.contains('|'.join(nutritionist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(nutritionist_exact_matches)

# mask_nutritionist_exclusions = df['speciality'].str.contains(nutritionist_exclusions, case=False, na=False, regex=True)
mask_nutritionist_exclusions = df['speciality'].isin(nutritionist_exclusions)

# Final mask: Select Nutritionist
mask_nutritionist_final = mask_nutritionist & ~mask_nutritionist_exclusions

# Store the original values that will be replaced
original_nutritionist_values = df.loc[mask_nutritionist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_nutritionist_final, 'speciality'] = 'Nutritionist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Nutritionist", 'green'))
print(df.loc[mask_nutritionist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_nutritionist_values = df.loc[mask_nutritionist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Nutritionist", "cyan"))
for original_nutritionist_value in original_nutritionist_values:
    print(f"✅ {original_nutritionist_value} → Nutritionist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Nutritionist:", 'red'))
print(grouped_nutritionist_values)

# Print summary
matched_count_nutritionist = mask_nutritionist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Nutritionist: "
        f"{matched_count_nutritionist}",
        'red'))