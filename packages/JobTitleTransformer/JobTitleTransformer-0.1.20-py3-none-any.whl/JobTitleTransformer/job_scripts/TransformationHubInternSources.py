import pandas as pd
import numpy as np
import re
from nltk.corpus import stopwords
import unicodedata
import sys
import os
from termcolor import colored

# Remove the original_speciality column as no longer needed
df = df.drop(columns = ['original_speciality'])

# Declare the list of values available in main_title table
list_of_job_titles = [
    'Acupuncturist',
    'Advanced Registered Nurse Practitioner (ARNP)',
    'Aesthetic & Anti-aging Physician',
    'Aesthetic & Plastic Surgeon',
    'Aesthetic Physician',
    'Alternative Medicine Physician',
    'Anaesthesist',
    'Anatomist',
    'Andrologist',
    'Angiologist Phlebologist',
    'Anti-aging Physician',
    'Biologist Biochemist',
    'Biomedical Physician',
    'Cardiologist',
    'Clinic Manager',
    'Clinical Staff',
    'Company CEO',
    'Company Manager',
    'Company Medical Staff',
    'Company Representative',
    'Consultant',
    'Cosmetic Dermatologist',
    'Cosmetic Surgeon',
    'Cosmetologist MD',
    'Cytologist',
    'Dental Assistant',
    'Dental Surgeon',
    'Dentist',
    'Dermatologic Surgeon',
    'Dermatologist',
    'Distributor',
    'Employee',
    'Endocrinologist',
    'ENT Ear Nose Throat Physician',
    'Esthetician Cosmetician',
    'Event Manager',
    'Facial Plastic Surgeon',
    'General Physician',
    'General Surgeon',
    'Genetician',
    'Geriatrist',
    'Gynecologist Obstetrician',
    'Hair Transplant Surgeon',
    'Head of department',
    'Hematologist',
    'Hospital Manager',
    'Immunologist',
    'Influencer',
    'Internal Medicine',
    'Laboratory Medicine',
    'Lawyer',
    'Legal Counsel',
    'Licensed Practical Nurse (LPN)',
    'Marketing Manager',
    'Maxillofacial Surgeon',
    'Medical Advisor',
    'Medical Spa Manager',
    'Neonatologist',
    'Neurologist',
    'Neurophysiologist',
    'Non medical Staff',
    'Nurse Practitioner (NP)',
    'Nutritionist',
    'Oculoplastic Surgeon',
    'Oncologist',
    'Ophthalmologist',
    'Oral and Maxillofacial Surgeon',
    'Orthodontist',
    'Orthopedist',
    'Owner',
    'Pathologist',
    'Pediatrician',
    'Pharmacist',
    'Pharmacologist',
    'Photographer',
    'Physician Assistant',
    'Physiotherapist',
    'Plastic and Reconstructive Surgeon',
    'Plastic Surgeon',
    'Practice Manager',
    'Press',
    'Product Project Manager',
    'Professor Teacher',
    'Psychiatrist',
    'Psychologist',
    'Psychotherapist',
    'Radiologist',
    'Registered Nurse (RN)',
    'Research Scientist',
    'Rheumatologist',
    'Sales',
    'Sports Medicine Physician',
    'Stomatologist',
    'Student Resident Fellow',
    'Trichologist',
    'Urologist',
    'Vascular Surgeon',
    'ENT Head and Neck Specialist', # FOR EUROGIN
	'General Manager', # Old Value and doesnt exists in main title
	'Nurse' # Old Value and doesnt exists in main title
]

# Filter non-matching job titles after processing
not_transformed_job_titles = pd.DataFrame(df[~df['speciality'].isin(list_of_job_titles)])

# GroupBy to count how many records were not transformed to business format
grouped_not_transformed_job_titles = not_transformed_job_titles['speciality'].value_counts()

# Print non-matching titles and their count
print(colored("\nRemaining Job Titles that have not been transformed to business value format after processing:", 'red'))
print(tab(grouped_not_transformed_job_titles.head(100).reset_index(), headers=['Speciality', 'Count'], tablefmt='psql'))

# Print count of non-matching job titles
print(colored(f"Count of non-matching job titles after processing: {not_transformed_job_titles.shape[0]}", 'red'))

# Filtering logic - Job Title Is Other, Unknown, an integer or not relevant after processing
df_records_job_title_other = not_transformed_job_titles[
    not_transformed_job_titles['speciality'].astype(str).str.strip().isin(['Other', 'Unknown', 'None']) |  # Remove specified values
    not_transformed_job_titles['speciality'].astype(str).str.match(r'^\d+$') |  # Remove numbers only
    not_transformed_job_titles['speciality'].astype(str).str.match(r'^[A-Za-z]$')  # Remove single letters
]

# Print records were Job Title Is Other, Unknown, an integer or not relevant after processing
print(colored("\nJob Title Is Other, Unknown, an integer or not relevant:", 'red'))
print(tab(df_records_job_title_other.head(10).reset_index(),  headers='keys', tablefmt='psql'))

# Print count of records were Job Title Is Other, Unknown, an integer or not relevant after processing
print(colored(f"\nCount Job Title Is Other, Unknown, an integer or not relevant: {df_records_job_title_other.shape[0]}", 'red'))

print(colored("\nRecords were job_title has been transformed:", 'red'))
# Filter only transformed records (those that were successfully replaced)
transformed_job_titles = df[df['speciality'].isin(list_of_job_titles)].copy()
print(tab(transformed_job_titles.head(10), headers='keys', tablefmt='psql'))

# create a copy for concat operation during ML Stages
df_transformed = transformed_job_titles.copy()
print(colored("\nFinal Dataframe at the end of processing Job Titles Pipeline", "red", attrs=["bold"]))
print(tab(df_transformed.head(10), headers='keys', tablefmt='psql'))

# Print count of records with transformed job titles
print(colored(f"\nCount of transformed job titles after Processing: {transformed_job_titles.shape[0]}", 'red'))

# Get the row counts of df_test and df
count_not_transformed_job_titles = len(not_transformed_job_titles)

# For Programmer's Review
if count_not_transformed_job_titles > 0:
    print(colored(
        "\nThe count of not transformed job titles is greater than 0. The programmer needs to review these values "
        "\nbefore proceeding with further execution.", 'red'))

    # Print the count for debugging
    print(f"Count of not transformed job titles: {count_not_transformed_job_titles}")

    # Exit the pipeline
    sys.exit("Exiting pipeline as programmer needs to review the non-transformed job titles.")
else:
    print(colored(
        "\nThe count of transformed job titles is 0. The pipeline proceeds to the next stages.", 'green'))

    # Print the count for confirmation
    print(f"Count of not transformed job titles: {count_not_transformed_job_titles}")

# Concat Frames for next stage of execution
df = pd.concat([
    df,
    not_transformed_job_titles,
    df_other,
    df_CWS
], ignore_index=True)

print(colored("\nFinal Dataframe at the end of processing Job Titles Pipeline that will be sent for further execution", "red", attrs=["bold"]))
print(tab(df_transformed.head(10), headers='keys', tablefmt='psql'))

# Print count of records with transformed job titles
print(colored(f"\nCount of records at the end of processing Job Titles Pipeline that will be sent for further execution: {transformed_job_titles.shape[0]}", 'red'))

# Testing

# Get the row counts of df_test and df
count_df_test = len(df_test)
count_df = len(df)

# Check if the counts match
if count_df_test == count_df:
    print(colored(
        "\nThe count of source dataframe before processing job title transformation stages and after processing job "
        "\ntitle transformation pipeline remains same/equal. Thus, the pipeline will proceed its execution.", 'green'))
else:
    print(colored(
        "\nThe count of source dataframe before processing job title transformation stages and after processing job "
        "\ntitle transformation pipeline are not same/equal. Thus, the pipeline will stop its execution, you need to "
        "\nreview the pipeline.", 'red'))

    # Print the counts
    print(f"Count of df_test: {count_df_test}")
    print(f"Count of df: {count_df}")

    # Exit the program if the counts don't match
    sys.exit("Exiting pipeline due to mismatched record counts.")

# Tip: Uncomment the below if you want to club / pool all the list of variants and exact match DICT into one list and one DICT

# # Initialize lists to hold all variants and exact matches
# all_variants = []
# all_exact_matches = []
#
# # Create a snapshot of all global variables
# global_vars = globals().copy()
#
# # Iterate over the keys in the snapshot of globals
# for var_name, var_value in global_vars.items():
#     if var_name.endswith('_variants'):  # If the variable is a _variants list
#         all_variants.extend(var_value)  # Add the variants to the all_variants list
#     elif var_name.endswith('_exact_matches'):  # If the variable is a _exact_matches set or list
#         if isinstance(var_value, dict):
#             all_exact_matches.extend(var_value.values())  # Add the exact match values to the all_exact_matches list
#         elif isinstance(var_value, (set, list)):  # Check if it's a set or a list
#             all_exact_matches.extend(var_value)  # Use extend to add the elements
#
# # Check the results
# print("All Variants:", all_variants)
# print("All Exact Matches:", all_exact_matches)


