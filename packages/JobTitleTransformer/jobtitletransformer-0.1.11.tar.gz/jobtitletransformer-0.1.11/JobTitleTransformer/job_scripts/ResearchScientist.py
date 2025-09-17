import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Research Scientist related titles

research_scientist_variants = [
    # Standard Titles & Variants
    r"(?i)\bResearch Scientist\b",
    r"(?i)\bScientific Researcher\b",
    r"(?i)\bScientist\b",
    r"(?i)\bPrincipal Investigator\b",
    r"(?i)\bLaboratory Scientist\b",
    r"(?i)\bScientific Researcher (Research Scientist)\b",
    r"(?i)\bResearch Associate\b",
    r"(?i)\bPostdoctoral Researcher\b",
    r"(?i)\bBiomedical Research Scientist\b",
    r"(?i)\bR&D\b",
    r"(?i)\bAnalyst\b",
    r"(?i)\bResearcher\b",
    r"(?i)\bRa\b",
    r"(?i)\bOrganism\b",
    r"(?i)\bPrecision Medicine\b",
    r"(?i)\bScientific Writer\b",
    r"(?i)\bEvidence Generation\b",
    r"(?i)\bDirecteur Scientifique\b",
    r"(?i)\bScientific Manager\b",
    r"(?i)\bChief Scientific Officer\b",
    r"(?i)\bInnovation Et Valorisation Scientifique\b",
    r"(?i)\bBioinformatics\b",
    r"(?i)\bScientifique\b",
    r"(?i)\bEnvironmental Health\b",

    # Misspellings & Typographical Errors
    r"(?i)\bReseach Scientist\b",
    r"(?i)\bResearch Scienist\b",
    r"(?i)\bReserch Scientist\b",
    r"(?i)\bResarch Scientist\b",
    r"(?i)\bReseach Sientist\b",

    # Case Variations
    r"(?i)\bRESEARCH SCIENTIST\b",
    r"(?i)\bResearch SCIENTIST\b",
    r"(?i)\bresearch scientist\b",
    r"(?i)\bRESEARCH scientist\b",

    # Spanish Variants
    r"(?i)\bCientífico Investigador\b",
    r"(?i)\bInvestigador Científico\b",
    r"(?i)\bCientífico de Investigación\b",
    r"(?i)\bInvestigador\b",
    r"(?i)\bInvestigador Postdoctoral\b",
    r"(?i)\bInvestigador Principal\b",
    r"(?i)\bCientífico Biomédico\b",
    r"(?i)\bCientífico de Laboratorio\b",

    # Hybrid Spanish-English Variants
    r"(?i)\bResearch Científico\b",
    r"(?i)\bResearcher Científico\b",

    # Other Possible Variations (Doctor Forms, Specialist Forms)
    r"(?i)\bBiomedical Researcher\b",
    r"(?i)\bLaboratory Researcher\b",
    r"(?i)\bResearch Specialist\b",
    r"(?i)\bSenior Research Scientist\b",
    r"(?i)\bResearch Director\b",
    r"(?i)\bPrincipal Investigator (Research Scientist)\b",
    r"(?i)\bScientific Lead\b",
    r"(?i)\bClinical Research Scientist\b",
    r"(?i)\bResearch Coordinator\b",
    r"(?i)\bResearch\b",
    r"(?i)\bScoentist\b",
    r"(?i)\bVeterinary Science\b",
]

# Exact matches that should be updated
research_scientist_exact_matches = {
    "Research Scientist",
    "Scientific Researcher",
    "Scientist",
    "Principal Investigator",
    "Laboratory Scientist",
    "Scientific Researcher (Research Scientist)",
    "Research Associate",
    "Postdoctoral Researcher",
    "Biomedical Research Scientist",
    "Reseach Scientist",
    "Research Scienist",
    "Reserch Scientist",
    "Resarch Scientist",
    "Reseach Sientist",
    "Científico Investigador",
    "Investigador Científico",
    "Científico de Investigación",
    "Investigador",
    "Investigador Postdoctoral",
    "Investigador Principal",
    "Científico Biomédico",
    "Científico de Laboratorio",
    "Research Científico",
    "Researcher Científico",
    "Biomedical Researcher",
    "Laboratory Researcher",
    "Research Specialist",
    "Senior Research Scientist",
    "Research Director",
    "Principal Investigator (Research Scientist)",
    "Scientific Lead",
    "Clinical Research Scientist",
    "Research Coordinator",
    "Research",
    'Chief Science Officer',
    'Doctorat En Sciences De La Vie Et De La Sante - Specialisation Vieillissement Et Glycations',
    'Diretora De Pesquisa E Desenvolvimento',
    'Principal Medical Writer',
    'Exosome Specialist',
}

# # Define patterns (these should NOT be changed)
# research_scientist_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

research_scientist_exclusions = {
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
    'General Surgery Research Resident',
    'Epic Resolute Hospital Billing & Physician Billing Senior Analyst',
}

# Create a mask for Research Scientist
mask_research_scientist = df['speciality'].str.contains('|'.join(research_scientist_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(research_scientist_exact_matches)

# mask_research_scientist_exclusions = df['speciality'].str.contains(research_scientist_exclusions, case=False, na=False, regex=True)
mask_research_scientist_exclusions = df['speciality'].isin(research_scientist_exclusions)

# Final mask: Select Research Scientist
mask_research_scientist_final = mask_research_scientist & ~mask_research_scientist_exclusions

# Store the original values that will be replaced
original_research_scientist_values = df.loc[mask_research_scientist_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_research_scientist_final, 'speciality'] = 'Research Scientist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Research Scientist", 'green'))
print(df.loc[mask_research_scientist_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_research_scientist_values = df.loc[mask_research_scientist_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Research Scientist", "cyan"))
for original_research_scientist_value in original_research_scientist_values:
    print(f"✅ {original_research_scientist_value} → Research Scientist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Research Scientist:", 'red'))
print(grouped_research_scientist_values)

# Print summary
matched_count_research_scientist = mask_research_scientist_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Research Scientist: "
        f"{matched_count_research_scientist}",
        'red'))