import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for anatomist related titles
anatomist_variants = [
    r"(?i)\bAnatomist\b",
    r"(?i)\bAnatomy Specialist\b",
    r"(?i)\bAnatomy Expert\b",
    r"(?i)\bAnatomy Doctor\b",
    r"(?i)\bAnatomical Scientist\b",
    r"(?i)\bAnatomic Pathologist\b",
    r"(?i)\bAnatomy Researcher\b",
    r"(?i)\bAnatomy Lecturer\b",
    r"(?i)\bProfessor of Anatomy\b",
    r"(?i)\bAnatomy\b",
    r"(?i)\bAnatomiapatologica\b",
    r"(?i)\bAnatomiapatologica\b",
]

# Exact matches that should be updated
anatomist_exact_matches = {
    'Anatomist',
    'Anatomy Specialist',
    'Anatomy Expert',
    'Anatomy Doctor',
    'Anatomical Scientist',
    'Anatomic Pathologist',
    'Anatomy Researcher',
    'Anatomy Lecturer',
    'Anatomy Consultant',
    'Medical Anatomist',
    'Clinical Anatomist',
    'Human Anatomist',
    'Surgical Anatomist',
    'Pathological Anatomist',

    # Case-related errors
    'anatomist',
    'ANATOMIST',
    'anAtOmIsT',
    'AnAToMIST',
    'aNATOMIST',
    'ANATOMy Specialist',

    # Spanish-related exclusions
    'Anatomista',
    'Especialista en Anatomía',
    'Médico Anatomista',
    'Científico Anatómico',
    'Patólogo Anatómico',
    'Investigador en Anatomía',
    'Docente de Anatomía',
    'Profesor de Anatomía',
    'Anatomía Clínica',
    'Anatomista Médico',
    'Experto en Anatomía',

}

# Define patterns for  & Resident & Professor (these should NOT be changed)
anatomist_exclusions = {
    'Plastic Surgeon & Anatomist',
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

# Create a mask for Anatomist
mask_anatomist = df['speciality'].str.contains('|'.join(anatomist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(anatomist_exact_matches)
mask_anatomist_exclusions = df['speciality'].isin(anatomist_exclusions)

# Final mask: Select Anatomist
mask_anatomist_final = mask_anatomist & ~mask_anatomist_exclusions

# Store the original values that will be replaced
original_anatomist_values = df.loc[mask_anatomist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_anatomist_final, 'speciality'] = 'Anatomist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Anatomist", 'green'))
print(df.loc[mask_anatomist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_anatomist_values = df.loc[mask_anatomist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Anatomist", "cyan"))
for original_anatomist_value in original_anatomist_values:
    print(f"✅ {original_anatomist_value} → Anatomist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Anatomist:", 'red'))
print(grouped_anatomist_values)

# Print summary
matched_count_anatomist = mask_anatomist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Anatomist: "
        f"{matched_count_anatomist}",
        'red'))