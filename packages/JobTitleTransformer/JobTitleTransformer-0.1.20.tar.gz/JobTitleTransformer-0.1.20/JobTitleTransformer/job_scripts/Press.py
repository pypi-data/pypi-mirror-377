import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Press related titles

press_variants = [
    # Standard Titles & Variants
    r"(?i)\bPress\b",
    r"(?i)\bMedia\b",
    r"(?i)\bPublic Relations\b",
    r"(?i)\bPR\b",
    r"(?i)\bJournalist\b",

    # Misspellings & Typographical Errors
    r"(?i)\bPess\b",
    r"(?i)\bPrees\b",
    r"(?i)\bPrss\b",
    r"(?i)\bPresss\b",

    # Case Variations
    r"(?i)\bpress\b",
    r"(?i)\bPRESS\b",
    r"(?i)\bPrEsS\b",

    # Spanish Variants
    r"(?i)\bPrensa\b",
    r"(?i)\bRelaciones Públicas\b",
    r"(?i)\bComunicados de Prensa\b",
    r"(?i)\bMedios de Comunicación\b",
    r"(?i)\bDepartamento de Prensa\b",

    # Other Possible Variations
    r"(?i)\bPublic Relations Manager\b",
    r"(?i)\bMedia Relations\b",
    r"(?i)\bMedia Relations Specialist\b",
    r"(?i)\bPress Officer\b",
    r"(?i)\bCommunications\b",
    r"(?i)\bDirectrice De La Rdaction\b",
    r"(?i)\bAssistant Camera Operator\b",
    r"(?i)\bVideo Ad\b",
    r"(?i)\bEditor\b",
    r"(?i)\bFeatures Editor\b",
    r"(?i)\bGiornalista\b",
    r"(?i)\bAuthor\b",
    r"(?i)\bJournaliste\b",
    r"(?i)\bTv Production\b",
]

# Exact matches that should be updated
press_exact_matches = {
    "Press",
    "Media",
    "Public Relations",
    "PR",
    "Pess",
    "Prees",
    "Prss",
    "Presss",
    "Prensa",
    "Relaciones Públicas",
    "Comunicados de Prensa",
    "Medios de Comunicación",
    "Departamento de Prensa",
    "Public Relations Manager",
    "PR Specialist",
    "Media Relations",
    "Media Relations Specialist",
    "Press Officer",
    "PressMedia",
    "PressMedia",
    'Communications',
}

# # Define patterns (these should NOT be changed)
press_exclusions = r'\b(?:Social Media)|(?:Marketing)\b'

# press_exclusions = {
#     'Resident', 'resident', 'student', 'Trainee', 'Resident Doctor', 'Resident ooPhysician',
#     'Intern', 'intern', 'Medical Intern', 'Fellow', 'fellow', 'Clinical Fellow', 'Medical Student',
#     'Clinical Trainee', 'Trainee Doctor', 'Trainee Physician', 'Junior Doctor', 'Postgraduate Trainee',
#     'Aesthetic Fellow', 'Aesthetic Trainee', 'Aesthetic Medicine Fellow', 'Aesthetic Resident'
# }

# Create a mask for Press
mask_press = df['speciality'].str.contains('|'.join(press_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(press_exact_matches)

mask_press_exclusions = df['speciality'].str.contains(press_exclusions, case=False, na=False, regex=True)
# mask_press_exclusions = df['speciality'].isin(press_exclusions)

# Final mask: Select Press
mask_press_final = mask_press & ~mask_press_exclusions

# Store the original values that will be replaced
original_press_values = df.loc[mask_press_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_press_final, 'speciality'] = 'Press'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Press", 'green'))
print(df.loc[mask_press_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_press_values = df.loc[mask_press_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Press", "cyan"))
for original_press_value in original_press_values:
    print(f"✅ {original_press_value} → Press")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Press:", 'red'))
print(grouped_press_values)

# Print summary
matched_count_press = mask_press_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Press: "
        f"{matched_count_press}",
        'red'))