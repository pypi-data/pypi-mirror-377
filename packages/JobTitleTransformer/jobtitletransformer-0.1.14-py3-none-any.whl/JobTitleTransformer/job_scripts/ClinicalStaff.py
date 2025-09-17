import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Clinical Staff related titles

clinical_staff_variants = [
    r"(?i)\bClinical\s?Staff\b",
    r"(?i)\bClinical\s?Team\b",
    r"(?i)\bClinical\s?Support\s?Staff\b",
    r"(?i)\bHealth\s?Care\s?Team\b",
    r"(?i)\bHealthcare\s?Provider\s?Staff\b",
    r"(?i)\bNursing\s?Staff\b",
    r"(?i)\bSupport\s?Staff\b",
    r"(?i)\bClinical\s?Healthcare\s?Staff\b",
    r"(?i)\bAnalistaassistente\b",
    r"(?i)\bAesthetic Facilitator\b",
    r"(?i)\bAesthetic Mediclinic\b",
    r"(?i)\bAesthetic Clinician\b",
    r"(?i)\bAesthetic Device\b",
    r"(?i)\bSeniorclinicalqualitycoordinator\b",
    r"(?i)\bClinical Resource Nurse\b",
    r"(?i)\bDirectrice Centre Laser\b",
    r"(?i)\bAesthetic & Laser\b",
    r"(?i)\bClinical Software Nurse\b",
    r"(?i)\bPhlebotomy\b",
    r"(?i)\bChief Clinical Offier\b",
    r"(?i)\bChief Clinical Information Officer\b",
    r"(?i)\bClinical Operation\b",
    r"(?i)\bCoordinador De Quirofano\b",
    r"(?i)\bPlastic Surgery Trauma Co-Ordinator\b",
    r"(?i)\bClinical Resource Nurse\b",
    r"(?i)\bLaser & Light Therapy Industry\b",
    r"(?i)\bMlso\b",
    r"(?i)\bSeniorclinicalqualitycoordinator\b",
    r"(?i)\bDirectrice Centre Laser\b",
    r"(?i)\bLab Technician\b",
    r"(?i)\bAesthetic & Laser\b",
    r"(?i)\bPhlebotomy\b",
    r"(?i)\bClinical Software Nurse\b",
    r"(?i)\bAesthetic Mediclinic\b",
    r"(?i)\bChief Clinical Offier\b",
    r"(?i)\bChief Clinical Information Officer\b",
    r"(?i)\bClinical Staff\b",
    r"(?i)\bLab Leader\b",
    r"(?i)\bClinical Operation\b",
    r"(?i)\bCoordinador De Quirofano\b",
    r"(?i)\bAnalistaassistente\b",
    r"(?i)\bAesthetic Clinician\b",
    r"(?i)\bMedical Lab Technologist\b",
    r"(?i)\bMedical Lab\b",
    r"(?i)\bLab Director\b",
    r"(?i)\bHealthcare Staff\b",
    r"(?i)\bLab Specialist\b",
    r"(?i)\bPlastic Surgery Trauma Co-Ordinator\b",
    r"(?i)\bMedical Lab Teachnaligi\b",
    r"(?i)\bLab Assistant In Government Hospital\b",
    r"(?i)\bAesthetic Facilitator\b",
    r"(?i)\bAesthetic Device\b",
    r"(?i)\bClinical Education\b",
    r"(?i)\bClinical Specialist\b",
    r"(?i)\bClincial Specialist\b",
    r"(?i)\bSenior Support Specialist\b",
    r"(?i)\bHealthcare Professional\b",
    r"(?i)\bHealthcare\s?Staff\b",
    r"(?i)\bLead Laser Technician\b",
    r"(?i)\bLaser Technician Lead\b",
    r"(?i)\bLazer Technician\b",
    r"(?i)\bAnesthesiologist Technician\b",
    r"(?i)\bX-Ray Technician\b",
    r"(?i)\bMedical Laboratory Technician\b",
    r"(?i)\bPharmacy Technician\b",
    r"(?i)\bMental Health Technician\b",
    r"(?i)\bCae  & Laser Technician\b",
    r"(?i)\bEndoscopy Technician\b",
    r"(?i)\bBiomedical Technician\b",
    r"(?i)\bHnd Pharmacy Technician\b",
    r"(?i)\bEpid  Insp  Technician\b",
]

# Exact matches that should be updated
clinical_staff_exact_matches = {
    'Clinical Staff',
    'Clinical Team',
    'Clinical Support Staff',
    'Health Care Team',
    'Healthcare Provider Staff',
    'Nursing Staff',
    'Support Staff',
    'Clinical Healthcare Staff',
    'Lab',
    'lab',
    'Lead',
    'lead',
    'Laser',
    'laser',

    # Common misspellings for Clinical Staff titles
    'Clincal Staff',
    'Clinicial Staff',
    'Clincial Team',
    'Clinical Teamm',
    'Clinical Support Staffs',

    # Case-related errors for Clinical Staff titles
    'CLINICAL STAFF',
    'clinical STAFF',
    'clinical staff',
    'CLINICAL Team',
    'Healthcare Team',
    'support STAFF',

    # Variants of Clinical Staff for different types in Spanish
    'Personal Clínico',
    'Personal Médico',
    'Equipo Clínico',
    'Equipo de Atención Médica',
    'Personal de Apoyo Clínico',
    'Personal de Salud',
    'Personal de Soporte',
    'Equipo de Proveedores de Atención Médica',
    'Personal de Enfermería',
    'Personal Clínico de Salud',

    # Other possible variations (Including Doctor forms, Specialist forms)
    'Medical Support Staff',
    'Clinical Care Staff',
    'Clinical Providers',
    'Medical Support Team',

    # other values from data sources
    'Mlso',
    'Lead',
    'Laser & Light Therapy Industry',
    'Laser',
    'laser',
    'Cco',
    'Ami Coordinator',
    'Director Of Operating Room',
    'Clinical Nurse Coordinator',
    'Surgical Technologist',
    'Coordinator Of New Life Plastic & Dermatology Plovdiv',
    'Healthcare Staff',
    'Healthcar Staff',
    'Healtcare Staff',
    'HealthCare Staff',
    'HEALTHCARE STAFF',
    'healthcare staff',
    'Healthcare Professional Staff',
    'Healthcare Professional',
    'Healthcare Services Staff',
    'Support Healthcare Staff',
    'Support Specialist',
    'Laser Technician',
    'Clincal Manager',
    'Surgical coordinator',
    'Scrub Tech',
    'Laser Tech',
    'Medical coordinator',
    'Patient Care Coordinator',
    'Patient care Coordinator',
    'Patient coordinator',
    'Woundcare Specialist',
    'Certified Chief Surgical Technician Bariatrics Colorectal General & Robotic Surgery',
    'Certified Dermatology Technician',
    'Dermatology Clinical Assistant',
    'Dermatology Technician',
    'General Surgery Clinical Coordinator',
    'General Surgery Inventory Coordinator',
    'Plastic & General Surgery Coordinator',
    'Residency Program General Surgery Coordinator',
    'Primary Coordinator',
    'Medical Coordinator',
    'Positions assistant',
    'Surgical Scrub Tech',
    'TECNICA',
    'Auxiliar en enfermeria',
    'C&D',
    'CMA',
    'CNA',
    'FSC',
    'FSE',
    'FSU',
    'Field Service Engineer',
}

# Define patterns for  & Resident & Professor (these should NOT be changed)
clinical_staff_exclusions = {
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
    'Physician Clinical Education Consultant',
}

# Create a mask for Clinical Staff
mask_clinical_staff = df['speciality'].str.contains('|'.join(clinical_staff_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(clinical_staff_exact_matches)
mask_clinical_staff_exclusions = df['speciality'].isin(clinical_staff_exclusions)

# Final mask: Select Clinical Staff
mask_clinical_staff_final = mask_clinical_staff & ~mask_clinical_staff_exclusions

# Store the original values that will be replaced
original_clinical_staff_values = df.loc[mask_clinical_staff_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_clinical_staff_final, 'speciality'] = 'Clinical Staff'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Clinical Staff", 'green'))
print(df.loc[mask_clinical_staff_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_clinical_staff_values = df.loc[mask_clinical_staff_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Clinical Staff", "cyan"))
for original_clinical_staff_value in original_clinical_staff_values:
    print(f"✅ {original_clinical_staff_value} → Clinical Staff")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Clinical Staff:", 'red'))
print(grouped_clinical_staff_values)

# Print summary
matched_count_clinical_staff = mask_clinical_staff_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Clinical Staff: "
        f"{matched_count_clinical_staff}",
        'red'))