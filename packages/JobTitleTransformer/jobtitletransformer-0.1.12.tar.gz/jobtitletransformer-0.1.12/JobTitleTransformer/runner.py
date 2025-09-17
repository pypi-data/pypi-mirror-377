import os
from termcolor import colored
import pkg_resources
import pandas as pd


def run_pipeline(df):
    # List of scripts in order of execution
    ordered_scripts = [
        "_encode_decode.py",
        "Acupuncturist.py",
        "ARNP.py",
        "AestheticAntiAgingPhy.py",
        "AestheticPlasticSurgeon.py",
        "AestheticPhysician.py",
        "AlternativeMedicinePhysician.py",
        "Anaesthesist.py",
        "Anatomist.py",
        "Andrologist.py",
        "AngiologistPhlebologist.py",
        "AntiagingPhysician.py",
        "BiologistBiochemist.py",
        "BiomedicalPhysician.py",
        "Cardiologist.py",
        "ClinicManager.py",
        "ClinicalStaff.py",
        "CompanyCEO.py",
        "CompanyManager.py",
        "CompanyMedicalStaff.py",
        "CompanyRepresentative.py",
        "Consultant.py",
        "CosmeticDermCosmeticSurgeon.py",
        "CosmetologistMD.py",
        "Cytologist.py",
        "DentalAssistant.py",
        "DentalSurgeon.py",
        "Dentist.py",
        "DermatologicSurgeon.py",
        "Dermatologist.py",
        "Distributor.py",
        "Employee.py",
        "Endocrinologist.py",
        "ENTPhysician.py",
        "Esthetician.py",
        "EventManager.py",
        "FacialPlasticSurgeon.py",
        "GeneralPhysician.py",
        "GeneralSurgeon.py",
        "Genetician.py",
        "Geriatrist.py",
        "GynecologistObstetrician.py",
        "HairTransplantSurgeon.py",
        "Headofdepartment.py",
        "Hematologist.py",
        "HospitalManager.py",
        "Immunologist.py",
        "Influencer.py",
        "InternalMedicine.py",
        "LaboratoryMedicine.py",
        "Lawyer.py",
        "LegalCounsel.py",
        "LPN.py",
        "MarketingManager.py",
        "MaxillofacialSurgeon.py",
        "MedicalAdvisor.py",
        "MedicalSpaManager.py",
        "NeonatologistNeurologist.py",
        "Neurophysiologist.py",
        "NonmedicalStaff.py",
        "NursePractitioner.py",
        "Nutritionist.py",
        "OculoplasticSurgeon.py",
        "Oncologist.py",
        "Ophthalmologist.py",
        "OralMaxillofacialSurgeon.py",
        "Orthodontist.py",
        "Orthopedist.py",
        "Owner.py",
        "Pathologist.py",
        "Pediatrician.py",
        "Pharmacist.py",
        "Pharmacologist.py",
        "Photographer.py",
        "PhysicianAssistant.py",
        "Physiotherapist.py",
        "PlasticReconstructiveSurgeon.py",
        "PlasticSurgeon.py",
        "PracticeManager.py",
        "Press.py",
        "ProductProjectManager.py",
        "ProfessorTeacher.py",
        "Psychiatrist.py",
        "Psychologist.py",
        "Psychotherapist.py",
        "Radiologist.py",
        "RN.py",
        "ResearchScientist.py",
        "Rheumatologist.py",
        "Sales.py",
        "SportsMedicinePhysician.py",
        "Stomatologist.py",
        "Student.py",
        "Trichologist.py",
        "Urologist.py",
        "VascularSurgeon.py",
        "TransformationHub.py"
    ]

    # Use a shared globals dict and inject df
    globals_dict = {"df": df}

    # Execute each script
    for script_name in ordered_scripts:
        # Get the path to the script from the installed package
        script_path = pkg_resources.resource_filename('JobTitleTransformer', f'job_scripts/{script_name}')
        print(f"\nExecuting: {script_name}")

        # Open the script and execute it
        with open(script_path, "rb") as f:
            code = compile(f.read(), script_path, 'exec')
            exec(code, globals_dict)

        # Update df after each script (optional but safe)
        df = globals_dict["df"]

    return df