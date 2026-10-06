# ehrQL cheatsheet

Reference for the ehrQL features in this workshop.

- [Language reference](https://docs.opensafely.org/ehrql/reference/language/)
- [Language features](https://docs.opensafely.org/ehrql/reference/features/)
- [ehrQL cheatsheet](https://docs.opensafely.org/ehrql/reference/cheatsheet/)
- [Command line interface](https://docs.opensafely.org/ehrql/reference/cli/)

## Frames

A frame is the ehrQL equivalent of a table. You import frames. You do not define them.

A **patient frame** has at most one row per patient. A **event frame** can have many rows per patient.

A column on a frame is a **series**. A dataset column must be a patient series: one value per patient. Reduce an event frame to a patient series before you assign it to the dataset.

### Tables in this workshop

```python
from ehrql.tables.tpp import (
    patients,
    clinical_events,
    medications,
    practice_registrations,
    ethnicity_from_sus,
)
```

| Table | Kind | Columns |
| --- | --- | --- |
| `patients` | Patient | `sex`, `date_of_birth`, `date_of_death` |
| `practice_registrations` | Event | `start_date`, `end_date` |
| `clinical_events` | Event | `snomedct_code`, `date`, `numeric_value` |
| `medications` | Event | `dmd_code`, `date` |
| `ethnicity_from_sus` | Patient | `code` |

`patients` also has `age_on(date)` and `is_alive_on(date)`. `practice_registrations` also has `exists_for_patient_on(date)`.

`ethnicity_from_sus` has one row per patient. `ethnicity_from_sus.code` is a patient series. You can assign it to the dataset with no aggregation. The code is the SUS ethnicity code. Use it when the primary care ethnicity is missing.

## Dataset

A dataset definition file must assign the dataset to the name `dataset`.

```python
from ehrql import create_dataset

dataset = create_dataset()
dataset.sex = patients.sex
dataset.define_population(patients.exists_for_patient())
```

| Operation | What it does |
| --- | --- |
| `create_dataset()` | Start an empty dataset |
| `dataset.column_name = patient_series` | Add one column. `patient_id` is included automatically |
| `dataset.add_column(name, patient_series)` | Same result as `=` for one column |
| `dataset.define_population(condition)` | Keep patients for whom the boolean patient series is true |

Patients outside the population are absent from the output.

## Codelists

```python
from ehrql import codelist_from_csv

codes = codelist_from_csv(
    "codelists/example.csv",
    column="code",
)

codes_with_categories = codelist_from_csv(
    "codelists/example.csv",
    column="code",
    category_column="category",
)
```

| Argument | Meaning |
| --- | --- |
| `filename` | Path from the repository root. Use forward slashes |
| `column` | CSV column that holds the codes |
| `category_column` | Optional CSV column of categories. The codelist then maps each code to a category |

Pass a categorised codelist to `to_category()`.

`codelists/codelists.txt` lists the codelists for this repository. This command writes the CSV files:

```bash
opensafely codelists update
```

## Operators

Use these operators on ehrQL series. The Python words `and`, `or`, and `not` do not apply to series.

| Operator | Meaning |
| --- | --- |
| `==` | Equal |
| `!=` | Not equal |
| `>` `>=` `<` `<=` | Compare numbers or dates |
| `&` | And. True when both sides are true. False when either side is false. Null otherwise |
| `\|` | Or. True when either side is true. False when both sides are false. Null otherwise |
| `~` | Not. Swaps true and false. Null stays null |

A comparison with null is null.

| Method | Meaning |
| --- | --- |
| `.is_null()` | The value is missing |
| `.is_not_null()` | The value is present |
| `.is_in(values)` | The value is in a list or a codelist |

```python
patients.sex == "female"
patients.sex.is_in(["female", "male"])
clinical_events.snomedct_code.is_in(codes)
```

## Event frames

### Filter rows

`where(condition)` returns a new frame. It keeps rows where `condition` is true. It drops rows where `condition` is null.

Chain `where` to apply another filter. Each call keeps the rows that also match the next condition.

```python
clinical_events.where(
    clinical_events.snomedct_code.is_in(codes)
).where(
    clinical_events.date.is_on_or_after("2020-01-01")
)
```

### One value per patient

| Method | Result |
| --- | --- |
| `.exists_for_patient()` | Boolean patient series. True when the patient has at least one row |
| `.count_for_patient()` | Integer patient series. The number of rows. Zero when the patient has no rows |

```python
clinical_events.where(
    clinical_events.snomedct_code.is_in(codes)
).exists_for_patient()
```

On a patient frame, `exists_for_patient()` is true when that patient has a row.

### Sort, then pick one row

`sort_by` sorts each patient's rows. The first column is the main sort. Later columns break ties. Null is smaller than every other value.

| Method | Row kept |
| --- | --- |
| `.first_for_patient()` | First row in the sort order |
| `.last_for_patient()` | Last row in the sort order |

If several rows still tie, ehrQL picks one row. That pick stays the same unless the data change.

```python
clinical_events.sort_by(
    clinical_events.date
).last_for_patient().snomedct_code
```

The result of `first_for_patient()` or `last_for_patient()` is a patient frame. Read a column from it to get a patient series.

### Map a code to a category

`to_category(codelist)` replaces each code with the category from `category_column`. A code with no category becomes null. A patient with no row becomes null.

```python
code.to_category(codes_with_categories)
```

## Dates

Write a date as a string: `"2025-01-01"`.

### Arithmetic

```python
from ehrql import days, weeks, years

index_date + years(1)
index_date - days(90)
```

`days` and `weeks` have a fixed length. `years` and `months` follow the calendar. A result that lands on a date that does not exist, such as 29 February in the next year, moves forward to the next real date.

### Comparisons

These methods are on a date series. A null date makes the result null.

| Method | True when the date is |
| --- | --- |
| `.is_before(other)` | Earlier than `other` |
| `.is_on_or_before(other)` | Earlier than `other`, or the same day |
| `.is_after(other)` | Later than `other` |
| `.is_on_or_after(other)` | Later than `other`, or the same day |
| `.is_on_or_between(start, end)` | Inside the range, including both ends |
| `.is_between_but_not_on(start, end)` | Inside the range, excluding both ends |

### Methods on patient tables

| Method | Result |
| --- | --- |
| `patients.age_on(date)` | Age in whole years on that date |
| `patients.is_alive_on(date)` | Boolean. The recorded death date is null, or strictly after `date` |
| `practice_registrations.exists_for_patient_on(date)` | Boolean. A registration covers that date |

## `case`

`case` reads each `when` in order and returns the value from the first true condition. If no condition is true, it returns `otherwise`. If you omit `otherwise`, the result is null.

```python
from ehrql import case, when

label = case(
    when(value < 10).then("small"),
    when(value < 20).then("medium"),
    otherwise="large",
)
```

A later condition is tested only after the earlier conditions are false. You can combine conditions with `&` and `|` inside `when(...)`.

## `show`

`show` prints a dataset, a frame, or a series from local dummy data. It does not read real patient data.

```python
from ehrql import show

show(patients)
show(dataset)
show(dataset.sex, head=10)
```

| Argument | Effect |
| --- | --- |
| `label` | Text printed above the table |
| `head` | First N lines |
| `tail` | Last N lines |

You can pass `head` and `tail` together. You can pass several patient series, and `show` prints them in one table.

## Commands

`opensafely exec ehrql:v1` runs an ehrQL command.

```bash
opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition_t2dm.py \
  --dummy-tables dummy_tables \
  --output output/dataset_t2dm.csv
```

| Argument | Meaning |
| --- | --- |
| `DEFINITION_FILE` | Path to the Python file that defines `dataset` |
| `--output` | Output path. The extension selects the format: `.arrow`, `.csv`, or `.csv.gz`. With no `--output`, ehrQL prints the dataset |
| `--dummy-tables` | Directory with one dummy file per table |
| `--dummy-data-file` | One prepared dummy dataset file |

`--dummy-tables` and `--dummy-data-file` apply on your computer. The same command ignores them when it runs against real tables.

`project.yaml` runs `generate-dataset` as an action. Point that action at the dataset definition you want to run.
