import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Marketing Manager related titles

marketing_manager_variants = [
    # Standard Titles & Abbreviations
    r"(?i)\bMarketing\s?Manager\b",
    r"(?i)\bMarketing\s?Mng\b",
    r"(?i)\bMarketing\s?Mgr\b",
    r"(?i)\bMkt\s?Manager\b",
    r"(?i)\bMktg\s?Manager\b",
    r"(?i)\bMarketing\b",
    r"(?i)\bBrand Manager\b",
    r"(?i)\bCommercial Director\b",
    r"(?i)\bDesigner\b",
    r"(?i)\bCommercial Manager\b",
    r"(?i)\bChannel Manager\b",
    r"(?i)\bCosmetic PhysicianPodcast Host\b",
    r"(?i)\bEditorial Coordinator\b",
    r"(?i)\bP R  Medicina Estetica\b",
    r"(?i)\bP R\b",
    r"(?i)\bPR\b",
    r"(?i)\bPr & Social Media Coordinator\b",
    r"(?i)\bPR Specialist\b",
    r"(?i)\bSocial Media Pr Assistant\b",
    r"(?i)Social Media",
    r"(?i)\bHead Of Mr\b",
    r"(?i)\bPortfolio Sr  Manager\b",
    r"(?i)\bHead Of Communication\b",
    r"(?i)\bCommunication Manager\b",
    r"(?i)\bBrand Strategist\b",
    r"(?i)\bSeo Errors\b",
    r"(?i)\bBusiness Development Health Care\b",
    r"(?i)\bDigital Manager\b",
    r"(?i)\bAnalista De Mercadeo\b",
    r"(?i)\bPrint Strategist\b",
    r"(?i)\bAds\b",
    r"(?i)Business Development Manager",
    r"(?i)Content Strategist",
    r"(?i)Publicitaria",
    r"(?i)Business Development",
    r"(?i)\bPublicist\b",
    r"(?i)\bSeo\b",
    r"(?i)\bVideo Adds\b",
    r"(?i)\bMarket Mgr\b",
    r"(?i)\bMrktng Dir\b",
    r"(?i)\bStrategist\b",
    r"(?i)\bCorporate Communication\b",
    r"(?i)\bMedical Communication\b",
    r"(?i)\bMkt\b",
    r"(?i)\bLatest Innovations In Healthcare News Website\b",
    r"(?i)\bBdm\b",
    r"(?i)\bDev Web & Communication\b",
    r"(?i)\bBusiness Excellence Lead\b",
    r"(?i)\bVideos Add\b",
    r"(?i)\bEditorial\b",
    r"(?i)\bOnline\b",
    r"(?i)Facebook",
    r"(?i)Instagram",
    r"(?i)Digital Marketing",
    r"(?i)Marketing",
    r"(?i)Copywriter",
    r"(?i)\bCommunication\b",
    r"(?i)\bBusiness Developement\b",
    r"(?i)\bMktg Dir Botox\b",
    r"(?i)\bChargee De Communication\b",
    r"(?i)\bCommunication Agency\b",
    r"(?i)\bBody Contouring Product Marketing Manager\b",
    r"(?i)\bBusiness Growth\b",
    r"(?i)\bAssociate Media Director\b",
    r"(?i)\bBusiness Associate\b",
    r"(?i)\bMedia Supervisor\b",
    r"(?i)\bHvac Supervisor Or Telecom\b",
    r"(?i)\bSenior Media Supervisor\b",
    r"(?i)\bPrint Supervisor\b",
    r"(?i)\bMarketing & Communications Coordinator\b",
    r"(?i)\bSocial Media Coordinator\b",
    r"(?i)\bMedia Coordinator\b",
    r"(?i)\bMedia Planner\b",
    r"(?i)\bMedia Assistant\b",
    r"(?i)\bCommunications\b",
    r"(?i)\bVidep Editor\b",

    # Misspellings & Typographical Errors
    r"(?i)\bMarkting\s?Manager\b",
    r"(?i)\bMarketting\s?Manager\b",
    r"(?i)\bMarketing\s?Managr\b",
    r"(?i)\bMarkting\s?Managr\b",
    r"(?i)\bMarkeing\s?Manager\b",
    r"(?i)\bMarketing\s?Maneger\b",
    r"(?i)\bMarketing\s?Manger\b",
    r"(?i)\bMarket\s?Manager\b",

    # Case Variations
    r"(?i)\bmarketing manager\b",
    r"(?i)\bMarketing manager\b",
    r"(?i)\bmarketing Manager\b",
    r"(?i)\bMARKETING MANAGER\b",
    r"(?i)\bMarkEting ManageR\b",

    # Spanish Variants
    r"(?i)\bGerente\s?de\s?Marketing\b",
    r"(?i)\bGerente\s?de\s?Mercadeo\b",
    r"(?i)\bGerente\s?de\s?Publicidad\b",
    r"(?i)\bDirector\s?de\s?Marketing\b",
    r"(?i)\bDirector\s?de\s?Mercadotecnia\b",
    r"(?i)\bGerente\s?de\s?Comercialización\b",
    r"(?i)\bJefe\s?de\s?Marketing\b",
    r"(?i)\bJefe\s?de\s?Publicidad\b",
    r"(?i)\bGerente\s?de\s?Estrategia\s?de\s?Marketing\b",

    # Other Possible Variations
    r"(?i)\bMarketing\s?Head\b",
    r"(?i)\bMarketing\s?Lead\b",
    r"(?i)\bChief\s?Marketing\s?Officer\b",
    r"(?i)\bCMO\b",
    r"(?i)\bHead\s?of\s?Marketing\b",
    r"(?i)\bDigital\s?Marketing\s?Manager\b",
    r"(?i)\bBrand\s?Marketing\s?Manager\b",
    r"(?i)\bAdvertising\s?Manager\b",
    r"(?i)\bMarketing\s?and\s?Communications\s?Manager\b",
    r"(?i)\bStrategic\s?Marketing\s?Manager\b",
    r"(?i)\bProduct\s?Marketing\s?Manager\b",
    r"(?i)\bCorporate\s?Marketing\s?Manager\b",
    r"(?i)\bGrowth\s?Marketing\s?Manager\b",
    r"(?i)\bPerformance\s?Marketing\s?Manager\b",
    r"(?i)\bContent\s?Marketing\s?Manager\b",
    r"(?i)\bBrand Management\b",
    r"(?i)\bPracticeMarketing Manager\b",
    r"(?i)\bPractice ManagerMarketing\b",
    r"(?i)\bBusiness Development Director\b",
    r"(?i)\bBd\b",
    r"(?i)\bBusiness Developer\b",
    r"(?i)\bDirector Of Business Development\b",
    r"(?i)\bDesign\b",
    r"(?i)\bMktg\b",
    r"(?i)Marketer",
    r"(?i)Marketing",
    r"(?i)\bArt\b",
    r"(?i)\bPublisher\b",
    r"(?i)\bDeputy Editor\b",
    r"(?i)\bMarket Development\b",
    r"(?i)\bCommunication Evenementielle\b",
    r"(?i)\bPublication Planning\b",
    r"(?i)\bPr\b",
    r"(?i)\bBrand Manager\b",
    r"(?i)\bBusiness Develoment\b",
    r"(?i)\bMaketing Manager\b",
    r"(?i)\bMarekting Director\b",
    r"(?i)\bMrketing Director\b",
    r"(?i)\bAesthetic Marketplace Manager\b",
    r"(?i)\bCRM Manager\b",
]

# Exact matches that should be updated
marketing_manager_exact_matches = {
    "Marketing Manager",
    "Marketing Mgr",
    "Mkt Manager",
    "Mktg Manager",
    "Markting Manager",
    "Marketting Manager",
    "Marketing Managr",
    "Marketing Mngr",
    "Marketing Maneger",
    "Marketing Manger",
    "Market Manager",
    "Gerente de Marketing",
    "Gerente de Mercadeo",
    "Gerente de Publicidad",
    "Director de Marketing",
    "Director de Mercadotecnia",
    "Gerente de Comercialización",
    "Jefe de Marketing",
    "Jefe de Publicidad",
    "Gerente de Estrategia de Marketing",
    "Marketing Head",
    "Marketing Lead",
    "Chief Marketing Officer",
    "CMO",
    "Head of Marketing",
    "Digital Marketing Manager",
    "Brand Marketing Manager",
    "Advertising Manager",
    "Marketing and Communications Manager",
    "Strategic Marketing Manager",
    "Product Marketing Manager",
    "Corporate Marketing Manager",
    "Growth Marketing Manager",
    "Performance Marketing Manager",
    "Content Marketing Manager",
    "Marketing",
    "Markting",
    "Maketing",
    "Marekting",
    "Marrketing",
    "Markeitng",
    "Maketting",
    "Business Development Manager",
    "Marketing Director",
    "Dev",
    "dev",
    "Business Development",
    "PracticeMarketing Manager",
    "Practice ManagerMarketing",
    "Business Development Director",
    "Bd",
    "Director Of Business Development",
    'Design',
    'Graphiste',
    'Brand Specialist',
    'Facial Aesthetic Publications',
    'Publication Manager',
    'Topic Lead Websessions',
    'Creative Director',
    'Director Of Biz Dev',
    'Advertising Director',
    'Business Stretagy Executive',
    'Desiger',
    'Advertising',
    'Hd Of Bus Dvlpmnt & CommL Ops',
    'Brand Developer',
    'Dev Director',
    'Director of Development',
    'Client Relations',
    'Platform Manager',
    'Director of Business Strategies',
    'Director of Client Relations',
    'Global PRE',
    'Global PRE Director',
    'Loyalty Director',
    'V P Patient Acquisition',
    'Global Development Manager',
    'Regional Director Of Growth & Development',
    'A V',
    'AV',
    'Animator',
    'Creative Director Alle',
    'Creative Partner',
    'Creative director',
    'Digital Content Manager',
    'Dir Global Commerical Development',
    'Display Works',
    'EltaMD Brand Director',
}

# Define patterns (these should NOT be changed)
marketing_manager_exclusions = {
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
}

# Create a mask for Marketing Manager
mask_marketing_manager = df['speciality'].str.contains('|'.join(marketing_manager_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(marketing_manager_exact_matches)
mask_marketing_manager_exclusions = df['speciality'].isin(marketing_manager_exclusions)

# Final mask: Select Marketing Manager
mask_marketing_manager_final = mask_marketing_manager & ~mask_marketing_manager_exclusions

# Store the original values that will be replaced
original_marketing_manager_values = df.loc[mask_marketing_manager_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_marketing_manager_final, 'speciality'] = 'Marketing Manager'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Marketing Manager", 'green'))
print(df.loc[mask_marketing_manager_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_marketing_manager_values = df.loc[mask_marketing_manager_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Marketing Manager", "cyan"))
for original_marketing_manager_value in original_marketing_manager_values:
    print(f"✅ {original_marketing_manager_value} → Marketing Manager")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Marketing Manager:", 'red'))
print(grouped_marketing_manager_values)

# Print summary
matched_count_marketing_manager = mask_marketing_manager_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Marketing Manager: "
        f"{matched_count_marketing_manager}",
        'red'))