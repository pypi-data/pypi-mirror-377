import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Clinic Manager related titles

clinic_manager_variants = [
    r"(?i)\bClinic\s?Manager\b",
    r"(?i)\bClinic\s?Administrator\b",
    r"(?i)\bHealthcare\s?Manager\b",
    r"(?i)\bMedical\s?Office\s?Manager\b",
    r"(?i)\bClinic\s?Supervisor\b",
    r"(?i)\bHealthcare\s?Administrator\b",
    r"(?i)\bNurse Manager\b",
    r"(?i)\bAestheticianClinic Manager\b",
    r"(?i)\bCentro Medico Azuaje\b",
    r"(?i)\bMedica Clinica Medica\b",
    r"(?i)\bTransportation Before & After Aesthetic Chirurgical Intervention\b",
    r"(?i)\bChief Of Staff\b",
    r"(?i)\bClinical Receptionist\b",
    r"(?i)\bOffice Mgr\b",
    r"(?i)\bClinical Support Services Manager\b",
    r"(?i)\bClinica Geral\b",
    r"(?i)\bClinico Geral\b",
    r"(?i)\bRnbn Clinic Director Plastic Surgery Centre\b",
    r"(?i)\bClinic Manager\b",
    r"(?i)\bClinic Administrator\b",
    r"(?i)\bClinicHospital\b",
    r"(?i)\bDental Clinic\b",
    r"(?i)\bAestetic Clinic Partner\b",
    r"(?i)\bRejenerative Clinic\b",
    r"(?i)\bOffice Manager\b",
    r"(?i)\bMedica Clinico Geral\b",
    r"(?i)\bClinical Receptionist\b",
    r"(?i)\bCeo Elite Helse Clinic\b",
    r"(?i)\bChief Of Staff\b",
    r"(?i)\bClinic CoordinatorBesuty Therapist\b",
    r"(?i)\bThe Pretty Young Clinic Seoul Korea\b",
    r"(?i)\bOffice Mgr\b",
    r"(?i)\bClinic Assistant\b",
    r"(?i)\bClinical Support Services Manager\b",
    r"(?i)\bClinica Geral\b",
    r"(?i)\bClinic Nurse\b",
    r"(?i)\bAesthetic Clinic Director\b",
    r"(?i)\bClinico Geral\b",
    r"(?i)\bClinic ManagerAnti-Aging Spacialist\b",
    r"(?i)\bAesthetic & Cosmetic Clinic\b",
    r"(?i)\bCentro Medico Azuaje\b",
    r"(?i)\bCeo Full Face Clinic\b",
    r"(?i)\bClinic Management\b",
    r"(?i)\bTransportation Before & After Aesthetic Chirurgical Intervention\b",
    r"(?i)\bClinic DirectorPlastic SurgeryRnbn\b",
    r"(?i)\bMedical Clinic Aesthetic Practice\b",
    r"(?i)\bRnbn Clinic Director Plastic Surgery Centre\b",
    r"(?i)\bClinic Management Ownership & Administration\b",
    r"(?i)\bDirector Cutaneous Imaging Clinic\b",
    r"(?i)\bCeo Of A Dermaesthetic Clinic\b",
    r"(?i)\bPain Rehabilitation Clinic\b",
    r"(?i)\bMedica Clinica Medica\b",
    r"(?i)\bNurse Manager\b",
    r"(?i)\bCeo Of Medical Clinic\b",
    r"(?i)\bClinic Director\b",
    r"(?i)\bHappy Aging Clinic Ceo\b",
    r"(?i)\bAesthetician & Clinic Assistant\b",
    r"(?i)\bCeo Of Aesthetic Clinic\b",
    r"(?i)\bClinical Nurse Manager\b",
    r"(?i)\bBeauty Clinic Ceo\b",
    r"(?i)\bDirector Of Ginza Tarumi Clinic\b",
    r"(?i)\bClinical Nurse Manager Emergency Department\b",
    r"(?i)\bHead Of The Clinic\b",
    r"(?i)\bMedica Clinica Geral\b",
    r"(?i)\bStem Cell Clinic\b",
    r"(?i)\bNurse Manager Rn\b",
    r"(?i)\bMember - Board Of Trustees Chief Of Staff - Umh Hospitals\b",
    r"(?i)\bAestheticianClinic Manager\b",
    r"(?i)\bClinic Manager Laser & Cosmetic Treatments\b",
    r"(?i)\bAesthetic Clinic Manager\b",
    r"(?i)\bHead Of Clinic\b",
    r"(?i)\bClinical Nurse Manager Of Behavioral Health Outpatient Services\b",
    r"(?i)\bClinic Manager Esthetician Not Using Injectables\b",
    r"(?i)\bClinical Nurse Manager Nicu Uh Rainbow Babies & ChildrenS\b",
    r"(?i)\bClinic ManagerAesthetican\b",
    r"(?i)\bClinic Director Of Cares Clinic\b",
    r"(?i)\bWellness Clinic\b",
    r"(?i)\bCoo Of A Clinic For Plastic Surgery\b",
    r"(?i)\bClinical Operations\b",
    r"(?i)\bClinical Governance\b",
    r"(?i)\bManager For Dr  Aziz\b",
]

# Exact matches that should be updated
clinic_manager_exact_matches = {
    'Clinic Manager',
    'Clinic Administrator',
    'Healthcare Manager',
    'Medical Office Manager',
    'Clinic Supervisor',
    'Healthcare Administrator',
    'Clinic',

    # Case-related errors
    'clinic manager',
    'clinic administrator',
    'healthcare manager',
    'medical office manager',
    'medical practice manager',
    'clinic supervisor',
    'healthcare administrator',
    'CLINIC MANAGER',
    'CLINIC ADMINISTRATOR',
    'HEALTHCARE MANAGER',
    'MEDICAL OFFICE MANAGER',
    'CLINIC SUPERVISOR',
    'HEALTHCARE ADMINISTRATOR',

    # Common misspellings
    'Clinic Maneger',
    'Clinic Mangager',
    'Clinc Manager',
    'Clinc Maneger',
    'Clinic Mananger',
    'Medial Office Manager',
    'Medicl Office Manager',
    'Medical Office Manger',

    # Spanish-related exclusions
    'Gerente de Clínica',
    'Administrador de Clínica',
    'Gerente de Atención Médica',
    'Gerente de Oficina Médica',
    'Supervisor de Clínica',
    'Administrador de Atención Sanitaria',
    
    # value from data sources
    'Clinic/Hospital',
    'Office Manager',
    'ClinicHospital',
    'Booking Manager',
    'Clinical Manager',
    'Clinic Hospital',
    'Private Clinic Hospital',
    'Other Clinic Hospital',
    'Clinic Operations Director',
    'Clinical Administrator',
    'Lead Patient Coordinator',
    'Treatment Coordinator',
    'Front Desk- Advanced Dermatology',
    'Medical Biller Dermatology',
    'Director of clinic operations',
    'Aesthetics Coordinator',
    'Aesthetics Manager',
    'Aesthetic Manager',
    'Cosmetic Manager',
    'COSMETIC MANAGER',
    'Cosmetic manage',
    'ARC',
    'Adm A',
    'Aesthetic Experience Manager',
    'Aesthetic Supervisor',
    'CHEF DE CLINIQUE',
    'CMM',
    'Consultation Co-ordinator',
    'Cosmetic Supervisor',
    'Director of WOO',
    'Executive Patient Concierge',
}

# Define patterns for  & Resident & Professor (these should NOT be changed)
clinic_manager_exclusions = {
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

# Create a mask for Clinic Manager
mask_clinic_manager = df['speciality'].str.contains('|'.join(clinic_manager_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(clinic_manager_exact_matches)
mask_clinic_manager_exclusions = df['speciality'].isin(clinic_manager_exclusions)

# Final mask: Select Clinic Manager
mask_clinic_manager_final = mask_clinic_manager & ~mask_clinic_manager_exclusions

# Store the original values that will be replaced
original_clinic_manager_values = df.loc[mask_clinic_manager_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_clinic_manager_final, 'speciality'] = 'Clinic Manager'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Clinic Manager", 'green'))
print(df.loc[mask_clinic_manager_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_clinic_manager_values = df.loc[mask_clinic_manager_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Clinic Manager", "cyan"))
for original_clinic_manager_value in original_clinic_manager_values:
    print(f"✅ {original_clinic_manager_value} → Clinic Manager")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Clinic Manager:", 'red'))
print(grouped_clinic_manager_values)

# Print summary
matched_count_clinic_manager = mask_clinic_manager_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Clinic Manager: "
        f"{matched_count_clinic_manager}",
        'red'))