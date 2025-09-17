import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Esthetician Cosmetician related titles

esthetician_variants = [
    r"(?i)\besthetician\b",
    r"(?i)\bcosmetician\b",
    r"(?i)\bestheticien\b",
    r"(?i)\bbeauty\s?therapist\b",
    r"(?i)\bcosmetic\s?esthetician\b",
    r"(?i)\blicensed\s?esthetician\b",
    r"(?i)\bcertified\s?esthetician\b",
    r"(?i)\bprofessional\s?esthetician\b",
    r"(?i)\bskin\s?care\s?specialist\b",
    r"(?i)\bcosmetic\s?specialist\b",
    r"(?i)\bskin\s?specialist\b",
    r"(?i)\bfacial\s?specialist\b",
    r"(?i)\bfacial\s?therapist\b",
    r"(?i)\bbeauty\s?specialist\b",
    r"(?i)\bbeauty\s?expert\b",
    r"(?i)\besthetician\s?MD\b",
    r"(?i)\bSkin Care\b",
    r"(?i)\bAesthetic Therapist\b",
    r"(?i)\bEstheticianMassage Therapist\b",
    r"(?i)\bDental Therapist\b",
    r"(?i)\bEsthetics\b",
    r"(?i)\bOther Cosmetic Beauty Specialty\b",
    r"(?i)\bOccupational Therapist\b",
    r"(?i)\bHair Removal\b",
    r"(?i)\bCosmetique\b",
    r"(?i)\bTherapist\b",
    r"(?i)\bBrows\b",
    r"(?i)\bCosmetologa Asesora\b",
    r"(?i)Aethetician",
    r"(?i)Aesthetician",
    r"(?i)Esthetician",
    r"(?i)Maquillista",
    r"(?i)\bKometyka\b",
    r"(?i)\bCertified Advanced EsthetcianAspiring Fnp\b",
    r"(?i)\bManicure Pedicure\b",
    r"(?i)\bEsthetic Beauty\b",
    r"(?i)\bSemi Permanent Makeup\b",
    r"(?i)\bSkintherapist & Podiatrist\b",
    r"(?i)\bCosmetic & Personal Care\b",
    r"(?i)\bFacialistBeautician\b",
    r"(?i)\bLash Master\b",
    r"(?i)\bNursBeautician\b",
    r"(?i)\bAltomaquiagem\b",
    r"(?i)\bPdo Threads\b",
    r"(?i)\bBeauticianPress\b",
    r"(?i)\bSkintherapist\b",
    r"(?i)\bHairSkin\b",
    r"(?i)\bAesthetic Laser Specialist\b",
    r"(?i)\bSkin & Laser Specialist\b",
    r"(?i)\bLazer & Skin Care Specialist\b",
    r"(?i)\bNurseSkin\b",
   r"(?i)\bParamedical Dermal\b",
   r"(?i)\bLaser Specialist\b",
   r"(?i)\bAesthetican\b",

    # Spanish variants
    r"(?i)\besteticista\b",  # Spanish form (esthetician)
    r"(?i)\besteticistas\b",  # Spanish plural form (esthetician)
    r"(?i)\bterapeuta\s?de\s?belleza\b",  # Spanish form (beauty therapist)
    r"(?i)\bestetista\s?profesional\b",  # Spanish form (professional esthetician)
    r"(?i)\bespecialista\s?en\s?cuidado\s?de\s?la\s?piel\b",  # Spanish form (skin care specialist)
    r"(?i)\besteticista\s?certificado\b",  # Spanish form (certified esthetician)

    # Other possible variations
    r"(?i)\bdoctor\s?in\s?esthetician\b",
    r"(?i)\bskin\s?care\s?doctor\b",
    r"(?i)\besthetician\s?expert\b",
    r"(?i)\bAesthetician\b",
    r"(?i)Aesthetician",
    r"(?i)\bAesthetician\b",
]

# Exact matches that should be updated
esthetician_exact_matches = {
    "Esthetician Cosmetician",
    "Certified Esthetician",
    "Beauty Therapist",
    "Skin Care Specialist",
    "Cosmetology Expert",
    "Facial Specialist",
    "Skincare",
    "Cosmetics",
    'Esthetics',
    'Esteticista',
    'Estheticienne',
    'Cosmetic Coordinator',
    'Hydro Facial',
    'Kosmetolog Massazhist',
    'Facial Massage',
    'Freelance Makeup Artist',
    'Internationally Certified Permananet Makeup Artist',
    'Esterica',
    'Waxing',
    'Micropigmentation',
    'Beauty Aesthetic',
    'Aestician',
    'Aesthetian',
    'Cosmetisc',
    'Aesthetian',
    'Facials',
    'Cosmetic NurseTrainer',
    'Aesthetcian',
    'Doctor Aestetician',
    'Facial consultant',
    'Cosmetic Lead',
}

# Define patterns (these should NOT be changed)
esthetician_exclusions = {
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
    'Cirujano General Medico Esteticista',
    'Esthetician Student',
    'Student Esthetician',
    'Aesthetician Student Nurse',
    'Medico CirujanoMedico Esteticista',
    'Skin Care Brand'
}

# Create a mask for Esthetician Cosmetician
mask_esthetician = df['speciality'].str.contains('|'.join(esthetician_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(esthetician_exact_matches)
mask_esthetician_exclusions = df['speciality'].isin(esthetician_exclusions)

# Final mask: Select Esthetician Cosmetician
mask_esthetician_final = mask_esthetician & ~mask_esthetician_exclusions

# Store the original values that will be replaced
original_esthetician_values = df.loc[mask_esthetician_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_esthetician_final, 'speciality'] = 'Esthetician Cosmetician'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Esthetician Cosmetician", 'green'))
print(df.loc[mask_esthetician_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_esthetician_values = df.loc[mask_esthetician_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Esthetician Cosmetician", "cyan"))
for original_esthetician_value in original_esthetician_values:
    print(f"✅ {original_esthetician_value} → Esthetician Cosmetician")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Esthetician Cosmetician:", 'red'))
print(grouped_esthetician_values)

# Print summary
matched_count_esthetician = mask_esthetician_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Esthetician Cosmetician: "
        f"{matched_count_esthetician}",
        'red'))