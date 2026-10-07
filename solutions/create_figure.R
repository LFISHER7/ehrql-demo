# Figure of dulaglutide prescribing in the year after the index date

library(readr)
library(dplyr)
library(ggplot2)
library(here)

data_path <- here("output", "dataset_t2dm.csv")
figure_path <- here("output", "dulaglutide_figure_r.png")

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
      percent_dulaglutide = round(100 * n_dulaglutide / n_patients, 1),
      label = paste0(n_dulaglutide, "/", n_patients)
    ) %>%
    rowwise() %>%
    mutate(sort_group = match(group, group_order[[characteristic]]))
  summary$sort_group[is.na(summary$sort_group)] <- 99L
  summary
}

sex <- summarise_groups(data, "Sex", "sex")
age_band <- summarise_groups(data, "Age band", "age_band")
ethnicity <- summarise_groups(data, "Ethnicity", "ethnicity")

plot_data <- bind_rows(sex, age_band, ethnicity) |>
  mutate(
    characteristic = factor(characteristic, levels = c("Sex", "Age band", "Ethnicity"))
  ) |>
  arrange(characteristic, sort_group) |>
  mutate(group = factor(group, levels = unique(group)))

figure <- ggplot(plot_data, aes(x = group, y = percent_dulaglutide)) +
  geom_col(fill = "#2c7fb8", width = 0.7) +
  geom_text(aes(label = label), hjust = -0.1, size = 3) +
  facet_wrap(~characteristic, scales = "free_x") +
  coord_flip() +
  scale_y_continuous(limits = c(0, 145), breaks = seq(0, 100, 20)) +
  labs(
    x = NULL,
    y = "Percent of patients",
    title = "Dulaglutide prescription in the year after the index date",
    caption = "Patients with type 2 diabetes who are registered and alive on 1 January 2025. Bar labels are counts."
  ) +
  theme_bw() +
  theme(panel.grid.major.y = element_blank())

dir.create(here("output"), showWarnings = FALSE)
ggsave(figure_path, figure, width = 12, height = 4.5)
