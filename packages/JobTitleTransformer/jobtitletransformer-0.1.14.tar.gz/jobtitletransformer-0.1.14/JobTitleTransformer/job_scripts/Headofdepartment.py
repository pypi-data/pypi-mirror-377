import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Head of department related titles

head_of_department_variants = [
    r"(?i)\bHead\s?of\s?Department\b",  # Standard title

    # Common misspellings and case errors
    r"(?i)\bHead\s?of\s?Depatment\b",
    r"(?i)\bHead\s?of\s?Deparment\b",
    r"(?i)\bHead\s?of\s?Departement\b",
    r"(?i)\bHOD\b",
    r"(?i)\bHead Of Service\b",
    r"(?i)\bClinical Director\b",
    r"(?i)\bChief Medical Officer\b",
    r"(?i)\bMedical Cio\b",
    r"(?i)\bHead Of Inject\b",
    r"(?i)\bHead Of Surgical Operation\b",
    r"(?i)\bHead Of Skin Solutions\b",
    r"(?i)\bHead Of Clinical Facilitation & Digital Deployment\b",

    # Spanish variants
    r"(?i)\bJefe\s?de\s?Departamento\b",
    r"(?i)\bDirector\s?de\s?Departamento\b",

    # Other possible variations
    r"(?i)\bDepartment\s?Head\b",
    r"(?i)\bChief\s?of\s?Department\b",
    r"(?i)\bHead\s?of\s?Division\b",
    r"(?i)\bDirector\s?of\s?Department\b",
    r"(?i)\bHead Of Qc Qp\b",
    r"(?i)\bHead Of Department Of Plastic Surgery\b",
    r"(?i)\bHead Of The Department Of Facial & Plastic Surgery\b",
    r"(?i)\bHead Of Department\b",
    r"(?i)\bHead Of Service\b",
    r"(?i)\bHead Of Surgical Operation\b",
    r"(?i)\bHead Of Qc Qp\b",
    r"(?i)\bDirctor\b",
    r"(?i)\bHead Of Service Department\b",
    r"(?i)\bHead Of Skin Solutions\b",
    r"(?i)\bDiretor\b",
    r"(?i)\bClinical Director\b",
    r"(?i)\bHead Of Department Of Plastic Surgery\b",
    r"(?i)\bSupervisor Molbio\b",
    r"(?i)\bField Services Supervisor\b",
    r"(?i)\bNurse Supervisor\b",
    r"(?i)\bSenior Clinical Director\b",
    r"(?i)\bHead Of Clinical Facilitation & Digital Deployment\b",
    r"(?i)\bGrassroots Supervisor\b",
    r"(?i)\bHead Of The Department Of Facial & Plastic Surgery\b",
    r"(?i)\bClinical Director Of Nursing Neuroscience Unit\b",
    r"(?i)\bHead Of Inject\b",
    r"(?i)\bField Supervisor\b",
    r"(?i)\bDivisional Clinical Director\b",
    r"(?i)\bManagement Supervisor\b",
    r"(?i)\bAnatomic Pathology Supervisor\b",
    r"(?i)\bAesthetics Clinical Director\b",
    r"(?i)\bDirector Of Department\b",
    r"(?i)\bHead Of Surgery Department\b",
    r"(?i)\bDir Of Administration\b",
]

# Exact matches that should be updated
head_of_department_exact_matches = {
    "Head of Department",
    "Head of Depatment",
    "Head of Deparment",
    "Head of Departement",
    "HOD",
    # Spanish variants
    "Jefe de Departamento",
    "Director de Departamento",
    # Other possible variations
    "Department Head",
    "Chief of Department",
    "Head of Division",
    "Director of Department",
    'Director',
    "Diretor",
    "Dirctor",
    "Directer",
    "Directar",
    "Directr",
    "Drector",
    "Dierctor",
    "Dorector",
    "Driector",
    'Supervisor',
    'supervisor',
    'Ami Director',
    'Directornuclear Medicine',
    'Technical Director',
    'Director Of Information Department',
    'Directors PaAdministrator',
    'Director Medico',
    'Clinical Transformation Director',
    'Head Of Im & T',
    'Chief Clinical Officer Digital Health',
    'Director Of Labor & Delivery',
    'Head Of Beauty Department At Largest Pharm Retailer In Caucasus',
    'DirectorProvider',
    'Director of Training',
    'Director of non-surgical serives',
    'Cosmetic Director',
    'Aesthetic Director',
    'Dir',
    'Medcal Director',
    'Director Of Physician Services',
    'Administrator Of Physician Services',
    'Assistant Deputy Minister Physician & Provider Services',
    'Assistant Physician Director Primary Care',
    'Clincial Physician Executive',
    'Physician Executive',
    'Physician Executive For Integrated Regina Health',
    'Physician Executive Integrated Northern Health',
    'Regional Physician Executive',
    'Supervisor Dermatology Services Puyallup',
    'Supervisor Theatrical Cosmetology',
    'Supervisor V4650 & Practice Physician',
    'System Physician Executive',
    'Chief Of Clinical Development',
    'DOS',
    'Director of surgical services',
}

# Define patterns (these should NOT be changed)
head_of_department_exclusions = {
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
    'Oral Maxillofacial Surgeon Clinical Director',
}

# Create a mask for Head of department
mask_head_of_department = df['speciality'].str.contains('|'.join(head_of_department_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(head_of_department_exact_matches)
mask_head_of_department_exclusions = df['speciality'].isin(head_of_department_exclusions)

# Final mask: Select Head of department
mask_head_of_department_final = mask_head_of_department & ~mask_head_of_department_exclusions

# Store the original values that will be replaced
original_head_of_department_values = df.loc[mask_head_of_department_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_head_of_department_final, 'speciality'] = 'Head of department'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Head of department", 'green'))
print(df.loc[mask_head_of_department_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_head_of_department_values = df.loc[mask_head_of_department_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Head of department", "cyan"))
for original_head_of_department_value in original_head_of_department_values:
    print(f"✅ {original_head_of_department_value} → Head of department")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Head of department:", 'red'))
print(grouped_head_of_department_values)

# Print summary
matched_count_head_of_department = mask_head_of_department_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Head of department: "
        f"{matched_count_head_of_department}",
        'red'))