import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Distributor related titles

distributor_variants = [
    r"(?i)\bdistributor\b",
    r"(?i)\bdistributors\b",
    r"(?i)\bwholesaler\b",
    r"(?i)\bwholesale\s?distributor\b",
    r"(?i)\bsupplier\b",
    r"(?i)\bproduct\s?supplier\b",
    r"(?i)\bvendor\b",
    r"(?i)\bsales\s?representative\b",
    r"(?i)\bdistribuidor\b",
    r"(?i)\bdistribuidores\b",
    r"(?i)\bmayorista\b",
    r"(?i)\bsuministrador\b",
    r"(?i)\bvendedor\b",
    r"(?i)\brepresentante\s?de\s?ventas\b",
    # Misspellings
    r"(?i)\bdistrbutor\b",
    r"(?i)\bdisttributor\b",
    r"(?i)\bdistrbutors\b",
    r"(?i)\bdistbtr\b",
    r"(?i)\bdistrubutor\b",
    # Other Possible Variations
    r"(?i)\bdistribution\s?manager\b",
    r"(?i)\bdistribution\s?coordinator\b",
    r"(?i)\bsales\s?distributor\b",
    r"(?i)\bsupply\s?chain\s?distributor\b",
    r"(?i)\bdelivery\s?distributor\b",
    r"(?i)\bdealer\b",
    r"(?i)\bManufacturing\b",
    r"(?i)\bDistribucion Nuticosmetica\b",
    r"(?i)\bFrangrance & Cosmetic\b",
    r"(?i)\bFrangrance & Cosmetic\b",
    r"(?i)\bComerciante\b",
    r"(?i)\bDistributer\b",
    r"(?i)\bSourcing Agent\b",
    r"(?i)\bIndependent Rep\b",
    r"(?i)\bBiomaterials\b",
    r"(?i)\bComprador\b",
    r"(?i)\bDistributeur\b",
    r"(?i)\bDistributorHolistic Skin Expert\b",
    r"(?i)\bDistruteur\b",
    r"(?i)\bBiomedical Equipment\b",
]

# Exact matches that should be updated
distributor_exact_matches = {
    "Distributor",
    "Distributors",
    "Wholesaler",
    "Wholesale Distributor",
    "Supplier",
    "Product Supplier",
    "Vendor",
    "Sales Representative",
    "Distribuidor",
    "Distribuidores",
    "Mayorista",
    "Sumistrador",
    "Vendedor",
    "Representante de Ventas",
    "Distrbutor",
    "Disttributor",
    "Distbtr",
    "Distrubutor",
    "Distribution Manager",
    "Distribution Coordinator",
    "Sales Distributor",
    "Supply Chain Distributor",
    "Delivery Distributor",
    "Dealer",
    'Orthopedics Instruments',
    'Wholesale Trader Of Gluathione & Dermal Fillers',
    'Wholesale Accounts Director',
    'Equipment',
    'Aesthetic seller',
}

# Define patterns (these should NOT be changed)
distributor_exclusions = {
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

# Create a mask for Distributor
mask_distributor = df['speciality'].str.contains('|'.join(distributor_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(distributor_exact_matches)
mask_distributor_exclusions = df['speciality'].isin(distributor_exclusions)

# Final mask: Select Distributor
mask_distributor_final = mask_distributor & ~mask_distributor_exclusions

# Store the original values that will be replaced
original_distributor_values = df.loc[mask_distributor_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_distributor_final, 'speciality'] = 'Distributor'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Distributor", 'green'))
print(df.loc[mask_distributor_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_distributor_values = df.loc[mask_distributor_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Distributor", "cyan"))
for original_distributor_value in original_distributor_values:
    print(f"✅ {original_distributor_value} → Distributor")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Distributor:", 'red'))
print(grouped_distributor_values)

# Print summary
matched_count_distributor = mask_distributor_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Distributor: "
        f"{matched_count_distributor}",
        'red'))