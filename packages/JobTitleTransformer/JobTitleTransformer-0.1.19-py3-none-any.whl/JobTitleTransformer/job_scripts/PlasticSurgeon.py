import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Plastic Surgeon related titles

plastic_surgeon_variants = [
    # Standard Titles & Variants
    r"(?i)\bCosmetic and Plastic Surgeon\b",
    r"(?i)\bSpecialistinplasticsurgery\b",

    # Misspellings & Typographical Errors
    r"(?i)\bPlasic Surgeon\b",
    r"(?i)\bPlastic Surgon\b",
    r"(?i)\bPlastic Surgen\b",
    r"(?i)\bPlstic Surgeon\b",

    # Spanish Variants
    r"(?i)\bCirujano Plástico\b",
    r"(?i)\bCirujano Plástico Especialista\b",

    # Other Possible Variations
    r"(?i)\bCosmetic and Plastic Surgery Specialist\b",
    r"(?i)\bPlastic Surgery Expert\b",
    r"(?i)\bConsultantPlastic Surgeon\b",
    r"(?i)\bConsultantPlastic Surgery\b",
    r"(?i)\bInjectablesPlastic Surgery\b",
    r"(?i)\bPlaatic Surgery\b",
    r"(?i)\bPlasti Surgeon\b",
    r"(?i)\bPlastnic Surgeon\b",
    r"(?i)\bPlastic Surgical\b",
    r"(?i)\bPlastic Surgeons\b",
    r"(?i)\bChirurgia Plastica\b",
    r"(?i)\bSurgery Plastic\b",
    r"(?i)\bCirurgiao Plastico\b",
    r"(?i)\bChirurgie Plastica\b",
    r"(?i)\bPlasticsurgeon\b",
    r"(?i)\bConsultant Plastic Surgery\b",
    r"(?i)\bHead Of Plastic Surgery\b",
    r"(?i)\bPlastic Surgery\b",
    r"(?i)\bSpecialist Plastic Surgery\b",
    r"(?i)\bPlastic Surgeron\b",
    r"(?i)\bChief - Section Of Plastic Surgery\b",
    r"(?i)\bBurns & Plastic Surgery\b",
    r"(?i)\bPlastic Surgery Consultant\b",
    r"(?i)\bPlastic Surgery Specialist\b",
    r"(?i)\bDirector Plastic Surgery\b",
    r"(?i)\bPlasticAesthetic Surgery\b",
    r"(?i)\bDirector Advanced Plastic Surgery Centre\b",
    r"(?i)\bPlatic Surgeon\b",
    r"(?i)\bOphthalmic Plastic Surgery\b",
    r"(?i)\bPlastic Surgery Non Board Certified\b",
    r"(?i)\bPlastic Surgery Md Phd\b",
    r"(?i)\bEnt Plastic Surgery\b",
    r"(?i)\bDirector General & Hd Of Plastic Surgery Dept\b",
    r"(?i)\bChief - Plastic Surgery\b",
    r"(?i)\bChief Pediatric Plastic Surgery\b",
    r"(?i)\bDirector Of Injectables Bucky Plastic Surgery\b",
    r"(?i)\bChirurgien Plasticien\b",
    r"(?i)\bChirurgie Plastica\b",
    r"(?i)\bCirurgia Plastica\b",
    r"(?i)\bCirujano Plastico\b",
    r"(?i)\bChirurgie Plastique\b",
    r"(?i)\bMedica Cirurgia Plastica\b",
    r"(?i)\bMedico Chirurgo Plastico\b",
    r"(?i)\bPlastic Chirurgie\b",
    r"(?i)\bCirujano Plasico\b",
    r"(?i)\bPlasticheskii Khirurg\b",
    r"(?i)\bConsultant Plastic Surgeon\b",
    r"(?i)\bBeverly Hills Plastic Surgeon\b",
]

# Exact matches that should be updated
plastic_surgeon_exact_matches = {
    "Plastic Surgeon",
    "Cosmetic and Plastic Surgeon",
    "Plasic Surgeon",
    "Plastic Surgon",
    "Plastic Surgen",
    "Plstic Surgeon",
    "Cirujano Plástico",
    "Cirujano Plástico Especialista",
    "Aesthetic Surgery Specialist",
    "Cosmetic and Plastic Surgery Specialist",
    "Plastic Surgery Expert",
    "Plastic",
    "Plastics",
    'Plastic Surgery',
    'Plastic Surgeon',
    'Plasticsurgeon',
    'Plasic Surgeon',
    'PlastiC Surgeon',
    'Plastic Surgery Specialist',
    'Plastic Surgeron',
    'Platic Surgeon',
    'PlastiC Surgeon',
    'Plastc Surgeon',
    'Plastc Surgeron',
    'Plasticsurgen',
    'Plasic Surgeon',
    'Plastic Surgeion',
    'plasticsurgeon',
    'Plasticsurgen',
    'Plastic Surgeon',
    'Plastic surgeon',
    'plastic surgeon',
    'PlasticSurgeon',
    'Plasticsurgeon',
    'Cirugia Plastica',
    'Medical Director & Plastic Surgeon',
    'Plastic Surgeon & Medical Director',
    'Plastic Surgeon - Antiaging Practicioner',
    'Md Plastics',
    'Chirurgia Palastica',
    'Cirujana Plastica',
    'Board Certified Plastic Surgeon',
    'Medical Director Plastic Surgeon',
}

# # Define patterns (these should NOT be changed)
plastic_surgeon_exclusions = r'\b(?:Aesthetic)|(?:Facial)|(?:Maxillofacial)|(?:Resident)|(?:Professor)|(?:Sales)\b'

# plastic_surgeon_exclusions = {
#     'Resident', 'resident', 'student', 'Trainee', 'Resident Doctor', 'Resident ooPhysician',
#     'Intern', 'intern', 'Medical Intern', 'Fellow', 'fellow', 'Clinical Fellow', 'Medical Student',
#     'Clinical Trainee', 'Trainee Doctor', 'Trainee Physician', 'Junior Doctor', 'Postgraduate Trainee',
#     'Aesthetic Fellow', 'Aesthetic Trainee', 'Aesthetic Medicine Fellow', 'Aesthetic Resident'
# }

# Create a mask for Plastic Surgeon
mask_plastic_surgeon = df['speciality'].str.contains('|'.join(plastic_surgeon_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(plastic_surgeon_exact_matches)

mask_plastic_surgeon_exclusions = df['speciality'].str.contains(plastic_surgeon_exclusions, case=False, na=False, regex=True)
# mask_plastic_surgeon_exclusions = df['speciality'].isin(plastic_surgeon_exclusions)

# Final mask: Select Plastic Surgeon
mask_plastic_surgeon_final = mask_plastic_surgeon & ~mask_plastic_surgeon_exclusions

# Store the original values that will be replaced
original_plastic_surgeon_values = df.loc[mask_plastic_surgeon_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_plastic_surgeon_final, 'speciality'] = 'Plastic Surgeon'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Plastic Surgeon", 'green'))
print(df.loc[mask_plastic_surgeon_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_plastic_surgeon_values = df.loc[mask_plastic_surgeon_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Plastic Surgeon", "cyan"))
for original_plastic_surgeon_value in original_plastic_surgeon_values:
    print(f"✅ {original_plastic_surgeon_value} → Plastic Surgeon")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Plastic Surgeon:", 'red'))
print(grouped_plastic_surgeon_values)

# Print summary
matched_count_plastic_surgeon = mask_plastic_surgeon_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Plastic Surgeon: "
        f"{matched_count_plastic_surgeon}",
        'red'))