import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Aesthetic & Anti-Aging Physician related titles (Variants)
aesthetic_antiaging_physician_variants = [
    r'\b(?:Aesthetic & Anti Aging|Aesthetic & AntiAging|Aesthetic & Antiaging)\b',
    r"(?i)\bAesthetic Antiage & Resgenerative Medicine\b",
    r"(?i)\bAppearance Medicine\b",
    r"(?i)\bSkin Rejuvenation & Resurfacing\b",
    r"(?i)\bNon Surgery\b",
    r"(?i)\bAesthetic Body Contouring Specialist\b",
    r"(?i)\bAesthetic&Anti-Aging Physcian\b",
    r"(?i)\bDr  Aesthetic & Anti-Aging Medicine\b",
]

# Exact matches that should be updated
aesthetic_antiaging_physician_exact_matches = {
    'Aesthetic & Anti Aging Physician',
    'Aesthetic & AntiAging Physician',
    'Aesthetic & Antiaging Physician',
    'Aesthetic & Anti Aging Practitioner',
    'Aesthetic & AntiAging Practitioner',
    'Aesthetic & Antiaging Practitioner',
    'Aesthetic & Anti-Aging Practitioner',
    'Aesthetic Anti-Aging Physician',
    'Aesthetic Anti Aging Physician',
    'Aesthetic AntiAging Physician',
    'Aesthetic Antiaging Physician',
    'Aesthetic Anti Aging Medical Doctor',
    'Aesthetic AntiAging Medical Doctor',
    'Aesthetic Antiaging Medical Doctor',
    'Aesthetic Anti Aging Specialist',
    'Aesthetic AntiAging Specialist',
    'Aesthetic Antiaging Specialist',
    'Aesthetic Anti Aging Doctor',
    'Aesthetic AntiAging Doctor',
    'Aesthetic Antiaging Doctor',
    'Aesthetic Anti Aging Surgeon',
    'Aesthetic AntiAging Surgeon',
    'Aesthetic Antiaging Surgeon',
    'Anti-Aging Aesthetic Physician',
    'Anti-Aging Aesthetic Practitioner',
    'Anti Aging Aesthetic Physician',
    'Anti Aging Aesthetic Practitioner',
    'Aesthetic & Anti Aging Medical Practitioner',
    'Aesthetic & AntiAging Medical Practitioner',
    'Aesthetic & Antiaging Medical Practitioner',
    'Aesthetic & Anti Aging Healthcare Practitioner',
    'Aesthetic & AntiAging Healthcare Practitioner',
    'Aesthetic & Antiaging Healthcare Practitioner',
    'Aesthetic Anti Aging Aesthetician',
    'Aesthetic & Anti Aging Medical Specialist',
    'Aesthetic & AntiAging Medical Specialist',
    'Aesthetic & Antiaging Medical Specialist',
    'Aesthetic & Anti-Aging Physician',
# Variations for common typos and case mistakes
    'Aesthetic & Anti-Aging Physician',
    'Aesthetic & AntiAging Physiican',
    'Aesthetic Anti-Aging Physican',
    'Aesthetic Anti Aging Physcian',
    'Aesthetic Anti Aging Pracitioner',
    'Aesthetic Anti-Aging Medical Doctor',
    'Aesthetic AntiAging Medical Dotor',
    'Aesthetic Anti Aging Speciallist',
    'Aesthetic Anti Aging Pracitioner',
    'Aesthetic Anti Aging Practicioner',
    'Aesthetic AntiAging Pracitioner',
    'Aesthetic Antiaging Medical Doctor',
    'Aesthetic AntiAging Surgeion',
    'Aesthetic Anti Aging Medcial Specalist',
    'Aesthetic Anti Aging Physican',
    'Aesthetic Anti-Aging Speciallist',
    'Aesthetic Anti Aging Healthcare Practicioner',
    'Aesthetic AntiAging Specilist',
    'Aesthetic Anti Aging Aesthetician',
    'Aesthetic AntiAging Surgeion',
    'Aesthetic Antiaging Doctor',
    'Aesthetic Antiaging Healthcare Specialist',
    'Aesthetic & Anti-Aging Practicioner',

    # values from data sources
    'Mesotherapist',
    'Mesapist',
    'Injectables',
    'Anti-Aging/Aesthetic Specialty',
    'Anti-AgingAesthetic Specialty',
    'Botox',
    'Body Contouring',
    'Aesthetic & Anti-Aging',
    'Aesthetics & Wellness Director',
    'Aesthetic & Medical Wellness Doctor',
    'GpAesthetic & Longevity Doctor',
    'Family MedecineAesthetic Anti-Aging Medecine',
    'Aesthetic & Wellness',
    'Aesthetic & Wellness Physicians At Monaco Wellness Tampa Fl',
    'Body Contouring Specialist',
    'body contouring specialist',
    'Aesthetic & Anti-aging Physcian',
}

# Define patterns for Anti-aging & Resident (these should NOT be changed)
aesthetic_antiaging_physician_exclusions = {
    'Anti-aging Physician',
    'Anti Aging Physician',
    'anti aging physician',
    'anti-aging physician',
    'Antiaging Physician',
    'AntiAging Physician',
    'antiaging physician',
    'antiAging physician',
    'anti-ageing physician',
    'anti ageeing physician',
    'Anti-Aging Dr.',
    'Anti Aging Dr.',
    'anti-aging dr',
    'anti aging dr',
    'Anti-Aging Specialist',
    'Anti Aging Specialist',
    'anti aging specialist',
    'anti-aging specialist',
    'Anti-aging Practitioner',
    'Anti Aging Practitioner',
    'anti-aging practitioner',
    'anti aging practitioner',
    'Anti-aging Physician Clinic',
    'Anti Aging Physician Clinic',
    'anti-aging physician clinic',
    'anti aging physician clinic',
    'Anti-aging MD',
    'Anti Aging MD',
    'anti-aging md',
    'anti aging md',
    'Anti-Aging Medical Doctor',
    'Anti Aging Medical Doctor',
    'anti-aging medical doctor',
    'anti aging medical doctor',
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
    'RN Injection & Body Contouring Specialist',
}

# Create a mask for aesthetics_antiaging_physician
mask_aesthetic_antiaging_physician = df['speciality'].str.contains('|'.join(aesthetic_antiaging_physician_variants), case=False, na=False, regex=True) | \
            df['speciality'].isin(aesthetic_antiaging_physician_exact_matches)
mask_aesthetic_antiaging_physician_exclusions = df['speciality'].isin(aesthetic_antiaging_physician_exclusions)

# Final mask: Select Aesthetic & Anti-aging Physician -related values
mask_aesthetic_antiaging_physician_final = mask_aesthetic_antiaging_physician & ~mask_aesthetic_antiaging_physician_exclusions

# Store the original values that will be replaced
original_aesthetics_antiaging_physician_values = df.loc[mask_aesthetic_antiaging_physician_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_aesthetic_antiaging_physician_final, 'speciality'] = 'Aesthetic & Anti-aging Physician'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Aesthetic & Anti-aging Physician", 'green'))
print(df.loc[mask_aesthetic_antiaging_physician_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_aesthetics_antiaging_physician_values = df.loc[mask_aesthetic_antiaging_physician_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Aesthetic & Anti-aging Physician", "cyan"))
for original_aesthetics_antiaging_physician_value in original_aesthetics_antiaging_physician_values:
    print(f"✅ {original_aesthetics_antiaging_physician_value} → Aesthetic & Anti-aging Physician")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Aesthetic & Anti-aging Physician:", 'red'))
print(grouped_aesthetics_antiaging_physician_values)

# Print summary
matched_count_aesthetics_antiaging_physician = mask_aesthetic_antiaging_physician_final.sum()

# Print results
print(colored(f"\nTotal values matched and changed (Stage 1) to Aesthetic & Anti-aging Physician: {matched_count_aesthetics_antiaging_physician}", 'red'))