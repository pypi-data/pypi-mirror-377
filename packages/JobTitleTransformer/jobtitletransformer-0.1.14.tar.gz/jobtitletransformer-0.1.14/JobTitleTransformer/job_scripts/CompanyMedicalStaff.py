import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Company Medical Staff related titles

company_medical_staff_variants = [
    r"(?i)\bcompany\s?medical\s?staff\b",
    r"(?i)\bmedical\s?staff\s?of\s?company\b",
    r"(?i)\bcorporate\s?medical\s?staff\b",
    r"(?i)\bcompany\s?healthcare\s?team\b",
    r"(?i)\borganization\s?medical\s?staff\b",
    r"(?i)\bmedical\s?team\s?of\s?company\b",
    r"(?i)\bcompany\s?medcal\s?staff\b",
    r"(?i)\bcompnay\s?medical\s?staff\b",
    r"(?i)\bcompany\s?mdeical\s?staff\b",
    r"(?i)\bcompany\s?mediccal\s?staff\b",
    r"(?i)\bcompany\s?medikal\s?staff\b",
    r"(?i)\bpersonal\s?médico\s?de\s?empresa\b",
    r"(?i)\bstaff\s?médico\s?de\s?compañía\b",
    r"(?i)\bequipo\s?médico\s?de\s?empresa\b",
    r"(?i)\bempleados\s?médicos\s?corporativos\b",
    r"(?i)\bcompany\s?physician\s?team\b",
    r"(?i)\bmedical\s?professionals\s?of\s?company\b",
    r"(?i)\bcorporate\s?health\s?staff\b",
    r"(?i)\bCompanyS Medical Staff\b",
    r"(?i)\bMedical\s?Team\b",
]

# Exact matches that should be updated
company_medical_staff_exact_matches = {
    'Company Medical Staff',
    'CompanyS Medical Staff',
    'Corporate Medical Staff',
    'Medical Team of Company',
    'Organization Medical Staff',
    'Company Healthcare Team',
    'Company Physician Team',
    'Medical Professionals of Company',
    'Corporate Health Staff',
    'Medical Staff',
    'medical staff',
    'med staff',
    'medicl staf',
    'Medical staff',
    'medical staff',
    'Medicalstaff',
    'MedicalStaff',
    'Medial Staff',
    'Medicla Staff',
    'MEDICAL STAFF',
    'medical staff',
    'Equipo Médico',
    'Medical Staff',
    'Medical Team',
    'Medial Team',
    'medical TEAM',
    'Physician Recruiter',
    'Senior Physician Recruiter',
    'Physician Recruitment',
    'Director Of Physician Recruitment',
    'Manager Physician Recruitment',
    'Physician Relations Manager',
    'Physician Relations Director',
    'Physician Recruitment Manager',
    'Director Physician Recruitment',
    'Assistant Vice President & Revenue Cycle Physician',
    'Associate Physician Recruiter',
    'Clinician & Physician Sourcer',
    'Coordinator - Physician Recruitment',
    'Corporate Director Physician Recruitment',
    'Dermatology Relations Professional',
    'Director Human Resources & Ambulatory & Services Physician',
    'Director Human Resources & Recruitment Physician',
    'Director Of Physician Relations',
    'Director Of Physician Services Ii',
    'Director Patient Services Programs Dermatology Psoriatic Disease Us',
    'Director Physician & Provider Recruitment',
    'Director Physician Recruitment - Connecticut & Supported Rhode Island Market',
    'Director Physician Relations',
    'Director Physician Relationship Management Technology',
    'Director Physician Talent',
    'Director Revenue Cycle & Premier Network Physician',
    'Director System & Recruitment Physician',
    'Cdi Physician Advisor',
    'Physician Liaison',
    'Clinician- Colorado Physician Health Program',
    'Division Manager Licensing For The Mn Board Of Cosmetology',
    'Ems& Cosmetology Licensing Aide Professional',
    'Executive Assistant To Cao & Physician Liaison',
    'Executive Assistant Dermatology',
    'Executive Community Physician Leader',
    'Executive Vp Chief Physician Executive & Chief Clinical Officer',
    'Field Director- Immunology & Dermatology',
    'Heor Strategy Dermatology Launches & Pipeline Lead',
    'Heritage Network Physicians',
    'Integrated Physician Omni Healthcare',
    'Internal Physician Relations Manager',
    'National Field Director Dermatology',
    'Nephrology Physician Recruiter',
    'Obgyn Physician Recruiter',
    'Pediatric Physician Recruiter',
    'Physician & Advanced Practice Provider Recruiter',
    'Physician & Apc Recruiter',
    'Physician & App Recruiter',
    'Physician & Faculty Recruiter',
    'Physician & Professional Clinic Talent Acquisition Specialist',
    'Physician & Provider Recruiter',
    'Physician & Provider Relations Manager',
    'Physician & Provider Relationship Manager',
    'Physician Access Coordinator',
    'Physician Access Coordinator Referring Physician Office',
    'Physician App & Leadership Recruiter',
    'Physician Outreach Coordinator',
    'Physician Outreach Specialist',
    'Physician Partnership Network Manager',
    'Physician Recruiter & Contracts Coordinator',
    'Physician Recruiter - Otolaryngology Ent & Internal Medicine Consultant',
    'Physician Recruiter Specialist',
    'Physician Recruiter--Emergency Medicine',
    'Physician Recruitment Assistant',
    'Physician Recruitment Specialist Senior',
    'Physician Relations Associate',
    'Physician Relations Coordinator',
    'Physician Resilience Medical Director',
    'Physician Resource Officer',
    'Physician Resources',
    'Physician Resources Specialist',
    'Physician Review Coordinator',
    'Physician Scheduler',
    'Physician Scheduler Provider Services Southeast Group',
    'Physician Sourcer',
    'Physician Support Specialist',
    'Regional Physician Services Manager',
    'Revenue Cycle Physicians Pfs',
    'Scheduler Dermatology',
    'Senior Engineer Medical Device Imaging Systems For Dermatology',
    'Senior Physician & Apc Recruiter',
    'Senior Physician Recruiter Remote',
    'Senior Physician Recruiter- Emergency Medicine - Nebraska Iowa Arkansas & Kentucky',
    'Specialist-Physician Relations',
    'Teleradiologist Physician Contractor',
    'Trauma & General Surgery App Supervisor',
    'Veterinary Technician- Dermatology',
    'Vice President Of Ambulatory & Physician Services',
    'Vice President Penn Highlands Physician Network',
    'Vice President Physician Acquisition',
    'Vice President Physician Development',
    'Vice President Physician Partnerships',
    'Vice President Physician Services',
    'Vice President- Physician Strategy Growth & Development',
    'Endo Aesthetics',
    'PowerAestheticGROUP',
    'Allergan Practice Consultant Facial Aesthetics',
    'Director Provider',
}

# Define patterns (these should NOT be changed)
company_medical_staff_exclusions = {
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
    'Aesthetic Resident'
}

# Create a mask for Company Medical Staff
mask_company_medical_staff = df['speciality'].str.contains('|'.join(company_medical_staff_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(company_medical_staff_exact_matches)
mask_company_medical_staff_exclusions = df['speciality'].isin(company_medical_staff_exclusions)

# Final mask: Select Company Medical Staff
mask_company_medical_staff_final = mask_company_medical_staff & ~mask_company_medical_staff_exclusions

# Store the original values that will be replaced
original_company_medical_staff_values = df.loc[mask_company_medical_staff_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_company_medical_staff_final, 'speciality'] = 'Company Medical Staff'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Company Medical Staff", 'green'))
print(df.loc[mask_company_medical_staff_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_company_medical_staff_values = df.loc[mask_company_medical_staff_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Company Medical Staff", "cyan"))
for original_company_medical_staff_value in original_company_medical_staff_values:
    print(f"✅ {original_company_medical_staff_value} → Company Medical Staff")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Company Medical Staff:", 'red'))
print(grouped_company_medical_staff_values)

# Print summary
matched_count_company_medical_staff = mask_company_medical_staff_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Company Medical Staff: "
        f"{matched_count_company_medical_staff}",
        'red'))