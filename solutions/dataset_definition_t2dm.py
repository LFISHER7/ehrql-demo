# Solution for the type 2 diabetes and dulaglutide example
# The codelists are already in the codelists/ folder

from ehrql import case, codelist_from_csv, create_dataset, when, years
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

# Dulaglutide codelist
dulaglutide_codes = codelist_from_csv(
    "codelists/opensafely-dulaglutide.csv",
    column="code",
)

# Ethnicity codelist
# Grouping_6 holds groups 1 to 5. Group 6 is "Not stated".
# "Not stated" has no SNOMED code. No code means missing ethnicity.
ethnicity5 = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="code",
    category_column="Grouping_6",
)

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

# Patient sex
dataset.sex = patients.sex

# Patient age band on the index date
age = patients.age_on(index_date)
dataset.age_band = case(
    when(age < 20).then("0-19"),
    when(age < 40).then("20-39"),
    when(age < 60).then("40-59"),
    when(age < 80).then("60-79"),
    when(age >= 80).then("80+"),
    otherwise="missing",
)

# Latest primary care ethnicity on or before the index date
ethnicity_snomed = (
    clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity5))
    .where(clinical_events.date.is_on_or_before(index_date))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .snomedct_code.to_category(ethnicity5)
)

# SUS ethnicity, used where primary care ethnicity is missing
ethnicity_sus = ethnicity_from_sus.code

dataset.ethnicity = case(
    when(
        (ethnicity_snomed == "1")
        | (ethnicity_snomed.is_null() & ethnicity_sus.is_in(["A", "B", "C"]))
    ).then("White"),
    when(
        (ethnicity_snomed == "2")
        | (ethnicity_snomed.is_null() & ethnicity_sus.is_in(["D", "E", "F", "G"]))
    ).then("Mixed"),
    when(
        (ethnicity_snomed == "3")
        | (ethnicity_snomed.is_null() & ethnicity_sus.is_in(["H", "J", "K", "L"]))
    ).then("South Asian"),
    when(
        (ethnicity_snomed == "4")
        | (ethnicity_snomed.is_null() & ethnicity_sus.is_in(["M", "N", "P"]))
    ).then("Black"),
    when(
        (ethnicity_snomed == "5")
        | (ethnicity_snomed.is_null() & ethnicity_sus.is_in(["R", "S"]))
    ).then("Other"),
    otherwise="Missing",
)

# Patient has a dulaglutide prescription in the year after the index date
one_year_after = index_date + years(1)
dataset.has_dulaglutide = (
    medications.where(medications.dmd_code.is_in(dulaglutide_codes))
    .where(medications.date.is_on_or_between(index_date, one_year_after))
    .exists_for_patient()
)

# Define population
dataset.define_population(has_registration & is_alive & has_type_2_diabetes)
