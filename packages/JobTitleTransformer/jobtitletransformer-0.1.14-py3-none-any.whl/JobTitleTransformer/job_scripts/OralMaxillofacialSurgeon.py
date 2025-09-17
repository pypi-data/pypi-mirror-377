import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Oral and Maxillofacial Surgeon related titles

oral_maxillofacial_variants = [
    # Standard Titles & Abbreviations
    r"(?i)\bOral\s?and\s?Maxillofacial\s?Surgeon\b",
    r"(?i)\bOral\s?&\s?Maxillofacial\s?Surgeon\b",
    r"(?i)\bOMFS\b",

    # Misspellings & Typographical Errors
    r"(?i)\bOral\s?and\s?Maxilofacial\s?Surgeon\b",
    r"(?i)\bOral\s?and\s?Maxillafacial\s?Surgeon\b",
    r"(?i)\bOral\s?and\s?Maxilofacil\s?Surgeon\b",
    r"(?i)\bOral\s?and\s?Maxilofascial\s?Surgeon\b",
    r"(?i)\bOral\s?and\s?Maxilofasial\s?Surgeon\b",
    r"(?i)\bOral\s?Maxillofacial\s?Surgeon\b",
    r"(?i)\bOral\s?Maxilofacial\s?Surgeon\b",
    r"(?i)\bOral\s?Maxilofacil\s?Surgeon\b",
    r"(?i)\bOral\s?Maxilofascial\s?Surgeon\b",
    r"(?i)\bOral\s?Maxilofasial\s?Surgeon\b",
    r"(?i)\bOral\s?&\s?Maxilofacial\s?Surgeon\b",

    # Case Variations
    r"(?i)\boral and maxillofacial surgeon\b",
    r"(?i)\bOral And Maxillofacial Surgeon\b",
    r"(?i)\bORAL AND MAXILLOFACIAL SURGEON\b",
    r"(?i)\bOrAl aNd MaXiLloFaCiaL SuRgEoN\b",

    # Spanish Variants
    r"(?i)\bCirujano\s?Oral\s?y\s?Maxilofacial\b",
    r"(?i)\bCirugía\s?Oral\s?y\s?Maxilofacial\b",
    r"(?i)\bEspecialista\s?en\s?Cirugía\s?Oral\s?y\s?Maxilofacial\b",
    r"(?i)\bCirujano\s?Oral\s?y\s?Facial\b",

    # Other Possible Variations (Including Doctor forms, Specialist forms)
    r"(?i)\bOral\s?and\s?Maxillofacial\s?Physician\b",
    r"(?i)\bOral\s?and\s?Maxillofacial\s?Specialist\b",
    r"(?i)\bOral\s?Surgeon\b",
    r"(?i)\bOral & Maxillofacial Surgery\b",
    r"(?i)\bHarmonizacao Orofacial\b",
    r"(?i)\bOmf Surgeon\b",
    r"(?i)\bOrofacial Harmonization\b",
    r"(?i)\bOral Surgeon & Medical Aesthetic Doctor\b",
    r"(?i)\bOral Surgery\b",
]

# Exact matches that should be updated
oral_maxillofacial_exact_matches = {
    "Oral and Maxillofacial Surgeon",
    "Oral & Maxillofacial Surgeon",
    "OMFS",
    "Oral and Maxilofacial Surgeon",
    "Oral and Maxillafacial Surgeon",
    "Oral and Maxilofacil Surgeon",
    "Oral and Maxilofascial Surgeon",
    "Oral and Maxilofasial Surgeon",
    "Oral Maxillofacial Surgeon",
    "Oral Maxilofacial Surgeon",
    "Oral Maxilofacil Surgeon",
    "Oral Maxilofascial Surgeon",
    "Oral Maxilofasial Surgeon",
    "Oral & Maxilofacial Surgeon",
    "Cirujano Oral y Maxilofacial",
    "Cirugía Oral y Maxilofacial",
    "Especialista en Cirugía Oral y Maxilofacial",
    "Cirujano Oral y Facial",
    "Oral and Maxillofacial Physician",
    "Oral and Maxillofacial Specialist",
    "Oral Surgeon",
    'Oral & Maxillofacial Surgery',
    'Orl',
    'Oral & Mixilo-Facial',
}

# # Define patterns (these should NOT be changed)
# oral_maxillofacial_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

oral_maxillofacial_exclusions = {
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

# Create a mask for Oral and Maxillofacial Surgeon
mask_oral_maxillofacial = df['speciality'].str.contains('|'.join(oral_maxillofacial_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(oral_maxillofacial_exact_matches)

# mask_oral_maxillofacial_exclusions = df['speciality'].str.contains(oral_maxillofacial_exclusions, case=False, na=False, regex=True)
mask_oral_maxillofacial_exclusions = df['speciality'].isin(oral_maxillofacial_exclusions)

# Final mask: Select Oral and Maxillofacial Surgeon
mask_oral_maxillofacial_final = mask_oral_maxillofacial & ~mask_oral_maxillofacial_exclusions

# Store the original values that will be replaced
original_oral_maxillofacial_values = df.loc[mask_oral_maxillofacial_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_oral_maxillofacial_final, 'speciality'] = 'Oral and Maxillofacial Surgeon'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Oral and Maxillofacial Surgeon", 'green'))
print(df.loc[mask_oral_maxillofacial_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_oral_maxillofacial_values = df.loc[mask_oral_maxillofacial_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Oral and Maxillofacial Surgeon", "cyan"))
for original_oral_maxillofacial_value in original_oral_maxillofacial_values:
    print(f"✅ {original_oral_maxillofacial_value} → Oral and Maxillofacial Surgeon")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Oral and Maxillofacial Surgeon:", 'red'))
print(grouped_oral_maxillofacial_values)

# Print summary
matched_count_oral_maxillofacial = mask_oral_maxillofacial_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Oral and Maxillofacial Surgeon: "
        f"{matched_count_oral_maxillofacial}",
        'red'))