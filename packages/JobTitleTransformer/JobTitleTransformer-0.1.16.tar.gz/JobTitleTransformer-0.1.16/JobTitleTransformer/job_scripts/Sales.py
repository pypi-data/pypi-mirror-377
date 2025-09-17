import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Sales related titles

sales_variants = [
    # Standard Titles & Variants
    r"(?i)\bSales\b",
    r"(?i)\bSales Representative\b",
    r"(?i)\bSales Manager\b",
    r"(?i)\bSales Director\b",
    r"(?i)\bSales Specialist\b",
    r"(?i)\bSales Executive\b",
    r"(?i)\bAccount Manager\b",
    r"(?i)\bBusiness Development Representative\b",
    r"(?i)\bSales Associate\b",
    r"(?i)\bAccount Executive\b",
    r"(?i)\bOperations Manager\b",
    r"(?i)\bRsm\b",
    r"(?i)\bAesthetic Accounting\b",
    r"(?i)\bSalesEvent Coordinator\b",
    r"(?i)Sales",
    r"(?i)Visitadora Medica",
    r"(?i)Sale Manager",
    r"(?i)Financial Manager",
    r"(?i)\bDemand Generation Manager\b",
    r"(?i)\bDirecteur Commercial\b",
    r"(?i)\bResponsavel Comercial\b",
    r"(?i)\bAccount Exec\b",
    r"(?i)\bCommercial\b",
    r"(?i)\bResponsable\b",
    r"(?i)\bSale\b",
    r"(?i)\bMgr Sr Dev - Botox Cosmetic Us Facial Aes Sales\b",
    r"(?i)\bE-Commerce\b",
    r"(?i)\bSalesClient\b",
    r"(?i)\bCommerciale\b",
    r"(?i)\bAccount Executive\b",

    # Misspellings & Typographical Errors
    r"(?i)\bSlaes\b",
    r"(?i)\bSals\b",
    r"(?i)\bSlaesman\b",
    r"(?i)\bSalesman\b",
    r"(?i)\bSalses\b",

    # Case Variations
    r"(?i)\bSALES\b",
    r"(?i)\bsales\b",
    r"(?i)\bSaLeS\b",
    r"(?i)\bSALESMAN\b",

    # Spanish Variants
    r"(?i)\bVentas\b",
    r"(?i)\bRepresentante de Ventas\b",
    r"(?i)\bGerente de Ventas\b",
    r"(?i)\bDirector de Ventas\b",
    r"(?i)\bEspecialista en Ventas\b",
    r"(?i)\bEjecutivo de Ventas\b",
    r"(?i)\bAsociado de Ventas\b",
    r"(?i)\bDesarrollo de Negocios en Ventas\b",
    r"(?i)\bRepresentante de Ventas\b",

    # Hybrid Spanish-English Variants
    r"(?i)\bSales Representante\b",
    r"(?i)\bSales Gerente de Ventas\b",
    r"(?i)\bSales Ejecutivo\b",
    r"(?i)\bBusiness Development Ventas\b",

    # Other Possible Variations (Doctor Forms, Specialist Forms)
    r"(?i)\bAccount Sales Manager\b",
    r"(?i)\bClient Relations Specialist\b",
    r"(?i)\bBusiness Development Sales\b",
    r"(?i)\bSales Lead Specialist\b",
    r"(?i)\bRegional Sales Manager\b",
    r"(?i)\bBilling Contact\b",
    r"(?i)\bAccountant\b",
    r"(?i)\bCOMMERICIAL ASSISTANT\b",
    r"(?i)Sales",
]

# Exact matches that should be updated
sales_exact_matches = {
    "Sales",
    "Sales Representative",
    "Sales Manager",
    "Sales Director",
    "Sales Specialist",
    "Sales Executive",
    "Account Manager",
    "Business Development Representative",
    "Sales Associate",
    "Slaes",
    "Sals",
    "Slaesman",
    "Salesman",
    "Salses",
    "SALES",
    "sales",
    "SaLeS",
    "SALESMAN",
    "Ventas",
    "Representante de Ventas",
    "Gerente de Ventas",
    "Director de Ventas",
    "Especialista en Ventas",
    "Ejecutivo de Ventas",
    "Asociado de Ventas",
    "Desarrollo de Negocios en Ventas",
    "Sales Representante",
    "Sales Gerente de Ventas",
    "Sales Ejecutivo",
    "Business Development Ventas",
    "Account Sales Manager",
    "Client Relations Specialist",
    "Business Development Sales",
    "Sales Lead Specialist",
    "Regional Sales Manager",
    "Specialized StoreConcept Store",
    'Account Coordinator',
    'Finance',
    'Account Director',
    'Group Account Director',
    'Commercialdirector',
    'Franchise Manager',
    'Comercial',
    'Dir Comercial',
    'National Accounts Director',
    'Teleshopping',
    'Ready-To-Wear Fashion Store',
    'Travel Retail Duty Free',
    'Account Directpr',
    'AE',
}

# # Define patterns (these should NOT be changed)
# sales_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

sales_exclusions = {
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

# Create a mask for Sales
mask_sales = df['speciality'].str.contains('|'.join(sales_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(sales_exact_matches)

# mask_sales_exclusions = df['speciality'].str.contains(sales_exclusions, case=False, na=False, regex=True)
mask_sales_exclusions = df['speciality'].isin(sales_exclusions)

# Final mask: Select Sales
mask_sales_final = mask_sales & ~mask_sales_exclusions

# Store the original values that will be replaced
original_sales_values = df.loc[mask_sales_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_sales_final, 'speciality'] = 'Sales'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Sales", 'green'))
print(df.loc[mask_sales_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_sales_values = df.loc[mask_sales_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Sales", "cyan"))
for original_sales_value in original_sales_values:
    print(f"✅ {original_sales_value} → Sales")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Sales:", 'red'))
print(grouped_sales_values)

# Print summary
matched_count_sales = mask_sales_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Sales: "
        f"{matched_count_sales}",
        'red'))