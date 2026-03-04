#!/usr/bin/env Rscript

suppressMessages({
  library(tidyverse)
  library(extrafont)
  loadfonts(device = "postscript")
})

# =========================
# 参数读取
# =========================
args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 3) {
  stop("Usage: Rscript plot_freq_dotplot_ExpandedTCR.R <input.txt> <output.png> <Y_axis_label>")
}

input_file <- args[1]
output_file <- args[2]
y_label_name <- args[3]

# =========================
# 绘图主题
# =========================
mytheme <- theme_bw(base_size = 20) +
  theme(
    text = element_text(family = "Arial", face = "bold", color = "black"),
    legend.title = element_text(hjust = 0.5, size = 25),
    legend.text = element_text(size = 20),
    legend.background = element_rect(colour = "black"),
    axis.title.x = element_text(vjust = 1, size = 30),
    axis.title.y = element_text(size = 30),
    axis.text.x = element_text(size = 25),
    axis.text.y = element_text(size = 25),
    strip.background = element_rect(fill = NA, color = NA),
    panel.grid.minor = element_blank()
  )

# =========================
# Fold 分类函数
# =========================
Fold_type <- function(Fold) {
  ifelse(
    Fold >= 100, "≥100",
    ifelse(Fold >= 20, "20–100", "<20")
  )
}

sizes <- c("<20" = 1, "20–100" = 3, "≥100" = 6)

# =========================
# 数据读取
# =========================
data <- read.csv(input_file, sep = "\t")

# =========================
# 数据整理
# =========================
data_plot <- data %>%
  mutate(freq_c_log = log10(freq_c),
         freq_b_log = log10(freq_b)) %>%
  filter(freq_c >= 0.0001) %>%
  select(cdr3aa, freq_c_log, freq_b_log,
         FC, Expanded, TrueTCR) %>%
  mutate(
    Expansion = ifelse(
      Expanded == "True",
      "Expanded",
      "Not expanded"
    ),
    Expansion = factor(
      Expansion,
      levels = c("Expanded", "Not expanded")
    ),
    Specificity = ifelse(
      TrueTCR == "True",
      "Ag-specific",
      "Non-specific"
    ),
    Specificity = factor(
      Specificity,
      levels = c("Ag-specific","Non-specific")
    )
  )

data_plot <- mutate(data_plot, Fold = Fold_type(FC))
data_plot$Fold <- factor(
  data_plot$Fold,
  levels = c("≥100", "20–100", "<20")
)

# =========================
# 绘图
# =========================
fig1 <- ggplot() +
  geom_point(
    data = data_plot,
    aes(freq_b_log, freq_c_log,
        color = Specificity,
        fill = Expansion,
        size = Fold),
    shape = 21,
    stroke = 1.5,
    alpha = 0.9
  ) +
  scale_color_manual(
    name = "Specificity",
    values = c(
      "Ag-specific" = "#74C476",
      "Non-specific" = "#EF3B2C"
    )
  ) +
  scale_fill_manual(
    name = "Expansion",
    values = c(
      "Expanded" = "#FEB24C", 
      "Not expanded" = "gray")
  ) +
  scale_size_manual(
    name = "Fold change",
    values = sizes
  ) +
  guides(
    fill = guide_legend(order = 1,
                         override.aes = list(size = 6)),
    color = guide_legend(order = 2,
                          override.aes = list(size = 6)),
    size = "none"
  ) +
  xlab("Clonotype frequency in NC (log₁₀)") +
  ylab(paste0("Frequency in ", y_label_name, " (log₁₀)")) + 
  scale_x_continuous(
    breaks = seq(-6, 0, 1),
    limits = c(-6, 0)
  ) +
  scale_y_continuous(
    breaks = seq(-4, 0, 1),
    limits = c(-4, 0)
  ) +
  mytheme +
  theme(
    legend.position = "inside",
    legend.position.inside = c(.8, .78)
  )

# =========================
# 输出图片
# =========================
ggsave(
  filename = output_file,
  plot = fig1,
  device = "png",
  width = 8,
  height = 8
)

