import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Medical Spa Manager related titles

spa_variants = [
    # Standard Titles & Abbreviations
    r"(?i)\bMedical\s?Spa\s?Manager\b",
    r"(?i)\bMed\s?Spa\s?Manager\b",
    r"(?i)\bSpa\s?Medical\s?Manager\b",
    r"(?i)\bMedical\s?Aesthetic\s?Spa\s?Manager\b",
    r"(?i)\bManager\s?of\s?Medical\s?Spa\b",
    r"(?i)\bDirector\s?of\s?Medical\s?Spa\b",
    r"(?i)\bMedical\s?Wellness\s?Spa\s?Manager\b",
    r"(?i)\bSpa\s?Manager\s?\(Medical\)\b",
    r"(?i)\bSpa Manager\b",
    r"(?i)\bBeauty Salon\b",
    r"(?i)\bBeautician\b",
    r"(?i)\bSpa\b",
    r"(?i)\bClinic CoordinatorBesuty Therapist\b",
    r"(?i)\bStudio Medico Pisano\b",
    r"(?i)\bStudio Manager\b",
    r"(?i)\bProvider Owner Botox Beauty Spa Llc\b",
    r"(?i)\bMed Spa\b",
    r"(?i)\bMedSpa\b",
    r"(?i)\bMedspa\b",
    r"(?i)\bMedical Spa\b",
    r"(?i)\bMedicalSpa\b",
    r"(?i)\bMedicalspa\b",
    r"(?i)\bMedispa\b",
    r"(?i)\bHeadspa\b",
    r"(?i)\bHead spa\b",
    r"(?i)\bSpaMaster\b",
    r"(?i)\bSpa Master\b",
    r"(?i)\bMasterspa\b",
    r"(?i)\bMaster spa\b",
    r"(?i)\bMedics & Spa\b",
    r"(?i)\bMedicsSpa\b",
    r"(?i)\bMedics Spa\b",
    r"(?i)\bBesuty Therapist\b",
    r"(?i)\bBeauty Therapist\b",
    r"(?i)\bBeautyTherapist\b",

    # Misspellings & Typographical Errors
    r"(?i)\bMediacal\s?Spa\s?Manager\b",
    r"(?i)\bMedial\s?Spa\s?Manager\b",
    r"(?i)\bMedical\s?Sap\s?Manager\b",
    r"(?i)\bMedical\s?Spaa\s?Manager\b",
    r"(?i)\bMedical\s?Sspa\s?Manager\b",
    r"(?i)\bMedical\s?Spaaa\s?Manager\b",
    r"(?i)\bMedial\s?Spa\s?Manger\b",
    r"(?i)\bMedical\s?Spa\s?Manger\b",
    r"(?i)\bMedcial\s?Spa\s?Manager\b",
    r"(?i)\bMedical\s?Spa\s?Maneger\b",
    r"(?i)\bMedical\s?Spa\s?Managr\b",
    r"(?i)\bMedical\s?Spaa\s?Mngr\b",

    # Case Variations
    r"(?i)\bmedical spa manager\b",
    r"(?i)\bMedical spa manager\b",
    r"(?i)\bmedical Spa Manager\b",
    r"(?i)\bMEDICAL SPA MANAGER\b",
    r"(?i)\bMeDical Spa ManaGer\b",

    # Spanish Variants
    r"(?i)\bGerente\s?de\s?Spa\s?Médico\b",
    r"(?i)\bAdministrador\s?de\s?Spa\s?Médico\b",
    r"(?i)\bDirector\s?de\s?Spa\s?Médico\b",
    r"(?i)\bEncargado\s?de\s?Spa\s?Médico\b",
    r"(?i)\bGerente\s?de\s?Bienestar\s?Médico\b",
    r"(?i)\bCoordinador\s?de\s?Spa\s?Médico\b",

    # Other Possible Variations (Including Doctor/Specialist Titles)
    r"(?i)\bAesthetic\s?Spa\s?Manager\b",
    r"(?i)\bCosmetic\s?Spa\s?Manager\b",
    r"(?i)\bWellness\s?Spa\s?Manager\b",
    r"(?i)\bLuxury\s?Spa\s?Manager\b",
    r"(?i)\bSpa\s?Medical\s?Director\b",
    r"(?i)\bMedical\s?Day\s?Spa\s?Manager\b",
    r"(?i)\bWellness Specialist\b",
]

# Exact matches that should be updated
spa_exact_matches = {
    "Medical Spa Manager",
    "Med Spa Manager",
    "Spa Medical Manager",
    "Medical Aesthetic Spa Manager",
    "Manager of Medical Spa",
    "Director of Medical Spa",
    "Medical Wellness Spa Manager",
    "Spa Manager (Medical)",
    "Mediacal Spa Manager",
    "Medial Spa Manager",
    "Medical Sap Manager",
    "Medical Spaa Manager",
    "Medical Sspa Manager",
    "Medical Spaaa Manager",
    "Medial Spa Manger",
    "Medical Spa Manger",
    "Medcial Spa Manager",
    "Medical Spa Maneger",
    "Medical Spa Managr",
    "Medical Spaa Mngr",
    "Gerente de Spa Médico",
    "Administrador de Spa Médico",
    "Director de Spa Médico",
    "Encargado de Spa Médico",
    "Gerente de Bienestar Médico",
    "Coordinador de Spa Médico",
    "Aesthetic Spa Manager",
    "Cosmetic Spa Manager",
    "Wellness Spa Manager",
    "Luxury Spa Manager",
    "Spa Medical Director",
    "Medical Day Spa Manager",
    "Beauty",
    'AROMATHERAPY SPECIALIST',
    'CPMT LASER company s Guest',
}

# # Define patterns (these should NOT be changed)
# spa_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

spa_exclusions = {
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

# Create a mask for Medical Spa Manager
mask_spa = df['speciality'].str.contains('|'.join(spa_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(spa_exact_matches)

# mask_spa_exclusions = df['speciality'].str.contains(spa_exclusions, case=False, na=False, regex=True)
mask_spa_exclusions = df['speciality'].isin(spa_exclusions)

# Final mask: Select Medical Spa Manager
mask_spa_final = mask_spa & ~mask_spa_exclusions

# Store the original values that will be replaced
original_spa_values = df.loc[mask_spa_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_spa_final, 'speciality'] = 'Medical Spa Manager'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Medical Spa Manager", 'green'))
print(df.loc[mask_spa_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_spa_values = df.loc[mask_spa_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Medical Spa Manager", "cyan"))
for original_spa_value in original_spa_values:
    print(f"✅ {original_spa_value} → Medical Spa Manager")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Medical Spa Manager:", 'red'))
print(grouped_spa_values)

# Print summary
matched_count_spa = mask_spa_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Medical Spa Manager: "
        f"{matched_count_spa}",
        'red'))