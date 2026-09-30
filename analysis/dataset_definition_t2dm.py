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

# Dulaglutide codelist

# Ethnicity codelist
# Grouping_6 holds groups 1 to 5. Group 6 is "Not stated".
# "Not stated" has no SNOMED code. No code means missing ethnicity.

# Patient is registered with a GP practice on the index date

# Patient is alive on the index date

# Patient has a type 2 diabetes record on or before the index date

# Patient sex

# Patient age band on the index date

# Latest primary care ethnicity on or before the index date

# SUS ethnicity, used where primary care ethnicity is missing

# Patient ethnicity

# Patient has a dulaglutide prescription in the year after the index date

# Define population
