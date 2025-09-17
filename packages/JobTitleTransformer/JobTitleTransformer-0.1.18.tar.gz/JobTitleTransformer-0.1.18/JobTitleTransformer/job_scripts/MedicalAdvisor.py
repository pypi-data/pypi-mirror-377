import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Medical Advisor related titles

medical_advisor_variants = [
    # Standard Titles & Abbreviations
    r"(?i)\bMedical\s?Advisor\b",
    r"(?i)\bMedical\s?Affairs\s?Advisor\b",
    r"(?i)\bHealthcare\s?Advisor\b",
    r"(?i)\bMedical\s?Affairs\s?Specialist\b",
    r"(?i)\bScientific\s?Advisor\b",
    r"(?i)\bClinical\s?Advisor\b",
    r"(?i)\bSenior\s?Medical\s?Advisor\b",
    r"(?i)\bChief\s?Medical\s?Advisor\b",
    r"(?i)\bMedical\s?Affairs\s?Manager\b",
    r"(?i)\bHead Of Advisory\b",
    r"(?i)\bPhysician Liason\b",
    r"(?i)\bApprentice Medical Communication\b",
    r"(?i)\bMsd\b",
    r"(?i)\bScience Executive Advisor\b",
    r"(?i)\bSenior Regulatory Advisor\b",

    # Misspellings & Typographical Errors
    r"(?i)\bMedcial\s?Advisor\b",
    r"(?i)\bMediacl\s?Advisor\b",
    r"(?i)\bMedical\s?Advisr\b",
    r"(?i)\bMedical\s?Advissor\b",
    r"(?i)\bMedical\s?Advisro\b",
    r"(?i)\bMedcial\s?Advisr\b",
    r"(?i)\bMedical\s?Advizeor\b",
    r"(?i)\bMedicall\s?Advisor\b",
    r"(?i)\bMedical\s?Advisour\b",
    r"(?i)\bMedical\s?Adviosr\b",

    # Case Variations
    r"(?i)\bmedical advisor\b",
    r"(?i)\bMedical advisor\b",
    r"(?i)\bmedical Advisor\b",
    r"(?i)\bMEDICAL ADVISOR\b",
    r"(?i)\bMedIcal AdvIsor\b",

    # Spanish Variants
    r"(?i)\bAsesor\s?Médico\b",
    r"(?i)\bEspecialista\s?en\s?Asuntos\s?Médicos\b",
    r"(?i)\bConsejero\s?Médico\b",
    r"(?i)\bDirector\s?Médico\s?Consultor\b",
    r"(?i)\bGestor\s?de\s?Asuntos\s?Médicos\b",
    r"(?i)\bAsesor\s?de\s?Salud\b",

    # Other Possible Variations (Including Doctor/Specialist Titles)
    r"(?i)\bMedical\s?Director\b",
    r"(?i)\bMedical\s?Strategy\s?Advisor\b",
    r"(?i)\bRegulatory\s?Medical\s?Advisor\b",
    r"(?i)\bPharmaceutical\s?Advisor\b",
    r"(?i)\bDrug\s?Safety\s?Advisor\b",
    r"(?i)\bClinical\s?Regulatory\s?Advisor\b",
    r"(?i)\bSenior\s?Medical\s?Consultant\b",
    r"(?i)\bGlobal\s?Medical\s?Advisor\b",
    r"(?i)\bHealth\s?Policy\s?Advisor\b",
    r"(?i)\bHealthcare\s?Regulatory\s?Advisor\b",
    r"(?i)\bMedical Affairs Lead\b",
]

# Exact matches that should be updated
medical_advisor_exact_matches = {
    "Medical Advisor",
    "Medical Affairs Advisor",
    "Healthcare Advisor",
    "Medical Affairs Specialist",
    "Scientific Advisor",
    "Clinical Advisor",
    "Senior Medical Advisor",
    "Chief Medical Advisor",
    "Medical Affairs Manager",
    "Medcial Advisor",
    "Mediacl Advisor",
    "Medical Advisr",
    "Medical Advissor",
    "Medical Advisro",
    "Medcial Advisr",
    "Medical Advizeor",
    "Medicall Advisor",
    "Medical Advisour",
    "Medical Adviosr",
    "Asesor Médico",
    "Especialista en Asuntos Médicos",
    "Consejero Médico",
    "Director Médico Consultor",
    "Gestor de Asuntos Médicos",
    "Asesor de Salud",
    "Medical Director",
    "Medical Strategy Advisor",
    "Regulatory Medical Advisor",
    "Pharmaceutical Advisor",
    "Drug Safety Advisor",
    "Clinical Regulatory Advisor",
    "Senior Medical Consultant",
    "Global Medical Advisor",
    "Health Policy Advisor",
    "Healthcare Regulatory Advisor",
    "Surgical Equipment",
    'Advisor',
    'Adviser',
    'Director Of Medical Supply',
    'Program Manager Health Public & Government Affairs',
    'Medicina Estrategica',
    'Director II Skincare Clinical Development & Medical Affairs',
    'Global Medical Advocacy',
    'HCP Advocacy',
    'MEDICA',
    'MEDICO',
    'MSL',
    'Medical Affairs Clinician',
    'Medical Science Liaison Skincare',
    'Physician Advisor',
    'Certified Dermatology Coder',
    'Dermatology Medical Affairs Head Us',
    'Director Field Medical Dermatology',
    'Director Medical Affairs Dermatology Us',
    'Medical Science Dermatology & Iai Liaison',
    'Medical Science Executive & Dermatology Immunology Liaison',
    'Director Medical Affairs',
    'Director Medical Affairs Clinical & Medical Affairs',
    'Medical Affairs',
    'Sr  Director Medical Affairs',
    'Associate Medical Affair Advisor - Neuromodulators',
    'DMP',
}

# Define patterns (these should NOT be changed)
medical_advisor_exclusions = r'\b(?:Plastic)|(?:Physician)|(?:Neonatology)\b'

# Create a mask for Medical Advisor
mask_medical_advisor = df['speciality'].str.contains('|'.join(medical_advisor_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(medical_advisor_exact_matches)
mask_medical_advisor_exclusions = df['speciality'].str.contains(medical_advisor_exclusions, case=False, na=False, regex=True)

# Final mask: Select Medical Advisor
mask_medical_advisor_final = mask_medical_advisor & ~mask_medical_advisor_exclusions

# Store the original values that will be replaced
original_medical_advisor_values = df.loc[mask_medical_advisor_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_medical_advisor_final, 'speciality'] = 'Medical Advisor'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Medical Advisor", 'green'))
print(df.loc[mask_medical_advisor_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_medical_advisor_values = df.loc[mask_medical_advisor_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Medical Advisor", "cyan"))
for original_medical_advisor_value in original_medical_advisor_values:
    print(f"✅ {original_medical_advisor_value} → Medical Advisor")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Medical Advisor:", 'red'))
print(grouped_medical_advisor_values)

# Print summary
matched_count_medical_advisor = mask_medical_advisor_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Medical Advisor: "
        f"{matched_count_medical_advisor}",
        'red'))