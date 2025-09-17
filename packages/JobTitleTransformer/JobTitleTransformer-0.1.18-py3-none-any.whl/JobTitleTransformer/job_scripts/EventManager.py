import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

# Define regex patterns for Event Manager related titles

event_manager_variants = [
    r"(?i)\bevent\s?manager\b",
    r"(?i)\bevent\s?planner\b",
    r"(?i)\bevent\s?coordinator\b",
    r"(?i)\bevent\s?supervisor\b",
    r"(?i)\bevent\s?director\b",
    r"(?i)\bevent\s?organizer\b",
    r"(?i)\bevent\s?planning\s?manager\b",
    r"(?i)\bevent\s?production\s?manager\b",
    r"(?i)\bevent\s?operations\s?manager\b",
    r"(?i)\bevent\s?staff\s?manager\b",
    r"(?i)\bevent\s?marketing\s?manager\b",
    r"(?i)\bevent\s?project\s?manager\b",
    r"(?i)\bevent\s?management\s?specialist\b",
    r"(?i)\bevent\s?consultant\b",
    r"(?i)\bevent\s?strategist\b",
    r"(?i)\bevent\s?administrator\b",
    r"(?i)\bTrade Show\b",
    r"(?i)\bEvents Manager\b",
    r"(?i)Events",
    r"(?i)Tradeshow",
    r"(?i)Exhibition Manager",
    r"(?i)\bChef De Projet Congres\b",
    r"(?i)\bConfirm The Booth\b",
    r"(?i)Mice",
    r"(?i)Teamlead Congresses",
    r"(?i)Conference Producer",
    r"(?i)Booth Staff",
    r"(?i)Exhibitions",
    r"(?i)Exhibition",
    r"(?i)\bCongress Agency\b",
    r"(?i)\bCongress\b",
    r"(?i)\bExpo Man\b",
    r"(?i)\bOnsite Registration Support\b",
    r"(?i)\bSymposia&Congress Expert\b",
    r"(?i)\bConference\b",
    r"(?i)\bEvent Booking\b",
    r"(?i)\bHost\b",
    r"(?i)\bEvent Services Manager\b",
    r"(?i)\bExhibit Planning\b",
    r"(?i)\bEvent Assistant\b",
    r"(?i)\bEvent Planning\b",
    r"(?i)\bConvention Coordinator\b",
    r"(?i)\bConvention Manager\b",

    # Spanish variants
    r"(?i)\bgerente\s?de\s?eventos\b",  # Spanish form (event manager)
    r"(?i)\bplanificador\s?de\s?eventos\b",  # Spanish form (event planner)
    r"(?i)\bcoordinador\s?de\s?eventos\b",  # Spanish form (event coordinator)
    r"(?i)\borganizador\s?de\s?eventos\b",  # Spanish form (event organizer)
    r"(?i)\bdirector\s?de\s?eventos\b",  # Spanish form (event director)
    r"(?i)\bresponsable\s?de\s?eventos\b",  # Spanish form (event supervisor)
    r"(?i)\bplanificador\s?de\s?eventos\s?certificado\b",  # Spanish form (certified event planner)
    r"(?i)\bcoordinador\s?de\s?eventos\s?profesional\b",  # Spanish form (professional event coordinator)
    r"(?i)\bcoordinador\s?de\s?eventos\s?certificado\b",  # Spanish form (certified event coordinator)

    # Other possible variations
    r"(?i)\bmanager\s?of\s?events\b",
    r"(?i)\bplanner\s?of\s?events\b",
    r"(?i)\bcoordinator\s?of\s?events\b",
    r"(?i)\bevent\s?project\s?coordinator\b",
    r"(?i)\bevent\s?program\s?manager\b",
    r"(?i)\bcelebration\s?planner\b",
    r"(?i)\bconference\s?organizer\b",
    r"(?i)\bfestival\s?organizer\b",
    r"(?i)\bmeeting\s?planner\b",
    r"(?i)\bparty\s?planner\b",
    r"(?i)\bconference\s?manager\b",
    r"(?i)\bconvention\s?planner\b",
    r"(?i)\bcorporate\s?event\s?manager\b",
]

# Exact matches that should be updated
event_manager_exact_matches = {
    "Event Manager",
    "Event Planner",
    "Event Coordinator",
    "Event Supervisor",
    "Event Director",
    "Event Organizer",
    "Event Planning Manager",
    "Event Production Manager",
    "Event Operations Manager",
    "Event Staff Manager",
    "Event Marketing Manager",
    "Event Project Manager",
    "Event Management Specialist",
    "Event Consultant",
    "Event Strategist",
    "Event Administrator",
    # Spanish form matches
    "Gerente de Eventos",
    "Planificador de Eventos",
    "Coordinador de Eventos",
    "Organizador de Eventos",
    "Director de Eventos",
    "Responsable de Eventos",
    "Planificador de Eventos Certificado",
    "Coordinador de Eventos Profesional",
    "Coordinador de Eventos Certificado",
    'Attendee Manager',
    'Meeting Producer',
    'Show Coordinator',
    'Booth Operator',
    'Director of Conferences Logistics',
}

# Define patterns (these should NOT be changed)
event_manager_exclusions = {
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

# Create a mask for Event Manager
mask_event_manager = df['speciality'].str.contains('|'.join(event_manager_variants), case = False,
                                                          na = False, regex = True) | \
                            df['speciality'].isin(event_manager_exact_matches)
mask_event_manager_exclusions = df['speciality'].isin(event_manager_exclusions)

# Final mask: Select Event Manager
mask_event_manager_final = mask_event_manager & ~mask_event_manager_exclusions

# Store the original values that will be replaced
original_event_manager_values = df.loc[mask_event_manager_final, 'speciality'].unique()

# Update the speciality column based on exact matches
df.loc[mask_event_manager_final, 'speciality'] = 'Event Manager'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Event Manager", 'green'))
print(df.loc[mask_event_manager_final, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_event_manager_values = df.loc[mask_event_manager_final, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Event Manager", "cyan"))
for original_event_manager_value in original_event_manager_values:
    print(f"✅ {original_event_manager_value} → Event Manager")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Event Manager:", 'red'))
print(grouped_event_manager_values)

# Print summary
matched_count_event_manager = mask_event_manager_final.sum()

# Print results
print(
    colored(
        f"\nTotal values matched and changed (Stage 1) to Event Manager: "
        f"{matched_count_event_manager}",
        'red'))