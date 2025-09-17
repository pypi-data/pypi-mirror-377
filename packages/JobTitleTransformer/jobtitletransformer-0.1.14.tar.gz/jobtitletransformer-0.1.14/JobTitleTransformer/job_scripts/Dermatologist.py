import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Dermatologist related titles

dermatologist_variants = [
    r"(?i)\bdermatologist\b",
    r"(?i)\bdermatologists\b",
    r"(?i)\bdermatologist\s?md\b",
    r"(?i)\bdermatologist\s?doctor\b",
    r"(?i)\bdermatology\s?specialist\b",
    r"(?i)\bboard-certified\s?dermatologist\b",
    r"(?i)\bcertified\s?dermatologist\b",
    r"(?i)\bskin\s?specialist\b",
    r"(?i)\bdoctor\s?of\s?dermatology\b",
    r"(?i)\bdermatology\s?physician\b",
    r"(?i)\bdermatologiste\b",
    r"(?i)\bdermatologo\b",
    r"(?i)\bdermatologo(a)?\b",
    r"(?i)\bDermatologista\b",
    r"(?i)\bDermatologia\b",
    r"(?i)\bMedica Dermatologista\b",
    r"(?i)\bDermatologue\b",
    r"(?i)\bDermatologie\b",
    r"(?i)\bDermatologa\b",
    r"(?i)\bDermatovenereologist\b",
    r"(?i)\bDermatology & Venereology\b",
    r"(?i)\bAesthetic Dermatilogy\b",
    r"(?i)\bAesthetic Dernatology\b",
    r"(?i)\bAesthetic MedicineDermatology\b",
    r"(?i)\bMedica Dematologista\b",
    r"(?i)\bDermatogist\b",
    r"(?i)\bHead Of Dermatology\b",
    r"(?i)\bMole Screening\b",
    r"(?i)\bAesthetic & Clinical Dermatology\b",
    r"(?i)\bMsc Dermatology\b",
    r"(?i)\bPedderm\b",
    r"(?i)\bDermat\b",
    r"(?i)\bDermatologyst\b",
    r"(?i)\bDermathology\b",
    r"(?i)\bDermatologi Dan Venereologi\b",
    r"(?i)\bDermatovenerologist\b",
    r"(?i)\bDermatologyst\b",
    r"(?i)\bDermatologyst\b",
    r"(?i)\bDermatovenerology\b",
    r"(?i)\bDeematology\b",
    r"(?i)\bDermotoloji\b",
    r"(?i)\bDermatolgy\b",
    r"(?i)\bSkin Medical & Aesthetic\b",
    r"(?i)\bDermatoloji\b",
    r"(?i)\bDermstolog\b",
    r"(?i)\bImmunodermatology\b",
    r"(?i)\bDeramtology\b",
    r"(?i)\bSkin Msc\b",
    r"(?i)\bFamily PracticeDermatology\b",
    r"(?i)\bDermato Funcional\b",
    r"(?i)\bDermatologiss\b",
    r"(?i)\bSkin Specialist\b",
    r"(?i)\bDr Skin Care Professional\b",
    r"(?i)\bAesthetic DermatologistAnti-Aging\b",
]

# Exact matches that should be updated
dermatologist_exact_matches = {
    "Dermatologist",
    "Dermatologists",
    "Dermatologist MD",
    "Board-Certified Dermatologist",
    "Certified Dermatologist",
    "Doctor of Dermatology",
    "Skin Specialist",
    "Dermatologo",
    "Dermatologo(a)",
    "Dermatology",
    "Derm",
    "Derma",
    "Skin",
    "Aesthetic Dermatology",
    "Skin Clinic",
    'Filler',
    'Specialist Dermatology',
    'ConsultantDermatology',
    'Dermal Clinician',
    'Dermato',
    'Dermatolog',
    'Doctor Dermatology',
    'Md PhdDermatologist',
    'Chairman Dermatology Department',
    'Aesthetics & Dermatology',
    'Chair Of The Department Of Dermatology ',
    'Medicos Dermatologistas Credenciados A SbdSbcp',
    'Skin Aesthetic',
    'Chair Of The Department Of Dermatology',
    'Dermato Venereologist',
    'Dermatology & Aesthetic Medicine',
    'Dermatology & Medical Aesthetics',
    'Deematologist',
    'Specialist In Dermatology',
    'Dermatologogist',
    'Dermatolyst',
    'Dermatoly',
    'DermatologistaDermatologia Estetica',
    'Dermato-Venereologist',
    'Consultants Dermatology',
    'Dermatology Consultant',
    'Fabia valente',
}

# Define patterns (these should NOT be changed)
dermatologist_exclusions = {
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
    'Cosmetic Dermatologist',
    'Estudiante De Dermatologia  Cosmetologa En Ucrania',
    'Resident Of Dermatology & Venereology',
    'Resident Of Dermatovenereologist',
    'Dermatovenereologist Resident',
    'Consultant Dermatologist & Hair Transplant Surgeon',
    'Professor Of Dermatology & Co-Director Immunodermatology Laboratory',
    'Dermatologist Resident',
    'Residence Dermatologist',
    'Dermatologie Residence',
    'Sales Medical Dermatology Specialist',
    'Sales Executive & Immunology Dermatology Specialist',
    'Immunology Sales -Dermatology Specialist',
    'Dermatology Physician Assistant',
    'Immunology Sales Dermatology Specialist',
    'Resident dermatologist',
}

# Create a mask for Dermatologist
mask_dermatologist = df['speciality'].str.contains('|'.join(dermatologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(dermatologist_exact_matches)
mask_dermatologist_exclusions = df['speciality'].isin(dermatologist_exclusions)

# Final mask: Select Dermatologist
mask_dermatologist_final = mask_dermatologist & ~mask_dermatologist_exclusions

# Store the original values that will be replaced
original_dermatologist_values = df.loc[mask_dermatologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_dermatologist_final, 'speciality'] = 'Dermatologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Dermatologist", 'green'))
print(df.loc[mask_dermatologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_dermatologist_values = df.loc[mask_dermatologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Dermatologist", "cyan"))
for original_dermatologist_value in original_dermatologist_values:
    print(f"✅ {original_dermatologist_value} → Dermatologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Dermatologist:", 'red'))
print(grouped_dermatologist_values)

# Print summary
matched_count_dermatologist = mask_dermatologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Dermatologist: "
        f"{matched_count_dermatologist}",
        'red'))