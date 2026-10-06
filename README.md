# OpenSAFELY ehrQL walkthrough

This repository is a walkthrough for an ehrQL workshop, where you will build a dataset of patients with type 2 diabetes, then summarise dulaglutide prescribing in this population.

## Repository structure

```
.
├── CHEATSHEET.md                     # ehrQL reference for this workshop
├── analysis/                         # Walkthrough scripts
│   ├── dataset_definition_t2dm.py    # Dataset definition. Complete each step in this file.
│   ├── create_table.py               # Summary table in Python
│   ├── create_table.R                # Summary table in R
│   ├── create_table.do               # Summary table in Stata
│   ├── create_figure.py              # Figure in Python
│   ├── create_figure.R               # Figure in R
│   └── create_figure.do              # Figure in Stata
├── solutions/
│   └── dataset_definition_t2dm.py    # Finished dataset definition
├── codelists/
│   └── codelists.txt                 # Codelist references used by the dataset definition
├── dummy_tables/                     # Dummy patient data for a local run
├── project.yaml                      # Pipeline that generates the dataset, tables, and figures
├── output/                           # Dataset, tables, and figures are written here
├── metadata/                         # Logs from each pipeline run.
│   └── <action>.log                  # Messages and errors from one action
```


## Set up a codespace

Clone this repository and create a [GitHub codespace](https://docs.opensafely.org/getting-started/tutorial/create-a-github-codespace/). See also [How to use GitHub Codespaces in your project](https://docs.opensafely.org/getting-started/how-to/use-github-codespaces-in-your-project/).

## Walkthrough

The dataset definition is in [`analysis/dataset_definition_t2dm.py`](analysis/dataset_definition_t2dm.py). There are comments in that file marking each step. A finished copy is in [`solutions/dataset_definition_t2dm.py`](solutions/dataset_definition_t2dm.py). The ehrQL features for these steps are in [`CHEATSHEET.md`](CHEATSHEET.md).

Step 1 is to write the dataset definition. 
Step 2 is to run the dataset definition to create the dataset. 
Step 3 is to create the tables and figures.

## Outputs

| Language | Table | Figure |
| --- | --- | --- |
| Python | `output/dulaglutide_table_python.csv` | `output/dulaglutide_figure_python.png` |
| R | `output/dulaglutide_table_r.csv` | `output/dulaglutide_figure_r.png` |
| Stata | `output/dulaglutide_table_stata.csv` | `output/dulaglutide_figure_stata.png` |

## Useful links

- [OpenSAFELY getting started guide](https://docs.opensafely.org/getting-started/)
- [ehrQL tutorial](https://docs.opensafely.org/ehrql/tutorials/introduction-to-ehrql/)
- [OpenSAFELY documentation](https://docs.opensafely.org/)
- [ehrQL documentation](https://docs.opensafely.org/ehrql/)
- [OpenCodelists](https://www.opencodelists.org/)
- [OpenSAFELY platform](https://www.opensafely.org/)

## Licence

This repository is licensed under the MIT licence. See [`LICENSE`](LICENSE).
