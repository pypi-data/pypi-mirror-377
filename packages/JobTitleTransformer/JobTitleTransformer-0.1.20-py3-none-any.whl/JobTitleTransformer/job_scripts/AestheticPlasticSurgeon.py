import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for aesthetics_antiaging_physician related titles
aesthetic_plastic_surgeon_variants = [
    r"(?i)\bAesthetic & Plastic Surgeon\b",
    r"(?i)\bChirurgien Esthetique\b",
    r"(?i)\bEsthetic Surgeon\b",
    r"(?i)\bAesthetic Surgery\b",
    r"(?i)\bDermatosurgery\b",
    r"(?i)\bPlastic Surgery & Aesthetic Medicine\b",
    r"(?i)\bCraniofacial Aesthetic & Plastic Surgeon\b",
    r"(?i)\bAesthetic Surgeon\b",
    r"(?i)\bPlastic & Aesthetic Surgeon\b",
    r"(?i)\bMedico EsteticistaCirurgia Plastica\b",
    r"(?i)\bPlastic Arsthetics\b",
    r"(?i)\bDermatologist Cosmetologist Plastic Surgery\b",
    r"(?i)\bConsultant Plastic & Aesthetic Surgeon\b",
    r"(?i)\bPlastic Surgery Aesthetic Surgery\b",
    r"(?i)\bAesthetic Plastic Surgeon\b",
    r"(?i)\bCosmetology & Plastic Surgery\b",
    r"(?i)\bPlastic Operations\b",
    r"(?i)\bChirurgie Esthetique\b",
    r"(?i)\bCirujano Estetico\b",
    r"(?i)\bMedico CirujanoMedico Esteticista\b",
    r"(?i)\bOtorrinolaringologo Y Cirujano Estetico\b",
    r"(?i)\bMedica De Cirurgia Estetica\b",
    r"(?i)\bMedico Cirujano Estetico Medico Estetico Antienvegesimiento\b",
    r"(?i)\bFacharzt Chirurgie Und Asthetische Medizin\b",
]

# Exact matches that should be updated

aesthetic_plastic_surgeon_exact_matches = {
    # Existing exact matches for exclusions
    'Aesthetic & Plastic Surgeon',
    'Aesthetic Surgery',
    'Aesthetic Chirurgien',
    'Chirurgien Esthetique',
    'Esthetic Chirurgeon',
    'Aesthetic Surgeon',
    'Aesthetic Surgery Injector',
    'Aesthetic Plastic Surgery Injector',
    'Plastic Arsthetics',
    'Dermatosurgery',
    'Surgeons of Aesthetic Plastic Surgery',
    'Restorative Aesthetic Surgery',
    'Chirurgienne Esthétique',
    'Aesthetic & Plastic Surgeon',

    # Variations for misspellings and case mistakes for Aesthetic Plastic Surgeon and related titles
    'Aesthetic & Platic Surgeon',
    'Aesthetic Surgeons',
    'Aesthetic Plastic Surgeons',
    'Plastic Surgeon Aesthetic',
    'Aesthetic Surgery Specialist',
    'Aesthetic Surgical Specialist',
    'Plastic Surgery Aesthetic',
    'Plastic Aesthetic Surgeon',
    'Aesthetic Plastic Surgeon Specialist',
    'Aesthetic Surgeon Specialist',
    'Plastic Surgeons Aesthetic',
    'Plastic Surgeons of Aesthetic Surgery',
    'Aesthetician Plastic Surgeon',
    'Aesthetic Surgery Specialist',
    'Surgical Aesthetic Surgeon',
    'Aesthetic Plastic Surgery Specialist',
    'Aesthetic Surgery Surgeons',
    'Aesthetic Surgeon Doctor',
    'Plastic Surgeon Aesthetic Specialist',
    'Aesthetic Surgical Doctor',
    'Aesthetic Surgery Doctor',
    'Plastic Surgery Doctor Aesthetic',

    # Common misspellings for Aesthetic Plastic Surgery titles
    'Aesthetic Pplastic Surgeon',
    'Aestheti Surgery',
    'Aesthetic Pastic Surgeon',
    'Aestehtic Surgeon',
    'Aesthetic Surgen',
    'Aesthetic Plastc Surgeon',
    'Aesthetic Surgon',
    'Aesthetic Plastic Surgon',
    'Aesthtic Surgeon',
    'Plastic Arsthetics Specialist',
    'Aesthetic Surgen',
    'Aesthetic & Platic Surgeon',

    # Case-related errors for Aesthetic Plastic Surgeon
    'aesthetic & Plastic surgeon',
    'Aesthetic Plastic surgeon',
    'Aesthetic surgeron',
    'aesthetic surgery injector',
    'plastic Aesthetic surgeon',
    'aesthetic and plastic Surgeon',
    'plastic Surgeon aesthetic',
    'aesthetic surgery injector',
    'plastic & Aesthetic surgeon',
    'Plastic Surgeon aesthetic',

    # Variants of Aesthetic Surgeon for different types of surgeries
     'Aesthetic Surgery Body Surgeon',
    'Aesthetic Body Plastic Surgeon',

    # Other possible variations (Including Doctor forms, Specialist forms)
    'Aesthetic Plastic Surgery Doctor',
    'Doctor Aesthetic Plastic Surgeon',
    'Aesthetic & Plastic Surgeon Doctor',
    'Doctor of Aesthetic Surgery',
    'Aesthetic Surgical Doctor',
    'Doctor of Aesthetic Plastic Surgery',

    # Excluding Aesthetic Plastic Surgery titles with variations of surgeons
    'Aesthetic Plastic Surgeon Specialist',
    'Aesthetic Plastic Surgery Consultant',
    'Plastic Surgery Cosmetic Specialist',
    'Aesthetic Surgery Specialist',
    'Aesthetic Surgeon & Specialist',
    'International Exchange & Cooperation Department Of China Plastic & Aesthetic Association',
    'Aestethic surgeon',
}

# Define patterns for Maxillo & Facial Plastic & Resident (these should NOT be changed)
aesthetic_plastic_surgeon_exclusions = {
    # Existing exact matches for exclusions
    'Maxillo Facial Plastic Surgery',
    'Resident Plastic Surgery',
    'Facial Plastic Surgery',
    'Head Of The Department Of Facial & Plastic Surgery',
    'Head Of Department Of Plastic Surgery',
    'Cosmetic Doctor Plastic Surgery Resident',
    'Facial Aesthetics Plastic Surgery',
    'Resident In Plastic Surgery',
    'Assistant Professor In Plastic Surgery/Hawler Me',
    'Professor Of Plastic Surgery',
    'Associate Professor Of Plastic Surgery',
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
    'Plastic & Reconstructive Surgeon',
    'Plastic Surgery Medical Assistant',
    'Rnbn Clinic Director Plastic Surgery Centre',
    'Coo Of A Clinic For Plastic Surgery',
    'Rep Sr Plastic Surgery Us Plastice Surgery',

    # Variations for misspellings and case mistakes for Maxillo/Facial/Plastic Surgery
    'Maxillofacial Plastic Surgery',
    'Maxillo-Facial Plastic Surgery',
    'Facial Aesthetic Plastic Surgery',
    'Maxillofacial Surgery Resident',
    'Resident Facial Surgery',
    'Plastic Surgeon Resident',
    'Facial Plastic Surgeon Resident',
    'Plastic Surgery Resident',
    'Maxillofacial Surgeon Resident',
    'Maxillo Facial Surgery Resident',
    'Maxillofacial Plastic Surgery Fellow',
    'Resident Maxillofacial Surgeon',
    'Cosmetic Surgeon Resident',
    'Plastic Surgery Intern',
    'Resident Surgeon (Plastic Surgery)',
    'Assistant Professor Maxillofacial Surgery',
    'Assistant Professor Plastic Surgery',
    'Facial Plastic Surgery Fellow',
    'Fellow in Maxillofacial Surgery',
    'Junior Maxillofacial Surgeon',
    'Plastic Surgery Fellow',
    'Professor Plastic Surgery',
    'Plastic Surgery Trauma Co-Ordinator',

    # Variants of student/professor related titles:
    'Plastic Surgery Student',
    'Student in Plastic Surgery',
    'Clinical Fellow Maxillofacial Surgery',
    'Junior Plastic Surgeon',
    'Fellow in Facial Plastic Surgery',
    'Facial Surgeon Fellow',
    'Trainee Plastic Surgeon',
    'Resident Surgeon Maxillofacial',
    'Intern Plastic Surgery',
    'Plastic Surgery Postgraduate',
    'Trainee Aesthetic Plastic Surgeon',
    'Postgraduate Fellow Plastic Surgery',
    'Fellow Aesthetic Surgery',
    'Plastic Surgery Resident Trainee',
    'Clinical Fellow Plastic Surgery',
    'Maxillofacial Surgery Resident',
    'Facial Surgery Intern',
    'Facial Surgeon Resident',
    'Junior Facial Surgeon',
    'Professor Maxillofacial Surgery',
    'Assistant Plastic Surgery Professor',
    'Junior Facial Plastic Surgeon',
    'Facial Surgery Postgraduate Trainee',

    # Common misspellings and alternative phrasings
    'Maxillo-Facial Surgeon',
    'Maxillofacial Surgeion',
    'Facial Surgeon',
    'Plastic Surgeion',
    'Facial Surgeron',
    'Maxillofaciel Surgery',
    'Maxillofacial Surgery',
    'Facial Plastc Surgery',
    'Facial Plastc Surgeon',
    'Maxilofacial Surgery',
    'Maxillofacial Surrgery',
    'Facial Surgery Specalist',
    'Facial Surgery Practitionar',
    'Facial Plastic Surgeon',
    'Facial Surgery Doctor',
    'Maxillofacial Plastician',
    'Maxillofacial Aesthetician',
    'Facial Surgery Resident',
    'Facial Plastic Surgeon Resident',
    'Maxillofacial Practitioner',
    'Aesthetic Maxillofacial Surgeon',
    'Junior Facial Plastic Surgery',

    # Case-related errors
    'Maxillo Facial Plastic Surgeonn',
    'Facial Platic Surgery',
    'Maxillo Face Surgery',
    'Plastic Surgon Resident',
    'Maxillo-Facial Plastic Surgon',
    'Facial Plastics Surgeion',
    'Fellow in Maxillo Facial Surgery',
    'Resident Facial Surgeon',
    'Maxillofacial Aesthetic Surgeon',
    'Resident Facail Surgeon',
    'Maxillofacial Plastic Surgery Fellow',
    'Maxillofacial Surgery Fellow',
    'Aesthetic Facail Surgeon',
    'Maxillofacial Plastician Resident',
    'Plastic Surgery Pa',

    # Additional Facial Plastic Surgeon-related titles:
    'Facial Plastic Surgeon',
    'Facial Reconstructive Surgeon',
    'Facial Plastic Surgeon Specialist',
    'Plastic & Reconstructive Surgeon',
    'Plastic Reconstructive & Aesthetic Surgeon',
    'Reconstructive Facial Plastic Surgeon',
    'Reconstructive Surgeon',
    'Cosmetic Facial Plastic Surgeon',
    'Cosmetic & Reconstructive Facial Surgeon',
    'Plastic & Reconstructive Surgeon',
    'Plastic & Reconstructive Surgery Fellow',
    'Facial Aesthetic Plastic Surgeon',
    'Facial Aesthetic Surgeon',
    'Facial Plastic Surgery Specialist',
    'Facial Cosmetic Surgeon',
    'Plastic Surgeon (Facial Surgery)',
    'Aesthetic Plastic & Reconstructive Surgeon',
    'Aesthetic Facial Plastic Surgeon',
    'Cosmetic Facial Surgeon',
    'Reconstructive Plastic Surgeon',
    'Facial Plastic Surgeon (Cosmetic)',
    'Facial Plastic Surgery Doctor',

    # Misspellings and case-related errors for Facial Plastic Surgeons:
    'Facial Plastc Surgeon',
    'Facial Surgeoon',
    'Plastic Surgion (Facial)',
    'Facial Surrgeon',
    'Facial Plastic Surgery Doctor',
    'Facial Plastic Surgon',
    'Cosmetic Facial Surgeon',
    'Plastic & Reconstructive Surgeion',
    'Reconstructive Facial Surgeion',
    'Plastic Reconstructive Surgeion',
    'Facial Plastic Surgeon (Reconstructive)',
    'Facial Cosmetic Surgeron',
    'Facial Plastic Surgery Spcialist',
    'Senior Resident Department Of Plastic Surgery',
    'Rep Plastic Surgery Us Plastic Surgery',
    'Plastic Rekonstructive & Aesthetic Surgery',
    'Plastic Reconstructive & Aesthetic Surgery',
    'Consultant Facial Plastic Surgeon',
    'Plastic Reconstructive Aesthetic Surgery',
}

# Create a mask for aesthetic_plastic_surgeon
mask_aesthetic_plastic_surgeon = df['speciality'].str.contains('|'.join(aesthetic_plastic_surgeon_variants), case=False, na=False, regex=True) | \
            df['speciality'].isin(aesthetic_plastic_surgeon_exact_matches)
mask_aesthetic_plastic_surgeon_exclusions = df['speciality'].isin(aesthetic_plastic_surgeon_exclusions)

# Final mask: Select Aesthetic & Plastic Surgeon values
mask_aesthetic_plastic_surgeon_final = mask_aesthetic_plastic_surgeon & ~mask_aesthetic_plastic_surgeon_exclusions

# Store the original values that will be replaced
original_aesthetic_plastic_surgeon_values = df.loc[mask_aesthetic_plastic_surgeon_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_aesthetic_plastic_surgeon_final, 'speciality'] = 'Aesthetic & Plastic Surgeon'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Aesthetic & Plastic Surgeon", 'green'))
print(df.loc[mask_aesthetic_plastic_surgeon_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_aesthetic_plastic_surgeon_values = df.loc[mask_aesthetic_plastic_surgeon_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Aesthetic & Plastic Surgeon", "cyan"))
for original_aesthetic_plastic_surgeon_value in original_aesthetic_plastic_surgeon_values:
    print(f"✅ {original_aesthetic_plastic_surgeon_value} → Aesthetic & Plastic Surgeon")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Aesthetic & Plastic Surgeon:", 'red'))
print(grouped_aesthetic_plastic_surgeon_values)

# Print summary
matched_count_aesthetic_plastic_surgeon = mask_aesthetic_plastic_surgeon_final.sum()

# Print results
print(colored(f"\nTotal values matched and changed (Stage 1) to Aesthetic & Plastic Surgeon: {matched_count_aesthetic_plastic_surgeon}", 'red'))