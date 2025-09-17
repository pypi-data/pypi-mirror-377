import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

df['speciality'] = df['speciality'].apply(normalize_text)  # Apply normalization

# Define regex patterns for ARNP-related titles (excluding RN, BSN)
arnp_variants = [
    r'\b(?:Arnp|Aprn|Advance Practice Nurse Practitioner|Aprn-Cnp|Fnp-Bc|Crna|Dnp|Rnc-Tnp|Enp|Crnp)\b',
    r'\b(?:Master Injector|Regenerative Med|Medspa Owner|Wellness Professional)\b',
    r'\b(?:Cosmetic Injector)\b',
    r'\b(?:Nurse \(Registered - Arnp\))\b',  # Ensures exact match
    r"(?i)\bARNP\b",
    r"(?i)\bAdvanced Registered Nurse Practitioner\b",
    r"(?i)\bArpn\b",
    r"(?i)\bArpn\b",
    r"(?i)\bAesthetic Nourse\b",
    r"(?i)\bAesthetic PracticionerNurse\b",
    r"(?i)\bCosmetic Injecting Nurse\b",
    r"(?i)\bDermatology Nurse\b",
    r"(?i)\bSkin TherapistNurse Dermatology\b",
    r"(?i)\bAdvanced Practice Registered Nurse\b",
    r"(?i)\bNurse Aesthetic\b",
    r"(?i)\bNurses\b",
    r"(?i)\bCnp\b",
    r"(?i)\bNurse Injector\b",
    r"(?i)\bNurse InjectorLaser\b",
]

# Exact matches that should be updated
arnp_exact_matches = {
    'Nurse (Registered - Arnp)',
    'Arnp',
    'Aprn',
    'Crna Injector',
    'Aprn Fnp-Bc',
    'Dnp Bsb Aprn Fnp-C Rnc-Tnp',
    'Mn Aprn Fnp-C',
    'Dnp Arnp',
    'Aprn Crna',
    'Advanced Registered Nurse Practitioner',
    'Advanced Nurse Practitioner',
    'Registered Nurse (ARNP)',
    'Registered Nurse Practitioner (ARNP)',
    'ARNP-C',
    'ARNP-FNP',
    'FNP-BC',
    'CRNA',
    'CRNA Injector',
    'Certified Nurse Practitioner',
    'Certified Advanced Practice Nurse',
    'Certified Nurse Midwife',
    'Nurse Practitioner (ARNP)',
    'Family Nurse Practitioner (ARNP)',
    'Adult Nurse Practitioner (ARNP)',
    'Pediatric Nurse Practitioner (ARNP)',
    'Psychiatric Nurse Practitioner (ARNP)',
    'Acute Care Nurse Practitioner (ARNP)',
    'Doctor of Nursing Practice (DNP)',
    'Doctor of Nursing Practice - APRN',
    'Doctorate APRN', 'DNP-ARNP',
    'Nurse Practitioner (APRN)',
    'Advanced Practice Registered Nurse (APRN)',
    'Nurse Anesthetist (CRNA)',
    'CRNA Nurse Injector',
    'APRNs',
    'APRN-CNP',
    'APRN-FNP',
    'FNP-BC APRN',
    'APRN-C',
    'Nurse Aesthetic Practitioner',
# Variations for common typos and case mistakes
    'Advanced Nurse Practitionar',
    'Adanced Nurse Practitioner',
    'Advaned Nurse Practitioner',
    'Arnp-CRNA',
    'Arnp-Crna',
    'APRN-Cnp',
    'Aprn-fnp',
    'APRN-Fnp',
    'Aprn-Fnp',
    'Doctor of Nursing Practce',
    'Doctorate APR',
    'Family Nurse Practioner (ARNP)',
    'Nurse Practioner (APRN)',
    'Nurse Anestheist (CRNA)',
    'FNP-BC',
    'Advanced Practiced Registered Nurse',
    'Advanced Practice Registered Nuse',
    'Advanced Nurse Practitoner',
    'Advanced Nursing Practitoner',
    'APRN Nurse',
    'APRN Nurse Practitioner',
    'Adanced Registered Nurse Practitioner',
    'Advanced Nurse Practicinor',
    'Advaneced Nurse Practitioner',
    'Nurse Practicianer (ARNP)',
    'Certified Nuse Practicioner',
    'A.D.N Nurse Practitioner',
    'Nurse Praticioner (ARNP)',
    'Advanced Nurse Practicioner (ARNP)',
    'Advanced Registered Nurse Practicioner (ARNP)',
    'Aesthetics Nurse',
    'Aesthetics NursePrescriber',
    'Aesthetic Nurse Specialist',
    'Aesthete Nurse',
    'NPNurse Injector',
    'AESTHETIC NURSE',
    'Advanced Practice Aesthetic RN',
    'Medical Aesthetics Nurse',
    'Dermatology Practice Nurse',
    'APN',
    'APN-C',
}

# Define patterns for RN & BSN (these should NOT be changed)
arnp_exclusions = r'\b(?:Rn|Bsn|Registered Nurse(?!\s+Advanced|\s+Practitioner|\s+Practicioner|\s*\()|Licensed Practical Nurse|Lpn)\b'

# Create a mask for ARNP-related terms but exclude RN/BSN
mask_arnp = df['speciality'].str.contains('|'.join(arnp_variants), case=False, na=False, regex=True) | \
            df['speciality'].isin(arnp_exact_matches)
mask_arnp_exclude = df['speciality'].str.contains(arnp_exclusions, case=False, na=False, regex=True)

# Final mask: Select ARNP-related values but exclude RN/BSN
mask_arnp_final = mask_arnp & ~mask_arnp_exclude

# Store the original values that will be replaced
original_arnp_values = df.loc[mask_arnp_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_arnp, 'speciality'] = 'Advanced Registered Nurse Practitioner (ARNP)'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Advanced Registered Nurse Practitioner (ARNP)", 'green'))
print(df.loc[mask_arnp_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_arnp_values = df.loc[mask_arnp_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Advanced Registered Nurse Practitioner (ARNP)", "cyan"))
for original_arnp_value in original_arnp_values:
    print(f"✅ {original_arnp_value} → Advanced Registered Nurse Practitioner (ARNP)")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with ARNP:", 'red'))
print(grouped_arnp_values)

# Print summary
matched_count_arnp = mask_arnp_final.sum()

# Print results
print(colored(f"\nTotal values matched and changed (Stage 1) to Advanced Registered Nurse Practitioner (ARNP): {matched_count_arnp}", 'red'))


