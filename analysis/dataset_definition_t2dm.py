# Demo code to create a dataset of patients with type 2 diabetes, including 
#   demographic variables, dulaglutide prescription status, and ethnicity.

# Demo steps:
# Step 1: Import codelists for type 2 diabetes, dulaglutide, and ethnicity from the `codelists.txt'
#         file by running `opensafely codelists update` in the terminal.
# Step 2: Run the code below as-is to create a basic dataset with demographic variables
#         with `opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition_t2dm.py` 
#         and view the dataset in the `output` folder and terminal
# Step 3. Add a dulaglutide prescription variable to the dataset
# Step 4. Add an ethnicity variable to the dataset, using primary care ethnicity  
#         where available, and SUS ethnicity where not

from ehrql import case, codelist_from_csv, create_dataset, when, years, show
from ehrql.tables.tpp import (
    patients,
    clinical_events,
    ethnicity_from_sus,
    medications,
    practice_registrations,
)

index_date = "2025-01-01"

dataset = create_dataset()
dataset.configure_dummy_data(population_size=100)


##################
# Codelists
# ################

# Type 2 diabetes codelist
type_2_diabetes_codes = list_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dmtype2_cod.csv",
    column="code",
)

#####################
# Resuable variables
# ###################

# Patient is registered with a GP practice on the index date
has_registration = practice_registrations.exists_for_patient_on(index_date)

# Patient is alive on the index date
is_alive = patients.is_alive_on(index_date)

# Patient has a type 2 diabetes record on or before the index date
has_type_2_diabetes = (
    clinical_events.where(clinical_events.snomedct_code.is_in(type_2_diabetes_codes))
    .where(clinical_events.date.is_on_or_before(index_date))
    .exists_for_patient()
)


#####################
# Dataset variables
# ###################

# Patient sex
dataset.sex = patients.sex

# Patient age band on the index date
dataset.age = patients.age_on(index_date)

dataset.age_band = case(
    when(dataset.age < 20).then("0-19"),
    when(dataset.age < 40).then("20-39"),
    when(dataset.age < 60).then("40-59"),
    when(dataset.age < 80).then("60-79"),
    when(dataset.age >= 80).then("80+"),
    otherwise="missing",
)


# Define population
dataset.define_population(has_registration & is_alive & has_type_2_diabetes)

show(dataset)