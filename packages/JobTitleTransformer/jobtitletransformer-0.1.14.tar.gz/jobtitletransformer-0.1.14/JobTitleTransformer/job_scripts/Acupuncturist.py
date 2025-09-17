import pandas as pd
import re
import unicodedata
import sys
import os
from termcolor import colored

acupuncturist_exact_matches = {
    'Acupuncturist',
    'Licensed Acupuncturist',
    'Certified Acupuncturist',
    'Acupuncture Practitioner',
    'Licensed Acupuncture Practitioner',
    'Traditional Chinese Medicine Acupuncturist',
    'Traditional Chinese Medicine Practitioner',
    'TCM Acupuncturist',
    'TCM Practitioner',
    'Acupuncture Specialist',
    'Acupuncture Therapist',
    'Acupuncture Doctor',
    'Acupuncture Specialist Doctor',
    'Doctor of Acupuncture',
    'Doctor of Traditional Chinese Medicine',
    'Doctor of Acupuncture and Oriental Medicine',
    'Doctor of Oriental Medicine',
    'Licensed Acupuncture Doctor',
    'Acupuncture and Oriental Medicine Practitioner',
    'Acupuncture and Herbal Medicine Specialist',
    'Acupuncturist MD',
    'Acupuncturist with Oriental Medicine',
    'Licensed Practitioner of Acupuncture',
    'Acupuncturist Doctor',
    'Acupuncturist and Herbalist',
    'Acupuncture Therapist MD',
    'Acupuncturist (TCM)',
    'Acupuncture Therapy Specialist',
    'Licensed Chinese Medicine Practitioner',
    'Chinese Medicine Acupuncturist',
    'Acupuncture and Acupressure Specialist',
    'Licensed Acupuncture and Herbal Medicine Practitioner',
    'Acupuncture and TCM Doctor',
    'Chinese Medicine Acupuncturist',
    'Acupuncturist Practitioner (TCM)',
    'Acupuncture and TCM Specialist',
    'Acupuncturist L.Ac',
    'Acupunctureist',
    'Acupunture Speciallist',
    'Acuprunture Specialist',
    'Acupunturist Specialist',
    'Acupuncturist Dipl. Ac',
    'Acupuncturist D.O.M.',
    'Doctor of Oriental Medicine Acupuncturist',
    'Acupunture',
    'Acupunturist',
    'Acupruncturist',
    'Acuponcturist',
    'Acupuncturist',
    'Acupuntureist',
    'Acupunturist doctor',
    'acupuncturist with oriental medicine',
    'Acupunture and oriental medicine',
    'Certified Traditional Chinese Medicine Acupuncturist',
    'Chinese medicine acupunturist',
    'Chinese medcine acupuncturist',
    'Acupuncturist TCM',
    'acupuncture practioner',
    'Doctor of Acupuncture and Chinese Medicine',
    'Licensed Acupuncture and Chinese Medicine Practitioner',
    'Certified Acupuncture Specialist',
    'TCM acupuncturist practitioner',
    'TCM acupuncture practitioner',
    'AcupuncturIst Md',
    'AcupuncturIst D.o.m',
    'Tcm acupuncturist',
    'tcM acupuncturist',
    'acupuncturist (tcm)',
    'tcm practicioner',
    'tcm practioner',
    'acupuncture',
    'acupuncturist',
    'aCuPuncturist',
    'aCUPUNCTURIST',
    'acupuncturIst',
    'Acupunture therapist',
    'acupunture practitioner',
    'acupuncture therapiest',
    'Doctor of acupuncture and chinese medicine',
    'tcm acupunturist',
    'acupuncturist and herbalist',
    'AcupuncturIst and HerbalIst',
    'Acupuncurist doctor',
# Variations for common typos and case mistakes
}

# Apply transformation and track changes
mask_acupuncturist = df['speciality'].str.contains('Acupuncturist', case=False, na=False, regex=True) | \
                     df['speciality'].isin(acupuncturist_exact_matches)

# Store the original values that will be replaced
original_acupuncturist_values = df.loc[mask_acupuncturist, 'speciality'].unique()

# Update the speciality column
df.loc[mask_acupuncturist, 'speciality'] = 'Acupuncturist'

# Check AFTER updating
print(colored("\nUnique values AFTER updating: Acupuncturist", 'green'))
print(df.loc[mask_acupuncturist, 'speciality'].unique())

# GroupBy to count how many records were replaced by the new value
grouped_acupuncturist_values = df.loc[mask_acupuncturist, 'speciality'].value_counts()

# Print the exact replacements
print(colored("\nReplaced Values: Acupuncturist", "cyan"))
for original_acupuncturist_value in original_acupuncturist_values:
    print(f"✅ {original_acupuncturist_value} → Acupuncturist")

# GroupBy after replacement (to show the new value)
print(colored("\nGroupBy counts AFTER replacing with Acupuncturist:", 'red'))
print(grouped_acupuncturist_values)

# Print summary
matched_count_acupuncturist = mask_acupuncturist.sum()

# Print results
print(colored(f"\nTotal values matched and changed (Stage 1) to Acupuncturist: {matched_count_acupuncturist}", 'red'))
