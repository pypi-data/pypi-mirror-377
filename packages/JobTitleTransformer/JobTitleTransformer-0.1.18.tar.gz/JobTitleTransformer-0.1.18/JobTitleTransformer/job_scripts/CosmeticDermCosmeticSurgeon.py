import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Cosmetic Dermatologist related titles

cosmetic_dermatologist_variants = [
    # Standard title variations
    r"(?i)\bCosmetic\s?Dermatologist\b",
    r"(?i)\bDermatologist\s?Cosmetic\b",
    r"(?i)\bCosmetic\s?Skin\s?Specialist\b",
    r"(?i)\bDoctor\s?of\s?Cosmetic\s?Dermatology\b",
    r"(?i)\bCosmetic\s?Skin\s?Doctor\b",
    r"(?i)\bAesthetic\s?Dermatologist\b",
    r"(?i)\bSkin\s?Care\s?Specialist\b",

    # Common misspellings and case mistakes
    r"(?i)\bCosmetic\s?Dermotologist\b",
    r"(?i)\bCosmetick\s?Dermatologist\b",
    r"(?i)\bCosmotik\s?Dermatologist\b",
    r"(?i)\bKosmetic\s?Dermatologist\b",
    r"(?i)\bCosmetic\s?Dermetologist\b",

    # Variants in Spanish and other languages
    r"(?i)\bDermatólogo\s?Cosmético\b",
    r"(?i)\bMédico\s?Estético\b",
    r"(?i)\bEspecialista\s?en\s?Dermatología\s?Cosmética\b",

    # Other possible variations
    r"(?i)\bBoard\s?-?\s?Certified\s?Cosmetic\s?Dermatologist\b",
    r"(?i)\bGeneral\s?Cosmetic\s?Dermatologist\b",
    r"(?i)\bCosmeti Dermatology\b",
    r"(?i)\bLikar Dermatolog\b",
    r"(?i)\bCosmetic Dermatplpgy\b",
    r"(?i)\bConsultant DermatologistCosmetologist\b",
    r"(?i)\bCosmetic Dermatology\b",
    r"(?i)\bCosmetic Injecting\b",
    r"(?i)\bMedical Cosmetic\b",
    r"(?i)\bDermal Filler\b",
    r"(?i)\bKosmetische Medizin\b",
    r"(?i)\bCosmetic Injectables\b",
    r"(?i)\bMedica Procedimento Estetico\b",
    r"(?i)\bEstetica Facial\b",
    r"(?i)\bVrach Dermatokosmetolog\b",
    r"(?i)\bDermatology - Medical Devices\b",
    r"(?i)\bFacial Rejuvenation & Improvement Of Skin Quality With A Combination Of Injectable Treatments Of Hyaluronic Acid Calcium Hydroxyapatite & Botulinum Toxin Type A A Case Report\b",
    r"(?i)\bAnti Wrinkle Tx\b",
    r"(?i)\bDermocosmetics\b",
    r"(?i)\bDermatologistCosmetologist\b",
    r"(?i)\bDermato Cosmetolog\b",
    r"(?i)\bEstetica E Cosmetica\b",
    r"(?i)\bCosmiatra\b",
    r"(?i)\bCosmetic Efficacy\b",
    r"(?i)\bAnti-Wrinkle\b",
]

# Exact matches that should be updated
cosmetic_dermatologist_exact_matches = {
    "Cosmetic Dermatologist",
    "cosmetic dermatologist",
    "COSMETIC DERMATOLOGIST",
    "Cosmetic Dermotologist",
    "Cosmetick Dermatologist",
    "Cosmotik Dermatologist",
    "Kosmetic Dermatologist",
    "Cosmetic Dermetologist",
    "Cosmeti Dermatology",
    'Dermal Fillers',
    'dermal fillers',
    'dermal filler',
    'Dermal Filler',

    # Variants in Spanish
    "Dermatólogo Cosmético",
    "Médico Estético",
    "Especialista en Dermatología Cosmética",

    # Hybrid terms (English-Spanish combinations)
    "Cosmetic Dermatólogo",
    "Cosmetico Dermatologist",

    # Values from data sources
    "Cosmetic Dermatology",
    "cosmetic dermatology",
    "Aesthetic Dermatologist",
    'Cosmetic MedicineAesthetics',
    'Cosmetisch Arts',
    'DirectorSenior Dermal',
    'Dermal',
    'Vrach Kosmetolog Dermatolog',
    'Cosmetic Department',
    'Prp',
    'PRP',
    'prp',
    'Dermatology Therapeutic Specialist',
    'Senior Dermatology Therapeutic Specialist',
}

# Define patterns (these should NOT be changed)
cosmetic_dermatologist_exclusions = {
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
    'Registered Nurse Cosmetic Injectables',
}

# Create a mask for cosmetic_surgeon
mask_cosmetic_dermatologist = df['speciality'].str.contains('|'.join(cosmetic_dermatologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(cosmetic_dermatologist_exact_matches)
mask_cosmetic_dermatologist_exclusions = df['speciality'].isin(cosmetic_dermatologist_exclusions)

# Final mask: Select cosmetic_surgeon
mask_cosmetic_dermatologist_final = mask_cosmetic_dermatologist & ~mask_cosmetic_dermatologist_exclusions

# Store the original values that will be replaced
original_cosmetic_dermatologist_values = df.loc[mask_cosmetic_dermatologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_cosmetic_dermatologist_final, 'speciality'] = 'Cosmetic Dermatologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Cosmetic Dermatologist", 'green'))
print(df.loc[mask_cosmetic_dermatologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_cosmetic_dermatologist_values = df.loc[mask_cosmetic_dermatologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Cosmetic Dermatologist", "cyan"))
for original_cosmetic_dermatologist_value in original_cosmetic_dermatologist_values:
    print(f"✅ {original_cosmetic_dermatologist_value} → Cosmetic Dermatologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Cosmetic Dermatologist:", 'red'))
print(grouped_cosmetic_dermatologist_values)

# Print summary
matched_count_cosmetic_dermatologist = mask_cosmetic_dermatologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Cosmetic Dermatologist: "
        f"{matched_count_cosmetic_dermatologist}",
        'red'))


# Consmetic Surgeon

# Define regex patterns for Cosmetic Surgeon related titles

cosmetic_surgeon_variants = [
    # Standard title variations
    r"(?i)\bCosmetic\s?Surgeon\b",
    r"(?i)\bSurgeon\s?Cosmetic\b",
    r"(?i)\bCosmetic\s?Surgery\s?Specialist\b",
    r"(?i)\bSurgeon\s?for\s?Cosmetic\s?Procedures\b",
    r"(?i)\bDoctor\s?of\s?Cosmetic\s?Surgery\b",
    r"(?i)\bCosmetic Physician\b",
    r"(?i)\bCosmetic Surgery\b",
    r"(?i)\bCosmetic & Reconstruction Surgeon\b",
    r"(?i)\bCosmetic Physicians\b",

    # Common misspellings and case mistakes
    r"(?i)\bCosmetic\s?Surgion\b",
    r"(?i)\bCosmetick\s?Surgeon\b",
    r"(?i)\bCosmotik\s?Surgeon\b",
    r"(?i)\bKosmetic\s?Surgeon\b",
    r"(?i)\bCosmetic\s?Surjen\b",

    # Variants in Spanish and other languages
    r"(?i)\bCirujano\s?Cosmético\b",
    r"(?i)\bCirujano\s?Estético\b",
    r"(?i)\bMédico\s?Estético\b",

    # Other possible variations
    r"(?i)\bAesthetic Surgeon\b",
    r"(?i)\bBoard\s?-?\s?Certified\s?Cosmetic\s?Surgeon\b",
    r"(?i)\bCosmeti Surgery\b",
    r"(?i)\bGeneralCosmetic Surgeon\b",
    r"(?i)\bLikar Kosmetolog\b",
    r"(?i)\bCosmetic Physicion\b",
    r"(?i)\bDr  Kosmetolog\b",
    r"(?i)\bCoametic Surgeon\b",
]

# Exact matches that should be updated
cosmetic_surgeon_exact_matches = {
    "Cosmetic Surgeon",
    "Cosmetic Surgeon",
    "Cosmetic Surgeon",
    "Cosmetic Surgeon",
    "Cosmetic Surgeon",
    "Cosmetic Surgeon",
    "Cosmetic Surgeon",
    "Cosmetic Surgeon",
    "Cosmetic Surgeon",
    "Cosmetic Surgeon",
    "Cosmetic Surgeon",
    "Cosmetic Surgeon",
    "Cosmetic Surgeon",
    "Cosmetic Surgeon",
    "Cosmetic Surgeon",
    "Cosmetic Surgeon",

    # Common misspellings for Cosmetic Surgeon titles
    "Cosmetic Surgion",
    "Cosmetick Surgeon",
    "Cosmotik Surgeon",
    "Kosmetic Surgeon",
    "Cosmetic Surjen",
    "Cosmetik Surjen",
    "Kosmetic Surjen",
    "Cosmetic Surgeoon",

    # Case-related errors for Cosmetic Surgeon
    "cosmetic surgeon",
    "COSMETIC SURGEON",
    "Cosmetic Surgeon",
    "cosmetik surgeon",
    "kosmetic surgeon",
    "cosmetic surjen",
    "cosmetic surgeoon",

    # Variants of Cosmetic Surgeon in Spanish
    "Cirujano Cosmético",
    "Cirujano Estético",
    "Médico Estético",

    # Hybrid terms (Including English-Spanish combinations)
    "Cosmetic Cirujano",
    "Cosmetico Surgeon",

    # values from data sources
    'Cosmetic Doctor',
    'CIRUGIA COSMETICA',
}

# Define patterns (these should NOT be changed)
cosmetic_surgeon_exclusions = {
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
    'Plastic Reconstructive & Aesthetic Surgeon',
    'Cosmetic Surgery Fellow In Training',
}

# Create a mask for cosmetic_surgeon
mask_cosmetic_surgeon = df['speciality'].str.contains('|'.join(cosmetic_surgeon_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(cosmetic_surgeon_exact_matches)
mask_cosmetic_surgeon_exclusions = df['speciality'].isin(cosmetic_surgeon_exclusions)

# Final mask: Select cosmetic_surgeon
mask_cosmetic_surgeon_final = mask_cosmetic_surgeon & ~mask_cosmetic_surgeon_exclusions

# Store the original values that will be replaced
original_cosmetic_surgeon_values = df.loc[mask_cosmetic_surgeon_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_cosmetic_surgeon_final, 'speciality'] = 'Cosmetic Surgeon'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Cosmetic Surgeon", 'green'))
print(df.loc[mask_cosmetic_surgeon_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_cosmetic_surgeon_values = df.loc[mask_cosmetic_surgeon_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Cosmetic Surgeon", "cyan"))
for original_cosmetic_surgeon_value in original_cosmetic_surgeon_values:
    print(f"✅ {original_cosmetic_surgeon_value} → Cosmetic Surgeon")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Cosmetic Surgeon:", 'red'))
print(grouped_cosmetic_surgeon_values)

# Print summary
matched_count_cosmetic_surgeon = mask_cosmetic_surgeon_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Cosmetic Surgeon: "
        f"{matched_count_cosmetic_surgeon}",
        'red'))