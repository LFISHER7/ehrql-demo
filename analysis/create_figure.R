# Figure of dulaglutide prescribing in the year after the index date

library(readr)
library(dplyr)
library(ggplot2)
library(patchwork)
library(here)

data_path <- here("output", "dataset_t2dm.csv")
figure_path <- here("output", "dulaglutide_figure_r.png")

group_order <- list(
  Sex = c("female", "male"),
  "Age band" = c("0-19", "20-39", "40-59", "60-79", "80+", "missing"),
  Ethnicity = c("White", "Mixed", "South Asian", "Black", "Other", "Missing")
)

data <- read_csv(data_path, show_col_types = FALSE)
data$dulaglutide <- tolower(as.character(data$has_dulaglutide)) %in% c("true", "t", "1")

summarise_groups <- function(data, characteristic, column) {
  group_levels <- group_order[[characteristic]]
  summary <- data |>
    group_by(.data[[column]]) |>
    summarise(
      n_patients = n(),
      n_dulaglutide = sum(dulaglutide),
      .groups = "drop"
    ) |>
    rename(group = all_of(column)) |>
    mutate(
      group = as.character(group),
      percent_dulaglutide = round(100 * n_dulaglutide / n_patients, 1),
      sort_group = match(group, group_levels)
    )
  summary$sort_group[is.na(summary$sort_group)] <- 99L
  summary
}

sex <- summarise_groups(data, "Sex", "sex")
age_band <- summarise_groups(data, "Age band", "age_band")
ethnicity <- summarise_groups(data, "Ethnicity", "ethnicity")

draw_panel <- function(panel_data, characteristic) {
  ordered <- panel_data |>
    arrange(sort_group) |>
    mutate(group = factor(group, levels = rev(unique(group))))
  ggplot(ordered, aes(x = percent_dulaglutide, y = group)) +
    geom_col(fill = "#2c7fb8", width = 0.7) +
    scale_x_continuous(limits = c(0, 100), breaks = seq(0, 100, 20)) +
    labs(x = "Percent of patients", y = NULL, title = characteristic) +
    theme_bw() +
    theme(panel.grid.major.y = element_blank())
}

figure <- wrap_plots(
  draw_panel(sex, "Sex"),
  draw_panel(age_band, "Age band"),
  draw_panel(ethnicity, "Ethnicity"),
  nrow = 1
) +
  plot_annotation(
    title = "Dulaglutide prescription in the year after the index date",
    caption = "Patients with type 2 diabetes who are registered and alive on 1 January 2025."
  )

dir.create(here("output"), showWarnings = FALSE)
ggsave(figure_path, figure, width = 12, height = 4.5)
