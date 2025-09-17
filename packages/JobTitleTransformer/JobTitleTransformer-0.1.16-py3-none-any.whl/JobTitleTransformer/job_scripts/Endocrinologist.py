import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Endocrinologist related titles

endocrinologist_variants = [
    r"(?i)\bendocrinologist\b",
    r"(?i)\bendocrinologists\b",
    r"(?i)\bendocrinologist\s?doctor\b",
    r"(?i)\bendocrinology\s?specialist\b",
    r"(?i)\bendocrinologist\s?specialist\b",
    r"(?i)\bboard\s?certified\s?endocrinologist\b",
    r"(?i)\bdoctor\s?of\s?endocrinology\b",
    r"(?i)\bdoctor\s?endocrinologist\b",
    r"(?i)\bendocrinologist\s?physician\b",
    r"(?i)\bendocrinologist\s?md\b",
    r"(?i)\bendocrinologist\s?mds\b",
    r"(?i)\bendocrinologist\s?consultant\b",
    r"(?i)\bendocrinologist\s?expert\b",
    r"(?i)\bendocrinologist\s?doctor\b",
    r"(?i)\bendocrinologist\s?physician\s?specialist\b",
    # Spanish variants
    r"(?i)\bendocrinólogo\b",
    r"(?i)\bendocrinóloga\b",
    r"(?i)\bendocrinólogos\b",
    r"(?i)\bendocrinólogas\b",
    r"(?i)\bespecialista\s?en\s?endocrinología\b",
    r"(?i)\bdoctor\s?en\s?endocrinología\b",
    # Misspellings
    r"(?i)\bendocrinolgist\b",
    r"(?i)\bendocrinologiest\b",
    r"(?i)\bendocrinlogist\b",
    r"(?i)\bendocrinologist\s?doctor\b",
    r"(?i)\bendocrinogist\b",
    r"(?i)\bendoocrinologist\b",
    r"(?i)\bendocrinolgist\b",
    r"(?i)\bendocrinologist\s?md\b",
    # Case-related errors
    r"(?i)\bendocrinologist\b",
    r"(?i)\bENDOCRINOLOGIST\b",
    r"(?i)\bEndocrinologist\b",
    r"(?i)\bendocrinologist\b",
    # Other Possible Variations
    r"(?i)\bboard\s?certified\s?endocrinologist\b",
    r"(?i)\bendocrinology\s?expert\b",
    r"(?i)\bendocrinologist\s?specialist\b",
    r"(?i)\bendocrinology\s?doctor\b",
    r"(?i)\bendocrinologist\s?consultant\b",
    r"(?i)\bendocrinology\s?practitioner\b",
    r"(?i)\bendocrinologist\s?physician\b",
    r"(?i)\bendocrine\s?specialist\b",
    r"(?i)\bendocrinologist\s?expert\b",
    r"(?i)\bMedico Endocrinologista\b",
    r"(?i)Endocrinologista",
    r"(?i)Endocrinoligista",
    r"(?i)\bHrt Pellet Therapy\b",
    r"(?i)\bEndocrino\b",
    r"(?i)\bHormone Optimization Coordinator\b",
]

# Exact matches that should be updated
endocrinologist_exact_matches = {
    "Endocrinologist",
    "Endocrinologists",
    "Endocrinologist Doctor",
    "Endocrinology Specialist",
    "Endocrinologist Specialist",
    "Board Certified Endocrinologist",
    "Doctor of Endocrinology",
    "Doctor Endocrinologist",
    "Endocrinologist Physician",
    "Endocrinologist MD",
    "Endocrinologist MDs",
    "Endocrinologist Consultant",
    "Endocrinologist Expert",
    "Endocrinologist Physician Specialist",
    "Endocrinólogo",
    "Endocrinóloga",
    "Endocrinólogos",
    "Endocrinólogas",
    "Especialista en Endocrinología",
    "Doctor en Endocrinología",
    "Endocrinolgist",
    "Endocrinologiest",
    "Endocrinlogist",
    "Endocrinogist",
    "Endoocrinologist",
    "ENDOCRINOLOGIST",
    "endocrinologist",
    "Endocrinology Expert",
    "Endocrinology Doctor",
    "Endocrinology Practitioner",
    "Endocrine Specialist",
    'Director Obesity Chair',
}

# Define patterns (these should NOT be changed)
endocrinologist_exclusions = {
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
}

# Create a mask for Endocrinologist
mask_endocrinologist = df['speciality'].str.contains('|'.join(endocrinologist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(endocrinologist_exact_matches)
mask_endocrinologist_exclusions = df['speciality'].isin(endocrinologist_exclusions)

# Final mask: Select Endocrinologist
mask_endocrinologist_final = mask_endocrinologist & ~mask_endocrinologist_exclusions

# Store the original values that will be replaced
original_endocrinologist_values = df.loc[mask_endocrinologist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_endocrinologist_final, 'speciality'] = 'Endocrinologist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Endocrinologist", 'green'))
print(df.loc[mask_endocrinologist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_endocrinologist_values = df.loc[mask_endocrinologist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Endocrinologist", "cyan"))
for original_endocrinologist_value in original_endocrinologist_values:
    print(f"✅ {original_endocrinologist_value} → Endocrinologist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Endocrinologist:", 'red'))
print(grouped_endocrinologist_values)

# Print summary
matched_count_endocrinologist = mask_endocrinologist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Endocrinologist: "
        f"{matched_count_endocrinologist}",
        'red'))