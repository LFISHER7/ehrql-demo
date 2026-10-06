# Figure of dulaglutide prescribing in the year after the index date

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_PATH = Path("output/dataset_t2dm.csv")
FIGURE_PATH = Path("output/dulaglutide_figure_python.png")

GROUP_ORDER = {
    "Sex": ["female", "male"],
    "Age band": ["0-19", "20-39", "40-59", "60-79", "80+", "missing"],
    "Ethnicity": ["White", "Mixed", "South Asian", "Black", "Other", "Missing"],
}
CHARACTERISTICS = [
    ("Sex", "sex"),
    ("Age band", "age_band"),
    ("Ethnicity", "ethnicity"),
]


def summarise_groups(data, characteristic, column):
    summary = (
        data.groupby(column, dropna=False)
        .agg(n_patients=("dulaglutide", "size"), n_dulaglutide=("dulaglutide", "sum"))
        .reset_index()
        .rename(columns={column: "group"})
    )
    summary["group"] = summary["group"].astype(str)
    summary["n_dulaglutide"] = summary["n_dulaglutide"].astype(int)
    summary["percent_dulaglutide"] = (
        100 * summary["n_dulaglutide"] / summary["n_patients"]
    ).round(1)
    group_order = {group: index for index, group in enumerate(GROUP_ORDER[characteristic])}
    summary["sort_group"] = summary["group"].map(group_order).fillna(99)
    return summary.sort_values("sort_group")


data = pd.read_csv(DATA_PATH)
data["dulaglutide"] = data["has_dulaglutide"].astype(str).str.lower().isin(["true", "t", "1"])

fig, axes = plt.subplots(1, 3, figsize=(12, 4.5), sharex=True)
for axis, (characteristic, column) in zip(axes, CHARACTERISTICS):
    panel = summarise_groups(data, characteristic, column)
    positions = list(range(len(panel)))
    axis.barh(positions, panel["percent_dulaglutide"], color="#2c7fb8")
    axis.set_yticks(positions, panel["group"])
    axis.invert_yaxis()
    axis.set_xlim(0, 100)
    axis.set_xticks([0, 20, 40, 60, 80, 100])
    axis.set_xlabel("Percent of patients")
    axis.set_title(characteristic)

fig.suptitle("Dulaglutide prescription in the year after the index date")
fig.text(
    0.5,
    0.01,
    "Patients with type 2 diabetes who are registered and alive on 1 January 2025.",
    ha="center",
)
fig.tight_layout(rect=(0, 0.05, 1, 0.95))

FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(FIGURE_PATH, dpi=150)
