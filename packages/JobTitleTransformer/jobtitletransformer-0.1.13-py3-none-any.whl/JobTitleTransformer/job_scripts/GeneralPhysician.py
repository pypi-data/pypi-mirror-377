import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for General Physician related titles

general_physician_variants = [
    r"(?i)\bGeneral\s?Physician\b",
    r"(?i)\bGeneral\s?Practitioner\b",
    r"(?i)\bGP\b",
    r"(?i)\bFamily\s?Physician\b",
    r"(?i)\bFamily\s?Doctor\b",
    r"(?i)\bPrimary\s?Care\s?Physician\b",
    r"(?i)\bFamily Medicine\b",
    r"(?i)\bEpidemiologist\b",
    r"(?i)\bGeneral Practice\b",
    r"(?i)\bD O\b",
    r"(?i)\bDO\b",
    r"(?i)\bDra\b",
    r"(?i)\bMbbs\b",
    r"(?i)\bM b b s\b",
    r"(?i)\bM D\b",
    r"(?i)\bDr\b",
    r"(?i)\bDoc\b",
    r"(?i)\bMedico General\b",
    r"(?i)\bMedico Urgencias Medicas\b",
    r"(?i)\bAllergologist\b",
    r"(?i)\bGeneral Practioner\b",
    r"(?i)\bGeneral Practitioners\b",
    r"(?i)\bMedica Clinico Geral\b",
    r"(?i)\bConsulting Physician\b",
    r"(?i)\bEmergency Medicine\b",
    r"(?i)\bDocteur\b",
    r"(?i)\bInfectious Disease\b",
    r"(?i)\bDiagnosis\b",
    r"(?i)\bPodiatry\b",
    r"(?i)\bDoktor\b",
    r"(?i)\bGeneraliste\b",
    r"(?i)\bMdPrrsident\b",
    r"(?i)\bDokter\b",
    r"(?i)\bFamilymed\b",
    r"(?i)\bCritical Care Physician\b",
    r"(?i)\bMdphd\b",
    r"(?i)\bFamily Medicine\b",
    r"(?i)\bConsulting Physician\b",
    r"(?i)\bRehabilitation Specialist\b",

    # Spanish variants
    r"(?i)\bMédico\s?General\b",  # Spanish form (General Physician)
    r"(?i)\bMédico\s?de\s?Familia\b",  # Spanish form (Family Physician)
    r"(?i)\bMédico\s?Generalista\b",  # Spanish form (General Practitioner)
    r"(?i)\bMédico\s?de\s?Atención\s?Primaria\b",  # Spanish form (Primary Care Physician)

    # Other possible variations
    r"(?i)\bDoctor\s?General\b",
    r"(?i)\bDoctor\s?en\s?Medicina\s?General\b",
    r"(?i)\bBoard\s?Certified\s?General\s?Physician\b",
    r"(?i)\bGeneral\s?Medical\s?Doctor\b",
    r"(?i)\bLicensed\s?General\s?Physician\b",
    r"(?i)\bPrimary\s?Care\s?Physician\s?Specialist\b",
    r"(?i)\bCertified\s?General\s?Physician\b",
    r"(?i)\bDoctorOwner\b",
    r"(?i)\bGeneral Medicine\b",
    r"(?i)\bMedecin Generaliste\b",
    r"(?i)\bGeneral Practicioner\b",
    r"(?i)\bGeneral Physicion\b",
]

# Exact matches that should be updated
general_physician_exact_matches = {
    "General Physician",
    "General Practitioner",
    "GP",
    "Family Physician",
    "Family Doctor",
    "Primary Care Physician",
    # Spanish form matches
    "Médico General",
    "Médico de Familia",
    "Médico Generalista",
    "Médico de Atención Primaria",
    # Other possible variations
    "Doctor General",
    "Doctor en Medicina General",
    "Board Certified General Physician",
    "General Medical Doctor",
    "Licensed General Physician",
    "Primary Care Physician Specialist",
    "Certified General Physician",
    "Physician",
    "physician",
    "Physcian",
    "Phyisician",
    "Physisian",
    "Physician's",
    "Physican",
    "Phycisian",
    "Phisician",
    "Fysician",
    "Doctor",
    "Docter",
    "Dr",
    "dr",
    "Dotor",
    "Docotor",
    "Doctar",
    "Dr.",
    "dr.",
    "Dctor",
    "Doctr",
    "Docor",
    "Docr",
    'Other Physician',
    'md',
    'Md',
    'MD',
    'M D',
    'Private Clinic/Hospital',
    'Private ClinicHospital',
    'Medical Practitioner',
    'Medical Doctor',
    'Public Health Specialist',
    'Medicine',
    'General',
    'general',
    'Medecin',
    'DoctorOwner',
    'Generalist',
    'generalist',
    'Generaliste',
    'generaliste',
    'Clinic Doctor',
    'Clinic Physician',
    'Consultant Physician',
    'Family Practice',
    'Medical Director Physician',
    'Primary Care',
    'Family',
    'Medico',
    'Medica',
    'Medicine Doctor',
    'Doctor Of Medicine',
    'AestheticsGp',
    'Family MedicineAesthetics',
    'Medicina',
    'Vrach',
    'Docctor',
    'Medecin Generalist',
    'Medecine',
    'Oh Phusician',
    'Senior Physician',
    'Physical Medicine & Rehabilitation',
    'Primary  Operation',
    'Medecine Generale',
    'GpAesthetics',
    'Medico Principal',
    'Phusician',
    'Managing Practitioner',
    'Phisition',
    'Doctora',
    'Docytor',
    'ED Attending',
    'FMD',
    'MD MPH',
    'Md Ccfp Faarm',
    'Privada',
    'medico',
    'Doctor or Consultant',
    'Provider',
    'Physicisn',
    'Physician Mmg',
    'Attending Physician',
    'Emergency Physician',
    'Physician & Owner',
    'Physician - Med Onc',
    'Physician-Clinic',
    'Owner & Physician',
    'Physician & Founder',
    'Personal Physician',
    'Physician Owner',
    'Physician Partner - Hem',
    'Concierge Physician',
    'Physician & Chief Executive Officer',
    'Qp0032 - Physician',
    'Physicians',
    'Staff Physician',
    'Associate Physician',
    'Attending Physician Md',
    'Clinic Physician & Amp Ministry Medical Director Of Diabetes Care',
    'Physician & Co-Founder',
    'Physician & Employed',
    'Physician & Hospitalist',
    'Physician & Nocturnist',
    'Physician-Hospitalist Psv',
    'Senior Staff Physician',
    'Staff Physician Ii',
    'Supervising Physician',
    'Urgent Care Physician',
    'DPC',
    'EM',
    'Emergency',
    'FP',
}

# Define patterns (these should NOT be changed)
general_physician_exclusions = {
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
    'Family Physician Resident',
    'Emergency Medicine Resident Doctor',
    'Do You Want To Get More Sales',
    'General Medicine Student',
    'Gp Training',
    'Dr  Nurse Practitioner',
    'Doc In Maxillary Facial Surgery',
    'Practice Manager For Family Medicine Practice',
    'Personal Assistant To Dr',
    'Do Not Miss This Opportunity',
    'No Available Job I Do',
    'Senior Physician Recruiter- Emergency Medicine - Nebraska Iowa Arkansas & Kentucky',
    'Physician Recruiter--Emergency Medicine',
    'Physician Assistant - Emergency Medicine',
    'Emergency Medicine Physician Assistant',
}

# Create a mask for General Physician
mask_general_physician = df['speciality'].str.contains('|'.join(general_physician_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(general_physician_exact_matches)
mask_general_physician_exclusions = df['speciality'].isin(general_physician_exclusions)

# Final mask: Select General Physician
mask_general_physician_final = mask_general_physician & ~mask_general_physician_exclusions

# Store the original values that will be replaced
original_general_physician_values = df.loc[mask_general_physician_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_general_physician_final, 'speciality'] = 'General Physician'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: General Physician", 'green'))
print(df.loc[mask_general_physician_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_general_physician_values = df.loc[mask_general_physician_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: General Physician", "cyan"))
for original_general_physician_value in original_general_physician_values:
    print(f"✅ {original_general_physician_value} → General Physician")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with General Physician:", 'red'))
print(grouped_general_physician_values)

# Print summary
matched_count_general_physician = mask_general_physician_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to General Physician: "
        f"{matched_count_general_physician}",
        'red'))