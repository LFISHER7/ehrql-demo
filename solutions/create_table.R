# Table of dulaglutide prescribing in the year after the index date

library(readr)
library(dplyr)
library(here)

data_path <- here("output", "dataset_t2dm.csv")
table_path <- here("output", "dulaglutide_table_r.csv")

group_order <- list(
  Sex = c("female", "male"),
  "Age band" = c("0-19", "20-39", "40-59", "60-79", "80+", "missing"),
  Ethnicity = c("White", "Mixed", "South Asian", "Black", "Other", "Missing")
)

data <- read_csv(data_path, show_col_types = FALSE)
if (is.logical(data$has_dulaglutide)) {
  data$dulaglutide <- data$has_dulaglutide
} else {
  data$dulaglutide <- tolower(as.character(data$has_dulaglutide)) %in% c("true", "1")
}
data$dulaglutide[is.na(data$dulaglutide)] <- FALSE

summarise_groups <- function(data, characteristic, column) {
  summary <- data |>
    group_by(.data[[column]]) |>
    summarise(
      n_patients = n(),
      n_dulaglutide = sum(dulaglutide),
      .groups = "drop"
    ) |>
    rename(group = all_of(column)) |>
    mutate(
      characteristic = characteristic,
      group = as.character(group),
      percent_dulaglutide = round(100 * n_dulaglutide / n_patients, 1)
    ) |>
    rowwise() |>
    mutate(sort_group = match(group, group_order[[characteristic]]))

  summary$sort_group[is.na(summary$sort_group)] <- 99L
  summary
}

overall <- data.frame(
  characteristic = "Overall",
  group = "All patients",
  n_patients = nrow(data),
  n_dulaglutide = sum(data$dulaglutide),
  percent_dulaglutide = round(100 * mean(data$dulaglutide), 1),
  sort_group = 0,
  sort_characteristic = 0
)

sex <- summarise_groups(data, "Sex", "sex")
sex$sort_characteristic <- 1
age_band <- summarise_groups(data, "Age band", "age_band")
age_band$sort_characteristic <- 2
ethnicity <- summarise_groups(data, "Ethnicity", "ethnicity")
ethnicity$sort_characteristic <- 3

table <- bind_rows(overall, sex, age_band, ethnicity) |>
  arrange(sort_characteristic, sort_group) |>
  select(characteristic, group, n_patients, n_dulaglutide, percent_dulaglutide)

dir.create(here("output"), showWarnings = FALSE)
write_csv(table, table_path)
