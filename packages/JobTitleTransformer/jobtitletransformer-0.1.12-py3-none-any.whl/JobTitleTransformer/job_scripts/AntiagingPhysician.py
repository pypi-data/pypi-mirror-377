import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for anti_aging_physician related titles

anti_aging_physician_variants = [
    r"(?i)\bAnti-aging\s?Physician\b",
    r"(?i)\bAnti Aging\s?Physician\b",
    r"(?i)\bAnti-aging\s?Doctor\b",
    r"(?i)\bAnti Aging\s?Doctor\b",
    r"(?i)\bAnti-aging\s?Medical\s?Doctor\b",
    r"(?i)\bAnti Aging\s?Medical\s?Doctor\b",
    r"(?i)\bAnti-aging\s?Specialist\b",
    r"(?i)\bAnti Aging\s?Specialist\b",
    r"(?i)\bAnti-aging\s?Medicine\s?Physician\b",
    r"(?i)\bAnti Aging\s?Medicine\s?Physician\b",
    r"(?i)\bAnti-aging\s?Physician\s?Specialist\b",
    r"(?i)\bAnti Aging\s?Physician\s?Specialist\b",
    r"(?i)\bAnti-aging\s?Doctor\s?Specialist\b",
    r"(?i)\bAnti Aging\s?Doctor\s?Specialist\b",
    r"(?i)\bAnti-Aging Practitioner\b",
    r"(?i)\bAnti-Aging Physician\b",
    r"(?i)\bAge Management\b",
    r"(?i)\bLongevity Expert\b",
    r"(?i)\bMedecine Morphologique Et Anti Age\b",
    r"(?i)\bRj Medicina Estetica & Longevidade\b",
    r"(?i)\bEsthetics & Antiaging Medicine\b",
    r"(?i)\bAnti-Aging & Regenerative Medicine\b",
]

# Exact matches that should be updated
anti_aging_physician_exact_matches = {
    'Anti-aging Physician',
    'Anti-Aging Physician',
    'Anti-Aging physician',
    'Anti Aging Physician',
    'Anti-aging Doctor',
    'Anti-Aging Practitioner',
    'Anti-Aging Physician',
    'Anti Aging',
    'Anti-Aging',
    'Anti Aging Doctor',
    'Anti-aging Medical Doctor',
    'Anti Aging Medical Doctor',
    'Anti-aging Specialist',
    'Anti Aging Specialist',
    'Anti-aging Medicine Physician',
    'Anti Aging Medicine Physician',
    'Anti-aging Physician Specialist',
    'Anti Aging Physician Specialist',
    'Anti-aging Doctor Specialist',
    'Anti Aging Doctor Specialist',
    'Anti-aging Medicine Specialist',
    'Anti Aging Medicine Specialist',
    'Anti-aging Physician Expert',
    
    # Case-related errors
    'anti-aging physician',
    'anti aging physician',
    'ANTI-AGING PHYSICIAN',
    'ANTI AGING PHYSICIAN',
    'AnTi-AgiNg PhYsIcIaN',

    # Common misspellings
    'Anti-aging Physcian',
    'Anti-aging Phyisician',
    'Anti-agng Physician',
    'Anti Agng Physician',
    'Antiaging Physician',
    'Anti-Aging Phyisician',
    'AntiAging Physician',
    'Anti-Aging Physcian',
    'Anti-Aging Physicians',
    'Ant-aging Physician',
    'Anti-agin Physician',

    # Spanish-related exclusions
    'Médico Anti-envejecimiento',
    'Especialista en Anti-envejecimiento',
    'Doctor en Anti-envejecimiento',
    'Médico Anti-Aging',
    'Especialista Anti-Aging',
    'Doctor Anti-Aging',
    'Médico Anti-aging',
    'Especialista en Medicina Anti-envejecimiento',
    'Especialista en Medicina Anti-Aging',
    
    # Anti-Aging Practitioner
    "Anti-aging Practicioner",
    "Anti-aging Practitoner",
    "Anti-Aging Practicioner",
    "Anti-Aging Pracitioner",
    "Anti-aging Prctitioner",
    "AntiAging Practitioner",
    "Anti-Aging Practtioner",
    "Anti-aging Practitiner",
    "Anti-Aging Practicioners",
    "Anti-agng Practitioner",
    "Anti-agin Practitioner",
    'Anti-Aging Physician',
    'Anti Aging Medicine',
    'Antiaging',
    'Anti-Aging Skincare',
    'Medicine -Primary-Holistic-Antiaging',
    'Anti- Aging Medicine',
    'Anti-Ageing',
    'Anti Aging Dan Stem Cell',
    'Anti-Ageing Medicine',
    'Anti-AgingFunctional Med',
    'Antiaging Practitioner',
    'Antibaging doctor',
    'Anti-Ageing Physician',
    'ANTIAGING DOCTOR',
}

# Define patterns for  & Resident & Professor (these should NOT be changed)
anti_aging_physician_exclusions = {
    'Aesthetic & Anti-aging Physician',
    'Aesthetic & Anti Aging Physician',
    'Aesthetic & AntiAging Physician',
    'Aesthetic & Antiaging Physician',
    'Aesthetic & Anti Aging Practitioner',
    'Aesthetic & AntiAging Practitioner',
    'Aesthetic & Antiaging Practitioner',
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
    'Resident',
    'resident',
    'student',
    'Trainee',
    'Resident Doctor',
    'Resident Physician',
    'Intern', 'intern',
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
    'Aesthetic&Anti-Aging Physcian',
    'Anti Aging Center Manager',
    'Nurse Antiaging',
    'Plastic Surgeon - Antiaging Practicioner',
    'Antiaging Nutrition',
    'Dermatologist & Anti-Aging Specialist',
    'Anti-Aging & Sports Medicine',
    'Gynecologist & Anti Aging Physician',
    }

# Create a mask for Anti-aging Physician
mask_anti_aging_physician = df['speciality'].str.contains('|'.join(anti_aging_physician_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(anti_aging_physician_exact_matches)
mask_anti_aging_physician_exclusions = df['speciality'].isin(anti_aging_physician_exclusions)

# Final mask: Select Anti-aging Physician
mask_anti_aging_physician_final = mask_anti_aging_physician & ~mask_anti_aging_physician_exclusions

# Store the original values that will be replaced
original_anti_aging_physician_values = df.loc[mask_anti_aging_physician_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_anti_aging_physician_final, 'speciality'] = 'Anti-aging Physician'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Anti-aging Physician", 'green'))
print(df.loc[mask_anti_aging_physician_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_anti_aging_physician_values = df.loc[mask_anti_aging_physician_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Anti-aging Physician", "cyan"))
for original_anti_aging_physician_value in original_anti_aging_physician_values:
    print(f"✅ {original_anti_aging_physician_value} → Anti-aging Physician")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Anti-aging Physician:", 'red'))
print(grouped_anti_aging_physician_values)

# Print summary
matched_count_anti_aging_physician = mask_anti_aging_physician_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Anti-aging Physician: "
        f"{matched_count_anti_aging_physician}",
        'red'))