import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Employee related titles

employee_variants = [
    r"(?i)\bemployee\b",
    r"(?i)\bemployees\b",
    r"(?i)\bworker\b",
    r"(?i)\bworkers\b",
    r"(?i)\bstaff\s?member\b",
    r"(?i)\bteam\s?member\b",
    r"(?i)\bsubordinate\b",
    r"(?i)\bemployee\s?worker\b",
    r"(?i)\bempleado\b",
    r"(?i)\bempleados\b",
    r"(?i)\btrabajador\b",
    r"(?i)\btrabajadores\b",
    r"(?i)\bmiembro\s?de\s?equipo\b",
    r"(?i)\bcolaborador\b",
    r"(?i)\bsubordinado\b",
    r"(?i)\basociado\b",
    # Misspellings
    r"(?i)\bemplyee\b",
    r"(?i)\bemploye\b",
    r"(?i)\bemployye\b",
    r"(?i)\beployee\b",
    r"(?i)\bempoyee\b",
    r"(?i)\bemloyee\b",
    r"(?i)\bemployee\s?worker\b",
    # Other Possible Variations
    r"(?i)\bfull\s?time\s?employee\b",
    r"(?i)\bpart\s?time\s?employee\b",
    r"(?i)\btemporary\s?employee\b",
    r"(?i)\bpermanent\s?employee\b",
    r"(?i)\bcontract\s?employee\b",
    r"(?i)\bvolunteer\b",
    r"(?i)\bstaff\s?member\b",
    r"(?i)\btemporary\s?worker\b",
    r"(?i)\bWorker\b",
    r"(?i)\bEmployee\b",
    r"(?i)\bTechnical Associate\b",
    r"(?i)\bSecretaire De Direction\b",
    r"(?i)\bDaily Worker\b",
    r"(?i)\bCompany Employee\b",
    r"(?i)\bAs Worker\b",
    r"(?i)\bGovt Employee\b",
    r"(?i)\bAssistant Worker\b",
    r"(?i)\bStaff Member\b",
    r"(?i)\bI Am A Social Worker\b",
    r"(?i)\bGeneral Worker\b",
    r"(?i)\bWorker At Shop\b",
    r"(?i)\bGalderma Employee\b",
    r"(?i)\bInjectables Employee\b",
    r"(?i)\bLaborConstruction Worker\b",
    r"(?i)\bAbbvie Worker\b",
    r"(?i)\bFarm Worker\b",
    r"(?i)\bSocial Worker\b",
    r"(?i)\bPrivate Company Employee\b",
    r"(?i)\bWorkers\b",
]

# Exact matches that should be updated
employee_exact_matches = {
    "Employee",
    "Employees",
    "Worker",
    "Workers",
    "Staff",
    "Team Member",
    "Personnel",
    "Team",
    "Associate",
    "Subordinate",
    "Empleado",
    "Empleados",
    "Trabajador",
    "Trabajadores",
    "Miembro de Equipo",
    "Personal",
    "Colaborador",
    "Subordinado",
    "Asociado",
    "Empllyee",
    "Employe",
    "Employye",
    "Eployee",
    "Empoyee",
    "Emloyee",
    "Employee Worker",
    "Full Time Employee",
    "Part Time Employee",
    "Temporary Employee",
    "Permanent Employee",
    "Contract Employee",
    "Intern",
    "Volunteer",
    "Staff Member",
    "Temporary Worker",
    "Patient/Other",
    'Associate',
    'associate',
    'Direction',
    'direction',
    'staff',
    'Staff',
    'Senior Clerk',
}

# Define patterns (these should NOT be changed)
employee_exclusions = {
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
    'Volunteer Professor Of Dermatology',
    'Volunteer Assistant Clinical Professor',
}

# Create a mask for Employee
mask_employee = df['speciality'].str.contains('|'.join(employee_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(employee_exact_matches)
mask_employee_exclusions = df['speciality'].isin(employee_exclusions)

# Final mask: Select Employee
mask_employee_final = mask_employee & ~mask_employee_exclusions

# Store the original values that will be replaced
original_employee_values = df.loc[mask_employee_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_employee_final, 'speciality'] = 'Employee'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Employee", 'green'))
print(df.loc[mask_employee_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_employee_values = df.loc[mask_employee_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Employee", "cyan"))
for original_employee_value in original_employee_values:
    print(f"✅ {original_employee_value} → Employee")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Employee:", 'red'))
print(grouped_employee_values)

# Print summary
matched_count_employee = mask_employee_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Employee: "
        f"{matched_count_employee}",
        'red'))