import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Dentist related titles

dentist_variants = [
    r"(?i)\bdentist\b",
    r"(?i)\bdentis\b",
    r"(?i)\bdentis\s?specialist\b",
    r"(?i)\bdentista\b",
    r"(?i)\bdentista\s?oral\b",
    r"(?i)\bdentista\s?general\b",
    r"(?i)\bdoctor\s?dentist\b",
    r"(?i)\bDDS\b",
    r"(?i)\bDMD\b",
    r"(?i)\bOdontologist\b",
    r"(?i)\bImplantologist\b",
    r"(?i)\bDentistAesthetic Physician\b",
    r"(?i)\bGeneral Dentiste\b",
    r"(?i)\bMedico Odontoiatra\b",
    r"(?i)Odontoiatra",
    r"(?i)\bDentistry- Removable Prosthodontics\b",
    r"(?i)\bBDS\b",
    r"(?i)\bB D S\b",
    r"(?i)\bOdontologa\b",
    r"(?i)\bOdontologia\b",
    r"(?i)\bDentiste\b",
    r"(?i)\bDentistry Hof\b",
    r"(?i)\bProsthodontics\b",
    r"(?i)\bDentist & Aesthetician\b",
    r"(?i)\bOdontologist\b",
    r"(?i)\bImplantologist\b",
    r"(?i)\bDentist Aesthetic Doctor\b",
    r"(?i)\bOwner Dentist\b",
    r"(?i)\bOdontologa\b",
    r"(?i)\bDmd\b",
    r"(?i)\bDentistry Hof\b",
    r"(?i)\bDentistry\b",
    r"(?i)\bDentistry- Removable Prosthodontics\b",
    r"(?i)\bB D S\b",
    r"(?i)\bSpecialist Of Prosthodontics\b",
    r"(?i)\bOrofacial Dentist\b",
    r"(?i)\bGeneral Dentist\b",
    r"(?i)\bDentista Especialista Em Harmonizacao Orofacial\b",
    r"(?i)\bDentista\b",
    r"(?i)\bOdontologia\b",
    r"(?i)\bDentiste\b",
    r"(?i)\bBds\b",
    r"(?i)\bDoctor Of Dental Medicine\b",
    r"(?i)\bPediatric Dentist\b",
    r"(?i)\bDentist Orthodontics\b",
    r"(?i)\bDental Medicine\b",
    r"(?i)\bOdontoiatraa\b",
    r"(?i)\bGeneral Dentiste\b",
    r"(?i)\bDendis\b",
    r"(?i)\bDentist - Facial Harmonization\b",
    r"(?i)\bDentist & Esthetician\b",
    r"(?i)\bDentist Aesthetic\b",
    r"(?i)\bAesthetics Dentist\b",
    r"(?i)\bProsthodontics\b",
    r"(?i)\bDental Facial Aesthetics\b",
    r"(?i)\bDentistAesthetic Physician\b",
    r"(?i)\bDental & Skincare\b",
    r"(?i)\bDoctor Of Dental Medical\b",
    r"(?i)\bCosmetic Dentist Specializing In Veneers\b",
    r"(?i)\bDentist Dmd\b",
    r"(?i)\bMedico Odontoiatra\b",
    r"(?i)\bDentista Harmonizacao Orofacial\b",
    r"(?i)\bDental Doctor\b",
    r"(?i)\bDentist & Hp\b",
    r"(?i)\bGp Dentist\b",
    r"(?i)\bMedica Dentista\b",
    r"(?i)\bAesthetic Dentist\b",
    r"(?i)\bDoctor Dentist Spec\b",
    r"(?i)\bDentist Specializing In Orofacial Harmonization\b",
    r"(?i)\bDental Professional Aesthetic Practicioner\b",
    r"(?i)\bDental Professional\b",
    r"(?i)\bProf  Esthetic Medicine Dentist\b",
    r"(?i)\bDentist Naturopath\b",
    r"(?i)\bCosmetolog Dentist\b",
    r"(?i)\bDentist Aesthetic Medicine Doctor\b",
    r"(?i)\bDentist Facial Aesthetics\b",
    r"(?i)\bDental Therapist\b",
    r"(?i)\bMaxilofacial Dentist\b",
    r"(?i)\bStaff Dentist\b",
    r"(?i)\bDentist & Aesthetic Practiononer\b",
    r"(?i)\bMedico Dentista\b",
    r"(?i)\bDentist Facial Aesthetic & Dental Implants\b",
    r"(?i)\bDental Prosthodontics\b",
    r"(?i)\bCosmetic Dentist\b",
    r"(?i)\bAesthetician & Pediatric Dentist\b",
    r"(?i)\bDental & Aestetic Doctor\b",
    r"(?i)\bDentist & Med Spa\b",
]

# Exact matches that should be updated
dentist_exact_matches = {
    "Dr. Dentist",
    "Dr. [General Dentist]",
    "Dentistry",
    'Dental Clinic',
    'Dental Professional',
    'Dental',
    'Doctor Teeth',
    'DentistFacial Aesthetics',
    'Medicina Dentaria',
    'DentistOwner',
    'GDP',
}

# Define patterns (these should NOT be changed)
dentist_exclusions = [
    r"(?i)\bMaxillo\s?Facial\b",
    r"(?i)\bMaxillo-Facial\b",
    r"(?i)\bRecruiter\b",
] # maxillo variants

# Create a mask for Dentist
mask_dentist = df['speciality'].str.contains('|'.join(dentist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(dentist_exact_matches)
mask_dentist_exclusions = df['speciality'].isin(dentist_exclusions)

# Final mask: Select Dentist
mask_dentist_final = mask_dentist & ~mask_dentist_exclusions

# Store the original values that will be replaced
original_dentist_values = df.loc[mask_dentist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_dentist_final, 'speciality'] = 'Dentist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Dentist", 'green'))
print(df.loc[mask_dentist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_dentist_values = df.loc[mask_dentist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Dentist", "cyan"))
for original_dentist_value in original_dentist_values:
    print(f"✅ {original_dentist_value} → Dentist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Dentist:", 'red'))
print(grouped_dentist_values)

# Print summary
matched_count_dentist = mask_dentist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Dentist: "
        f"{matched_count_dentist}",
        'red'))