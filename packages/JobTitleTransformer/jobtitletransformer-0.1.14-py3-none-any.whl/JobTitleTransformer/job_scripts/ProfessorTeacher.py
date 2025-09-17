import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Professor Teacher related titles

professor_variants = [
    # Standard Titles & Variants
    r"(?i)\bProfessor Teacher\b",
    r"(?i)\bProfessor & Teacher\b",
    r"(?i)\bProfessor-Teacher\b",
    r"(?i)\bProfessor / Teacher\b",
    r"(?i)\bProf. Teacher\b",
    r"(?i)\bProf Teacher\b",
    r"(?i)\bProf.\b",
    r"(?i)\bProfessor\b",
    r"(?i)\bTeacher\b",
    r"(?i)\bTrainer\b",
    r"(?i)\bPhd\b",
    r"(?i)\bEducation\b",
    r"(?i)\bDean\b",
    r"(?i)\bPrinicpal\b",
    r"(?i)\bTeaching\b",
    r"(?i)\bProf\b",
    r"(?i)\bDean\b",
    r"(?i)\bAcademic\b",
    r"(?i)\bProfessir\b",
    r"(?i)\bCosmetologistTeacher\b",
    r"(?i)\bProgram Director\b",
    r"(?i)\bUniversity ProfessorOtolaryngologyFacial Plastic\b",

    # Misspellings & Typographical Errors
    r"(?i)\bProffesor Teacher\b",
    r"(?i)\bProfesor Teacher\b",
    r"(?i)\bProfesser Teacher\b",
    r"(?i)\bProfessar Teacher\b",
    r"(?i)\bProffesor Techer\b",
    r"(?i)\bProfessor Techer\b",
    r"(?i)\bProfesor Techer\b",
    r"(?i)\bProfesseur Teacher\b",
    r"(?i)\bProfessor Teachar\b",
    r"(?i)\bProf. Teachr\b",

    # Case Variations
    r"(?i)\bPROFESSOR TEACHER\b",
    r"(?i)\bprofessor teacher\b",
    r"(?i)\bProfEsSor TeaChEr\b",
    r"(?i)\bprOFesSor TeaCHer\b",

    # Spanish Variants
    r"(?i)\bProfesor Docente\b",
    r"(?i)\bProfesor Maestro\b",
    r"(?i)\bDocente Universitario\b",
    r"(?i)\bCatedrático Docente\b",
    r"(?i)\bProfesor Académico\b",
    r"(?i)\bInstructor Educativo\b",

    # Hybrid Spanish-English Variants
    r"(?i)\bProfessor Docente\b",
    r"(?i)\bProfesor Teacher\b",
    r"(?i)\bProf Teacher Académico\b",

    # Other Possible Variations (Doctor Forms, Specialist Forms)
    r"(?i)\bSenior Professor Teacher\b",
    r"(?i)\bLead Professor Teacher\b",
    r"(?i)\bHead of Teaching & Professorship\b",
    r"(?i)\bAcademic Professor\b",
    r"(?i)\bEducational Professor\b",
    r"(?i)\bUniversity Professor Teacher\b",
    r"(?i)\bLecturer & Professor\b",
    r"(?i)\bTeaching Professor\b",
    r"(?i)\bMA\b",
    r"(?i)\bM A\b",
    r"(?i)\bMa\b",
    r"(?i)\bProfessorTeacher\b",
    r"(?i)\bAcademic Program Administrator\b",
    r"(?i)\bKazakh National Medical University\b",
    r"(?i)\bEducator\b",
]

# Exact matches that should be updated
professor_exact_matches = {
    "Professor Teacher",
    "Professor & Teacher",
    "Professor-Teacher",
    "Professor / Teacher",
    "Prof. Teacher",
    "Prof Teacher",
    "Proffesor Teacher",
    "Professer Teacher",
    "Professar Teacher",
    "Proffesor Techer",
    "Professor Techer",
    "Profesor Techer",
    "Professeur Teacher",
    "Professor Teachar",
    "Prof. Teachr",
    "Profesor Docente",
    "Profesor Maestro",
    "Docente Universitario",
    "Catedrático Docente",
    "Profesor Académico",
    "Instructor Educativo",
    "Professor Docente",
    "Profesor Teacher",
    "Prof Teacher Académico",
    "Senior Professor Teacher",
    "Lead Professor Teacher",
    "Head of Teaching & Professorship",
    "Academic Professor",
    "Educational Professor",
    "University Professor Teacher",
    "Lecturer & Professor",
    "Teaching Professor",
    "Principal",
    "ProfessorTeacher",
    'Course Coordinator',
    'Master Of Science',
    'Adjunct Instructor',
    'Director Riphah International University Islamabad-Pakistan',
    'Learning & Development',
    'Assistant ProfessorMD',
    'Mf',
    'Cosmetology Instructor',
    'Cosmetology Career Technology Instructor',
    'Cosmetology1 Instructor',
    'High School Cosmetology Instructor',
    'Instructor Of Cosmetology',
    'Vocational Instructor Of Cosmetology',
    'Director PIR Training',
}

# # Define patterns (these should NOT be changed)
# professor_exclusions = r'\b(?:Plastic)|(?:Physician)\b'

professor_exclusions = {
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
    'Sales Trainer',
    'Rn Clinical Trainer',
}

# Create a mask for Professor Teacher
mask_professor = df['speciality'].str.contains('|'.join(professor_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(professor_exact_matches)

# mask_professor_exclusions = df['speciality'].str.contains(professor_exclusions, case=False, na=False, regex=True)
mask_professor_exclusions = df['speciality'].isin(professor_exclusions)

# Final mask: Select Professor Teacher
mask_professor_final = mask_professor & ~mask_professor_exclusions

# Store the original values that will be replaced
original_professor_values = df.loc[mask_professor_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_professor_final, 'speciality'] = 'Professor Teacher'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Professor Teacher", 'green'))
print(df.loc[mask_professor_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_professor_values = df.loc[mask_professor_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Professor Teacher", "cyan"))
for original_professor_value in original_professor_values:
    print(f"✅ {original_professor_value} → Professor Teacher")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Professor Teacher:", 'red'))
print(grouped_professor_values)

# Print summary
matched_count_professor = mask_professor_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Professor Teacher: "
        f"{matched_count_professor}",
        'red'))