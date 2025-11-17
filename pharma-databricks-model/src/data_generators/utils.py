"""
Utility Functions for Data Generation
Provides helper functions and constants for realistic pharmaceutical data generation
"""

from faker import Faker
from datetime import datetime, timedelta
import random
from decimal import Decimal


# Initialize Faker with seed for reproducibility
def get_faker_instance(seed=42):
    """Get Faker instance with seed for reproducible data generation"""
    fake = Faker()
    Faker.seed(seed)
    random.seed(seed)
    return fake


# Pharmaceutical-specific constants and reference data
MATERIAL_TYPES = [
    "Expression Vector",
    "Cell Line",
    "Master Cell Bank (MCB)",
    "Working Cell Bank (WCB)",
    "Therapeutic Protein",
    "Monoclonal Antibody",
    "Bispecific Antibody",
    "Raw Material",
    "Buffer",
    "Culture Media",
    "Reagent"
]

PROTEIN_SUBTYPES = ["IgG1", "IgG2", "IgG4", "IgA", "IgM"]

SPECIES_OF_ORIGIN = ["CHO", "HEK293", "E.coli", "Yeast", "Hybridoma"]

BATCH_STATUSES = ["Released", "Quarantine", "Rejected", "In Process", "On Hold"]

GENEALOGY_TYPES = ["Original", "Split", "Merge", "Rework", "Pooled"]

SAMPLE_TYPES = ["In-Process", "Retain", "Stability", "Reference"]

MANUFACTURER_TYPES = ["Internal", "CMO", "Testing Lab", "Supplier"]

SPECIFICATION_TYPES = ["Process", "Analytical", "Release", "Stability"]

NOTIFICATION_TYPES = ["Deviation", "CAPA", "Change Control", "Investigation"]

EVENT_TYPES = ["Process", "Equipment", "Material", "Analytical", "Documentation"]

SEVERITY_LEVELS = ["Critical", "Major", "Minor"]

NOTIFICATION_STATUSES = ["Open", "Investigating", "Pending Approval", "Closed"]

DOCUMENT_TYPES = ["Batch Record", "Protocol", "SOP", "COA", "Report", "Specification"]

SYSTEM_TYPES = ["LIMS", "MES", "ELN", "ERP", "QMS"]

PROCESS_PHASES = [
    "Upstream",
    "Downstream",
    "Fill-Finish",
    "Cell Banking",
    "Quality Control"
]

PROCESS_CATEGORIES = [
    "Cell Culture",
    "Purification",
    "Viral Inactivation",
    "Formulation",
    "Filtration",
    "Chromatography"
]

TEST_CATEGORIES = ["Identity", "Purity", "Potency", "Safety"]

TEST_METHOD_CATEGORIES = [
    "Chromatography",
    "Immunoassay",
    "Molecular Biology",
    "Microscopy",
    "Spectroscopy"
]

ANALYTICAL_TECHNIQUES = [
    "HPLC",
    "SEC-HPLC",
    "CEX-HPLC",
    "ELISA",
    "LAL",
    "Western Blot",
    "qPCR",
    "Flow Cytometry",
    "Mass Spectrometry"
]

STORAGE_CONDITIONS = [
    "Long-term (2-8°C)",
    "Accelerated (25°C/60%RH)",
    "Stressed (40°C/75%RH)",
    "Frozen (-20°C)",
    "Ultra-low (-80°C)"
]

TIMEPOINT_LABELS = ["T0", "1 week", "2 weeks", "1 month", "3 months", "6 months", "9 months", "12 months", "18 months", "24 months", "36 months"]

STUDY_TYPES = ["Stability", "Release", "Characterization", "Comparability"]

STUDY_PHASES = ["Discovery", "Pre-Clinical", "Phase 1", "Phase 2", "Phase 3", "Commercial"]

TRANSFORMATION_TYPES = [
    "Thaw",
    "Culture",
    "Passage",
    "Harvest",
    "Centrifugation",
    "Filtration",
    "Chromatography",
    "Formulation",
    "Fill",
    "Freeze"
]

ORDER_TYPES = ["Production", "Rework", "Validation", "Engineering"]

ORDER_STATUSES = ["Planned", "Released", "In Progress", "Complete", "Cancelled"]

USAGE_TYPES = ["Input", "Output", "Yield_Loss", "Sample"]

RESULT_STATUSES = ["Pass", "Fail", "OOS", "Pending", "Invalid"]

# Helper functions for realistic data generation

def generate_protein_sequence(length=100):
    """Generate random protein sequence"""
    amino_acids = "ACDEFGHIKLMNPQRSTVWY"
    return ''.join(random.choice(amino_acids) for _ in range(length))


def generate_material_id(material_type, counter):
    """Generate material ID based on type"""
    type_prefix = {
        "Expression Vector": "VEC",
        "Cell Line": "CL",
        "Master Cell Bank (MCB)": "MCB",
        "Working Cell Bank (WCB)": "WCB",
        "Therapeutic Protein": "TP",
        "Monoclonal Antibody": "mAb",
        "Bispecific Antibody": "BsAb",
        "Raw Material": "RM",
        "Buffer": "BUF",
        "Culture Media": "MED",
        "Reagent": "REG"
    }
    prefix = type_prefix.get(material_type, "MAT")
    return f"{prefix}-{2024}-{counter:04d}"


def generate_batch_id(year, counter):
    """Generate batch ID"""
    return f"BATCH-{year}-{counter:05d}"


def generate_sample_id(batch_id, counter):
    """Generate sample ID linked to batch"""
    return f"{batch_id}-S{counter:03d}"


def generate_timestamp(start_date, end_date):
    """Generate random timestamp between two dates"""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    time_delta = end_date - start_date
    random_days = random.randint(0, time_delta.days)
    random_seconds = random.randint(0, 86400)

    return start_date + timedelta(days=random_days, seconds=random_seconds)


def generate_date_range(start_date, num_dates, interval_days=30):
    """Generate a list of dates at regular intervals"""
    dates = []
    current_date = start_date
    for i in range(num_dates):
        dates.append(current_date)
        current_date += timedelta(days=interval_days)
    return dates


def add_realistic_variation(base_value, variation_percent=5):
    """Add realistic variation to a base value"""
    variation = base_value * (variation_percent / 100)
    return base_value + random.uniform(-variation, variation)


def generate_oos_result(target, lower, upper, oos_probability=0.05):
    """Generate test result with configurable OOS probability"""
    if random.random() < oos_probability:
        # Generate OOS result
        if random.random() < 0.5:
            # Below lower limit
            return random.uniform(lower * 0.7, lower * 0.99), True, "OOS"
        else:
            # Above upper limit
            return random.uniform(upper * 1.01, upper * 1.3), True, "OOS"
    else:
        # Generate in-spec result
        range_val = upper - lower
        result = random.uniform(lower + range_val * 0.1, upper - range_val * 0.1)
        return result, False, "Pass"


def get_lifecycle_stage_dates(stage):
    """Get realistic date ranges for lifecycle stages"""
    stages = {
        "Discovery": (datetime(2020, 1, 1), datetime(2021, 12, 31)),
        "Pre-Clinical": (datetime(2022, 1, 1), datetime(2022, 12, 31)),
        "Phase 1": (datetime(2023, 1, 1), datetime(2023, 6, 30)),
        "Phase 2": (datetime(2023, 7, 1), datetime(2024, 6, 30)),
        "Phase 3": (datetime(2024, 7, 1), datetime(2025, 12, 31)),
        "Commercial": (datetime(2026, 1, 1), datetime(2027, 12, 31)),
    }
    return stages.get(stage, (datetime(2023, 1, 1), datetime(2024, 12, 31)))
