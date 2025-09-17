import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored


# Define regex patterns for Non medical Staff related titles

non_medical_staff_variants = [
    # Standard Titles & Abbreviations
    r"(?i)\bNon\s?Medical\s?Staff\b",
    r"(?i)\bNon\s?Med\s?Staff\b",
    r"(?i)\bNon\s?Healthcare\s?Staff\b",
    r"(?i)\bNon\s?Clinical\s?Staff\b",
    r"(?i)\bNon\s?Medical\s?Personnel\b",
    r"(?i)\bAdministrative\s?Staff\b",
    r"(?i)\bHospital\s?Administrative\s?Staff\b",
    r"(?i)\bMedical\s?Office\s?Staff\b",
    r"(?i)\bHealthcare\s?Support\s?Staff\b",
    r"(?i)\bExecutive Assistant\b",
    r"(?i)\bMedico Nao Socio\b",
    r"(?i)\bHotel Chain\b",
    r"(?i)\bDecorator\b",
    r"(?i)\bAnalyst\b",
    r"(?i)\bData\b",
    r"(?i)\bAdministrative Assistant\b",
    r"(?i)\bRecruitment Lead\b",
    r"(?i)\bTalent Acquisition Manager\b",
    r"(?i)Talent Acquisition",
    r"(?i)\bOffice Job\b",
    r"(?i)\bMedical Technologist\b",
    r"(?i)\bSecretaire De Direction\b",
    r"(?i)\bInterpreter\b",
    r"(?i)\bOffice Staff\b",
    r"(?i)\bAmministratore Delegato\b",
    r"(?i)\bOffice ManagerBookkeeper\b",
    r"(?i)\bSafety Officer\b",
    r"(?i)\bKitchen Assistance\b",
    r"(?i)\bTecnology\b",
    r"(?i)\bAdmin Assist\b",
    r"(?i)\bOffice Work\b",
    r"(?i)\bProgrammer\b",
    r"(?i)\bAdministrative Manager\b",
    r"(?i)\bNon Specialist\b",
    r"(?i)\bTechnical Department Spare Part Assistant\b",
    r"(?i)\bWorldS First Ai Writing Assistant\b",

    # Misspellings & Typographical Errors
    r"(?i)\bNon\s?Medial\s?Staff\b",
    r"(?i)\bNone\s?Medical\s?Staff\b",
    r"(?i)\bNon\s?Medicl\s?Staff\b",
    r"(?i)\bNon\s?Medicall\s?Staff\b",
    r"(?i)\bNon\s?Medicia\s?Staff\b",
    r"(?i)\bNon\s?Mdical\s?Staff\b",
    r"(?i)\bNon\s?Meducal\s?Staff\b",
    r"(?i)\bNonn\s?Medical\s?Staff\b",
    r"(?i)\bNon\s?Medikal\s?Staff\b",
    r"(?i)\bNon\s?Meddical\s?Staff\b",

    # Case Variations
    r"(?i)\bnon medical staff\b",
    r"(?i)\bNon Medical staff\b",
    r"(?i)\bnon Medical Staff\b",
    r"(?i)\bNON MEDICAL STAFF\b",
    r"(?i)\bNonMed Staff\b",

    # Spanish Variants
    r"(?i)\bPersonal\s?No\s?Médico\b",
    r"(?i)\bEmpleado\s?No\s?Médico\b",
    r"(?i)\bTrabajador\s?No\s?Médico\b",
    r"(?i)\bStaff\s?No\s?Clínico\b",
    r"(?i)\bPersonal\s?Administrativo\s?de\s?Salud\b",

    # Other Possible Variations (Including Doctor/Specialist Forms)
    r"(?i)\bNon\s?Medical\s?Assistant\b",
    r"(?i)\bMedical\s?Receptionist\b",
    r"(?i)\bMedical\s?Secretary\b",
    r"(?i)\bHospital\s?Clerk\b",
    r"(?i)\bHealthcare\s?Administrative\s?Staff\b",
    r"(?i)\bMedical\s?Support\s?Staff\b",
    r"(?i)\bIt\b",
    r"(?i)\bSecretary\b",
    r"(?i)\bAssistant Cook\b",
    r"(?i)\bElectricien\b",
    r"(?i)\bIngeniero De Sistemas\b",
    r"(?i)\bSoftware Engineer\b",
    r"(?i)\bAdministrative Officer\b",
    r"(?i)\bAdministration\b",
    r"(?i)\bControl Officer\b",
    r"(?i)\bEngineering\b",
    r"(?i)\bEnegineer\b",
    r"(?i)\bElectricien\b",
    r"(?i)\bTalent Acquisition Manager\b",
    r"(?i)\bAnalyst\b",
    r"(?i)\bSenior Business Operation Analyst\b",
    r"(?i)\bExecutive Assistant\b",
    r"(?i)\bData\b",
    r"(?i)\bBiomedical Engineer\b",
    r"(?i)\bElectrical Engineer\b",
    r"(?i)\bAircraft Engineer\b",
    r"(?i)\bMedico Nao Socio\b",
    r"(?i)\bIngeniero De Sistemas\b",
    r"(?i)\bAdministration\b",
    r"(?i)\bAdministrative Assistant\b",
    r"(?i)\bAdmin\b",
    r"(?i)\bAdministrative Officer\b",
    r"(?i)\bMedical Technologist\b",
    r"(?i)\bOffice Job\b",
    r"(?i)\bIt Specialist\b",
    r"(?i)\bChemical Engineering\b",
    r"(?i)\bData Entry\b",
    r"(?i)\bEngineering\b",
    r"(?i)\bInformation Technologies It\b",
    r"(?i)\bRisk Analyst\b",
    r"(?i)\bIt\b",
    r"(?i)\bIt Manager\b",
    r"(?i)\bKitchen Assistance\b",
    r"(?i)\bOffice Staff\b",
    r"(?i)\bExecutive Assistant At Skillmed\b",
    r"(?i)\bDirector Of It\b",
    r"(?i)\bIt Services Manager\b",
    r"(?i)\bDecorator\b",
    r"(?i)\bInterpreter\b",
    r"(?i)\bControl Officer\b",
    r"(?i)\bData Entiry\b",
    r"(?i)\bIt Director\b",
    r"(?i)\bApplication Support Analyst\b",
    r"(?i)\bTecnology\b",
    r"(?i)\bJapanese Interpreter\b",
    r"(?i)\bAmministratore Delegato\b",
    r"(?i)\bCredit Control Business Analyst\b",
    r"(?i)\bSenior Business Analyst\b",
    r"(?i)\bMedical Engineer\b",
    r"(?i)\bOffice ManagerBookkeeper\b",
    r"(?i)\bSafety Officer\b",
    r"(?i)\bAvionics Technician\b",
    r"(?i)\bSecretary-General Of The Expert Group\b",
    r"(?i)\bData Interi\b",
    r"(?i)\bResearch Analyst\b",
    r"(?i)\bSecretary Of Society\b",
    r"(?i)\bAdmin Assist\b",
    r"(?i)\bOffice Work\b",
    r"(?i)\bProgrammer\b",
    r"(?i)\bAdministrative Manager\b",
    r"(?i)\bSecretary Ips\b",
    r"(?i)\bBiomedical Enegineer\b",
    r"(?i)\bCustomer Service Engineer\b",
    r"(?i)\bSystem Analyst\b",
    r"(?i)\bRecruitment Lead\b",
    r"(?i)\bHotel Chain\b",
    r"(?i)\bData Services Executive\b",
    r"(?i)\bDeputy Director Of It\b",
    r"(?i)\bData Analyst\b",
    r"(?i)\bNon Specialist\b",
    r"(?i)\bField Application Engineer\b",
    r"(?i)\bGraduate In Administration\b",
    r"(?i)\bPortfolio Analyst\b",
    r"(?i)\bTissue Engineering\b",
    r"(?i)\bR&D Engineer\b",
    r"(?i)\bYes ItS Free - Bookmark It Now\b",
    r"(?i)\bCivil Engineer\b",
    r"(?i)\bHead Of It Services\b",
    r"(?i)\bWife Secretary\b",
    r"(?i)\bApplication Analyst\b",
    r"(?i)\bSr  R&D Engineer\b",
    r"(?i)\bIt Systems Manager\b",
    r"(?i)\bSecurity Analyst\b",
    r"(?i)\bData Entry Operator\b",
    r"(?i)\bMecatronics & Biomedical Engineering\b",
    r"(?i)\bBiiomedical Analyst\b",
    r"(?i)\bAdministration & Finance Director\b",
    r"(?i)\bPersonal Secretary\b",
    r"(?i)\bStudying Business Administration & Management\b",
    r"(?i)\bSite Engineer\b",
    r"(?i)\bHead Of It\b",
    r"(?i)\bIt Consultant\b",
    r"(?i)\bOffice Administrative Assistant\b",
    r"(?i)\bEnvironmental Safety Officer\b",
    r"(?i)\bPaediatrician Analyst Public Health Agency Sweden\b",
    r"(?i)\bAssistant Cook\b",
    r"(?i)\bData Curator\b",
    r"(?i)\bBusiness Administration\b",
    r"(?i)\bDirector Engineering Department\b",
    r"(?i)\bHealth Engineering Student\b",
    r"(?i)\bR&D Quality Engineer\b",
    r"(?i)\bElectrical Engineering\b",
    r"(?i)\bComputer Engineering\b",
    r"(?i)\bBeauty Market Analyst\b",
    r"(?i)\bAv Technician\b",
    r"(?i)\bData Entry Adds Watching Computer Master\b",
    r"(?i)\bIt Helpdesk\b",
    r"(?i)\bField Technician\b",
    r"(?i)\bMedical Interpreter\b",
    r"(?i)\bMedical Administrative Assistant\b",
    r"(?i)\bSenior Information Analyst\b",
    r"(?i)\bSenior Research Analyst\b",
    r"(?i)\bEstimation Engineer\b",
    r"(?i)\bApp Analyst\b",
    r"(?i)\bBiomedical Engineering\b",
    r"(?i)\bPatent Engineer\b",
    r"(?i)\bSenior Field Service Engineer\b",
    r"(?i)\bClinical Quality & Patient Safety Officer\b",
    r"(?i)\bFinancial Analyst\b",
    r"(?i)\bInvestment Analyst\b",
    r"(?i)\bBusiness Analyst\b",
    r"(?i)\bProfessor Of Electrical Engineering Dept\b",
    r"(?i)\bDigital Analyst\b",
    r"(?i)\bSupercharge Your Writing Skills With Ai - Try It Free Today\b",
    r"(?i)\bAc Technician\b",
    r"(?i)\bLaunch Your Very Own Ai App Just Like Chatgpt & Charge People For It\b",
    r"(?i)\bAssistant Director Of It & Cfh\b",
    r"(?i)\bPackaging & Device Engineer\b",
    r"(?i)\bTesting Commissioning Engineer\b",
    r"(?i)\bData EntryWork Assignment\b",
]

# Exact matches that should be updated
non_medical_staff_exact_matches = {
    'Non-medical Staff',
    "Non Medical Staff",
    "Non Med Staff",
    "Non Healthcare Staff",
    "Non Clinical Staff",
    "Non Medical Personnel",
    "Administrative Staff",
    "Hospital Administrative Staff",
    "Medical Office Staff",
    "Healthcare Support Staff",
    "Non Medial Staff",
    "None Medical Staff",
    "Non Medicl Staff",
    "Non Medicall Staff",
    "Non Medicia Staff",
    "Non Mdical Staff",
    "Non Meducal Staff",
    "Nonn Medical Staff",
    "Non Medikal Staff",
    "Non Meddical Staff",
    "Personal No Médico",
    "Empleado No Médico",
    "Trabajador No Médico",
    "Staff No Clínico",
    "Personal Administrativo de Salud",
    "Non Medical Assistant",
    "Medical Receptionist",
    "Medical Secretary",
    "Hospital Clerk",
    "Healthcare Administrative Staff",
    "Medical Support Staff",
    "Administrative Employee",
    "Staff",
    "Admin",
    "Administrator",
    'ADMINISTRATOR',
    'Engineer',
    'It',
    'Online Work',
    'Engineer',
    'engineer',
    'Secretary',
    'secretary',
    'Facial Aesthetics Administrative Support',
    'Manager Facial Aesthetics Administrative Support',
    'Non-Medical Staff',
    'Graphic Installer',
    'Stand Builder',
    'Technician',
    'technician',
    'Guest',
    'guest',
    'Escort for attendee',
}

# # Define patterns (these should NOT be changed)
# non_medical_staff_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

non_medical_staff_exclusions = {
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
    'Sales Technician',
    'Sales Administrator',
    'Administrative coordinator',
    'Executive Assistant To Cao & Physician Liaison',
    'Executive Administrative Assistant To The Chief Executive Officer & Dental Manager',
    'Epic Resolute Hospital Billing & Physician Billing Senior Analyst',
    'Physician & Professional Clinic Talent Acquisition Specialist',
    'Dental Administrative Assistant',
    'Administrative Assistant Dental Department',
    'Executive Assistant Dermatology',
    'Physicians Administration',
    'Division Senior Sales Manager Administration L Oreal Dermatological Beauty',
    'Executive Assistant To Chief Commercial Officer Dental & Specialty Markets',
    'Administrative Assistant General Surgery',
}

# Create a mask for Non medical Staff
mask_non_medical_staff = df['speciality'].str.contains('|'.join(non_medical_staff_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(non_medical_staff_exact_matches)

# mask_non_medical_staff_exclusions = df['speciality'].str.contains(non_medical_staff_exclusions, case=False, na=False, regex=True)
mask_non_medical_staff_exclusions = df['speciality'].isin(non_medical_staff_exclusions)

# Final mask: Select Non medical Staff
mask_non_medical_staff_final = mask_non_medical_staff & ~mask_non_medical_staff_exclusions

# Store the original values that will be replaced
original_non_medical_staff_values = df.loc[mask_non_medical_staff_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_non_medical_staff_final, 'speciality'] = 'Non medical Staff'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Non medical Staff", 'green'))
print(df.loc[mask_non_medical_staff_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_non_medical_staff_values = df.loc[mask_non_medical_staff_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Non medical Staff", "cyan"))
for original_non_medical_staff_value in original_non_medical_staff_values:
    print(f"✅ {original_non_medical_staff_value} → Non medical Staff")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Non medical Staff:", 'red'))
print(grouped_non_medical_staff_values)

# Print summary
matched_count_non_medical_staff = mask_non_medical_staff_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Non medical Staff: "
        f"{matched_count_non_medical_staff}",
        'red'))