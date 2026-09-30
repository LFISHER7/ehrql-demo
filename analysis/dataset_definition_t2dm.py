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
dataset.configure_dummy_data(population_size=1000)

# Type 2 diabetes codelist
type_2_diabetes_codes = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dmtype2_cod.csv",
    column="code",
)

##################
# Codelists
# ################


# Dulaglutide codelist
# Demo Step 3: Add whether patient has a dulaglutide prescription in the last year
# dulaglutide_codes = codelist_from_csv(
#     "codelists/opensafely-dulaglutide.csv",
#     column="code",
# )

# Ethnicity codelist
# Grouping_6 holds groups 1 to 5. Group 6 is "Not stated".
# "Not stated" has no SNOMED code. No code means missing ethnicity.
# Demo Step 4: Add ethnicity to the dataset, using primary care ethnicity where available, and SUS ethnicity where not
# ethnicity5 = codelist_from_csv(
#     "codelists/opensafely-ethnicity-snomed-0removed.csv",
#     column="code",
#     category_column="Grouping_6",
# )

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

# Latest primary care ethnicity on or before the index date
# Demo Step 4: Add ethnicity to the dataset, using primary care ethnicity where available, and SUS ethnicity where not
# ethnicity_snomed = (
#     clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity5))
#     .where(clinical_events.date.is_on_or_before(index_date))
#     .sort_by(clinical_events.date)
#     .last_for_patient()
#     .snomedct_code.to_category(ethnicity5)
# )

# SUS ethnicity, used where primary care ethnicity is missing
# Demo Step 4: Add ethnicity to the dataset, using primary care ethnicity where available, and SUS ethnicity where not
# ethnicity_sus = ethnicity_from_sus.code

# Demo Step 4: Add ethnicity to the dataset, using primary care ethnicity where available, and SUS ethnicity where not
# dataset.ethnicity = case(
#     when(
#         (ethnicity_snomed == "1")
#         | (ethnicity_snomed.is_null() & ethnicity_sus.is_in(["A", "B", "C"]))
#     ).then("White"),
#     when(
#         (ethnicity_snomed == "2")
#         | (ethnicity_snomed.is_null() & ethnicity_sus.is_in(["D", "E", "F", "G"]))
#     ).then("Mixed"),
#     when(
#         (ethnicity_snomed == "3")
#         | (ethnicity_snomed.is_null() & ethnicity_sus.is_in(["H", "J", "K", "L"]))
#     ).then("South Asian"),
#     when(
#         (ethnicity_snomed == "4")
#         | (ethnicity_snomed.is_null() & ethnicity_sus.is_in(["M", "N", "P"]))
#     ).then("Black"),
#     when(
#         (ethnicity_snomed == "5")
#         | (ethnicity_snomed.is_null() & ethnicity_sus.is_in(["R", "S"]))
#     ).then("Other"),
#     otherwise="Missing",
# )

# Patient has a dulaglutide prescription in the year after the index date
# Demo Step 3: Add whether patient has a dulaglutide prescription in the last year
# one_year_after = index_date + years(1)
# dataset.has_dulaglutide = (
#     medications.where(medications.dmd_code.is_in(dulaglutide_codes))
#     .where(medications.date.is_on_or_between(index_date, one_year_after))
#     .exists_for_patient()
# )

# Define population
dataset.define_population(has_registration & is_alive & has_type_2_diabetes)

show(dataset)