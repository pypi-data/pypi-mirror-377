import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for alternative_medicine related titles
alternative_medicine_variants = [
    r"(?i)\bAlternative\sMedicine\sPhysician\b",
    r"(?i)\bAlternative\sHealth\sPhysician\b",
    r"(?i)\bHolistic\sPhysician\b",
    r"(?i)\bNatural\sMedicine\sPhysician\b",
    r"(?i)\bIntegrative\sMedicine\sPhysician\b",
    r"(?i)\bComplementary\sMedicine\sPhysician\b",
    r"(?i)\bAlternative\sMedicine\b",
    r"(?i)\bAlternative Medicine\b",
    r"(?i)\bAlternative Medcine\b",
    r"(?i)\bAlternetive Medicine\b",
    r"(?i)\bAlternative Medecine\b",
    r"(?i)\bAlternativ Medicine\b",
    r"(?i)\bAlternitive Medicine\b",
    r"(?i)\bAltrnative Medicine\b",
    r"(?i)\bAlterantive Medicine\b",
    r"(?i)\bAltrenative Medicine\b",
    r"(?i)\bAlternative Medcin\b",
    r"(?i)\bAlternatuve Medicine\b",
    r"(?i)\bAlternetive Medecine\b",
    r"(?i)\bAlterntive Medicine\b",
    r"(?i)\bHeilpraktiker\b",
    r"(?i)\bHeilpraktikerin\b",
    r"(?i)\bHeilpraktikerin\b",
    r"(?i)\bIntegrative Medicine\b",
    r"(?i)\bIridologist\b",
]

# Exact matches that should be updated
alternative_medicine_exact_matches = {
    'Alternative Medicine Physician',
    'Alternative Medicine Doctor',
    'Holistic Medicine Physician',
    'Integrative Medicine Physician',
    'Natural Medicine Physician',
    'Complementary Medicine Physician',
    'Holistic Health Physician',
    'Alternative Health Physician',
    'Alternative Medicine Specialist',
    'Holistic Medicine Doctor',
    'Integrative Medicine Doctor',
    'Natural Medicine Doctor',
    'Complementary Medicine Doctor',
    'Alternative Medicine Expert',
    'Holistic Health Doctor',
    'Natural Health Physician',
    'Natural Medicine Specialist',
    'Integrative Health Physician',
    'Integrative Medicine Specialist',
    'Alternative Medicine Practitioner',
    'Holistic Medicine Practitioner',
    'Integrative Medicine Practitioner',
    'Natural Medicine Practitioner',
    'Complementary Medicine Practitioner',
    'Alternative Medicine Practitioner Expert',
    'Alternative Medicine Doctor Expert',
    'Holistic Medicine Practitioner Expert',
    'Integrative Medicine Practitioner Expert',
    'Natural Medicine Practitioner Expert',
    'Complementary Medicine Practitioner Expert',
    'Alternative Medicine',

    # Spanish Titles:
    'Médico De Medicina Alternativa',
    'Médico En Medicina Alternativa',
    'Especialista En Medicina Alternativa',

    # Spanish: Alternative Medicine Physician
    'Médico De Salud Holística',
    'Médico En Medicina Holística',
    'Especialista En Medicina Holística',

    # Spanish: Holistic Medicine Physician
    'Médico De Medicina Natural',
    'Médico En Medicina Natural',
    'Especialista En Medicina Natural',

    # Spanish: Natural Medicine Physician
    'Médico De Medicina Integrativa',
    'Médico En Medicina Integrativa',
    'Especialista En Medicina Integrativa',

    # Spanish: Integrative Medicine Physician
    'Médico De Medicina Complementaria',
    'Médico En Medicina Complementaria',
    'Especialista En Medicina Complementaria',

    # Spanish: Complementary Medicine Physician

    # Variations for misspellings and case mistakes for Alternative Medicine Physician and related titles
    'Alternive Medicine Physician',
    'Alternative Medcine Physician',
    'Alternative Medecine Physician',
    'Alternative Medcine Doctor',
    'Alterntive Medicine Physician',
    'Alternitive Medicine Physician',
    'Altrernative Medicine Physician',
    'Alternative Mmedicine Physician',
    'Alternativ Medicine Physician',
    'Alternativ Medcine Physician',
    'Alternative Mdicine Physician',
    'Alterntive Medicine Dr.',
    'Alternative Medcine Dr.',
    'Alternative Medicine Docotr',
    'Altenative Medicine Physician',
    'Alterantive Medicine Physcian',
    'Alternative Medicne Physician',
    'Alternative Meidcine Physician',

    # Case mistakes:
    'Alternative medicine physician',
    'alternative medicine physician',
    'ALTERNATIVE MEDICINE PHYSICIAN',
    'Alternative Medicine physician',
    'alternative Medicine Physician',
    'alternative medicine Physician',
    'alternative Medcine Physician',
    'Alternative Medicine PHYSICIAN',
    'alternative Medicine Physician Expert',

    # Common Misspellings
    'Alternetive Medicine Physician',
    'Alternative Medicin Physician',
    'Alternative Medcine Doctor',
    'Alternitive Medcine Physician',
    'Alternetive Medicine Doc',
    'Alternative Meidicine Physician',
    'Alternative Medicne Physcian',
    'Alternative Medcine Physican',
    'Alterantive Medicine Doctor',
    'Alternative Medicine Pracitioner',
    'Alternative Medicen Physician',
    'Altrernative Medicine Doc',
    'Alternive Medcine Doctor',
    'Alternative Medecine Doctor',
    'Alteernative Medicine Physician',
    'Alternative Medicine',
    'Alternative Medcine',
    'Alternetive Medicine',
    'Alternative Medecine',
    'Alternativ Medicine',
    'Alternitive Medicine',
    'Altrnative Medicine',
    'Alterantive Medicine',
    'Altrenative Medicine',
    'Alternative Medcin',
    'Alternatuve Medicine',
    'Alternetive Medecine',
    'Alterntive Medicine',
    
    # Case-related errors for Alternative Medicine Physician:
    'alternative medicine Physician',
    'Alternative medcine physician',
    'Alternative medicine PHYSICIAN',
    'alternative Medicine Physician',
    'Alternative Medicine PHYsician',
    'alternative Medicine PHYsician',
    'ALTERNATIVE MEDICINE physician',
    'Alternative Medicne Physician',
    'alternative Medicine Physican',
    'Alternative medicine Phycian',
    'altnernative medicine physician',
    'Alternative medicne PHYSICIAN',
    'alternative medicine',
    'ALTERNATIVE MEDICINE',
    'Alternative MEDICINE',
    'aLTERNATIVE mEDICINE',
    'aLTERnAtIVE medicine',
    'alTeRnAtIvE mEdIcInE',

    # Spanish Variants for Alternative Medicine Physician titles:
    'Médico De Medicina Alternativa',
    'Médico En Medicina Alternativa',
    'Especialista En Medicina Alternativa',
    'Médico De Medicina Natural',
    'Médico En Medicina Natural',
    'Especialista En Medicina Natural',
    'Médico De Medicina Integrativa',
    'Médico En Medicina Integrativa',
    'Especialista En Medicina Integrativa',
    'Médico De Medicina Complementaria',
    'Médico En Medicina Complementaria',
    'Especialista En Medicina Complementaria',
    'Médico Holístico',
    'Médico De Salud Holística',
    'Médico De Medicina Complementaria',
    'Médico De Medicina Preventiva',
    'Médico Integrativo',
    'Especialista En Medicina Holística',
    'Medicina Alternativa',
    'Médico de Medicina Alternativa',
    'Médico Alternativo',
    'Especialista en Medicina Alternativa',
    'Médico en Medicina Alternativa',
    'Medicina Natural',
    'Especialista en Medicina Natural',
    'Médico Natural',
    'Salud Alternativa',
    'Tratamientos Alternativos',
    'Medicina Complementaria',
    'Medicina Holística',
    'Medicina Integrativa',

    # Doctor Forms:
    'Alternative Medicine Doctor',
    'Holistic Medicine Doctor',
    'Integrative Medicine Doctor',
    'Natural Medicine Doctor',
    'Complementary Medicine Doctor',
    'Holistic Health Doctor',
    'Alternative Health Doctor',
    'Doctor of Integrative Medicine',
    'Doctor of Holistic Medicine',
    'Doctor of Alternative Medicine',
    'Doctor of Natural Medicine',
    'Doctor of Complementary Medicine',

    # Specialist Forms:
    'Alternative Medicine Specialist',
    'Holistic Medicine Specialist',
    'Natural Medicine Specialist',
    'Integrative Medicine Specialist',
    'Complementary Medicine Specialist',
    'Alternative Medicine Expert',
    'Holistic Medicine Expert',
    'Integrative Medicine Expert',
    'Natural Medicine Expert',
    'Complementary Medicine Expert',
    'Alternative Medicine Consultant',
    'Holistic Medicine Consultant',
    'Integrative Medicine Consultant',
    'Natural Medicine Consultant',
    'Complementary Medicine Consultant',
    'Homeopathic Physician',
    'Functional Medicine',
    'Chiropractic Physician',
    'Functional',
}

# Define patterns for  & Resident & Professor (these should NOT be changed)
alternative_medicine_exclusions = {
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

# Create a mask for Alternative Medicine Physician
mask_alternative_medicine = df['speciality'].str.contains('|'.join(alternative_medicine_variants), case = False,
                                                         na = False, regex = True) | \
                           df['speciality'].isin(alternative_medicine_exact_matches)
mask_alternative_medicine_exclusions = df['speciality'].isin(alternative_medicine_exclusions)

# Final mask: Select Alternative Medicine Physician
mask_alternative_medicine_final = mask_alternative_medicine & ~mask_alternative_medicine_exclusions

# Store the original values that will be replaced
original_alternative_medicine_values = df.loc[mask_alternative_medicine_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_alternative_medicine_final, 'speciality'] = 'Alternative Medicine Physician'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Alternative Medicine Physician", 'green'))
print(df.loc[mask_alternative_medicine_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_alternative_medicine_values = df.loc[mask_alternative_medicine_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Alternative Medicine Physician", "cyan"))
for original_alternative_medicine_value in original_alternative_medicine_values:
    print(f"✅ {original_alternative_medicine_value} → Alternative Medicine Physician")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Alternative Medicine Physician:", 'red'))
print(grouped_alternative_medicine_values)

# Print summary
matched_count_alternative_medicine = mask_alternative_medicine_final.sum()

# Print results
print(
    colored(f"\nTotal values matched and changed (Stage 1) to Alternative Medicine Physician: {matched_count_alternative_medicine}",
            'red'))