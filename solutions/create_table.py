# Table of dulaglutide prescribing in the year after the index date

from pathlib import Path

import pandas as pd

DATA_PATH = Path("output/dataset_t2dm.csv")
TABLE_PATH = Path("output/dulaglutide_table_python.csv")

GROUP_ORDER = {
    "Sex": ["female", "male"],
    "Age band": ["0-19", "20-39", "40-59", "60-79", "80+", "missing"],
    "Ethnicity": ["White", "Mixed", "South Asian", "Black", "Other", "Missing"],
}


def dulaglutide_flag(column):
    if column.dtype == bool:
        return column.fillna(False)
    return column.astype(str).str.lower().isin(["true", "1"])


def summarise_groups(data, characteristic, column):
    summary = (
        data.groupby(column, dropna=False)
        .agg(n_patients=("dulaglutide", "size"), n_dulaglutide=("dulaglutide", "sum"))
        .reset_index()
        .rename(columns={column: "group"})
    )
    summary["group"] = summary["group"].astype(str)
    summary["characteristic"] = characteristic
    summary["n_dulaglutide"] = summary["n_dulaglutide"].astype(int)
    summary["percent_dulaglutide"] = (
        100 * summary["n_dulaglutide"] / summary["n_patients"]
    ).round(1)
    group_order = {group: index for index, group in enumerate(GROUP_ORDER[characteristic])}
    summary["sort_group"] = summary["group"].map(group_order).fillna(99)
    return summary


data = pd.read_csv(DATA_PATH)
data["dulaglutide"] = dulaglutide_flag(data["has_dulaglutide"])

overall = pd.DataFrame(
    [
        {
            "characteristic": "Overall",
            "group": "All patients",
            "n_patients": len(data),
            "n_dulaglutide": int(data["dulaglutide"].sum()),
            "percent_dulaglutide": round(100 * data["dulaglutide"].mean(), 1),
            "sort_group": 0,
            "sort_characteristic": 0,
        }
    ]
)

sections = [overall]
for sort_characteristic, (characteristic, column) in enumerate(
    [("Sex", "sex"), ("Age band", "age_band"), ("Ethnicity", "ethnicity")],
    start=1,
):
    section = summarise_groups(data, characteristic, column)
    section["sort_characteristic"] = sort_characteristic
    sections.append(section)

table = (
    pd.concat(sections, ignore_index=True)
    .sort_values(["sort_characteristic", "sort_group"])
    .loc[:, ["characteristic", "group", "n_patients", "n_dulaglutide", "percent_dulaglutide"]]
)

TABLE_PATH.parent.mkdir(parents=True, exist_ok=True)
table.to_csv(TABLE_PATH, index=False)
