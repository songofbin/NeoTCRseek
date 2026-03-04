############################################################
# NeoTCRseek – Unified Publication Theme
############################################################

suppressMessages({
  library(ggplot2)
  library(ggpubr)
  library(ggbeeswarm)
  library(extrafont)
  loadfonts(device = "postscript")
})

############################################################
############################################################

neotcr_palette <- c(
  "CMV-pp65"    = "#FF0000",  # 红色
  "Neo-74"      = "#FF7F0E",  # 橙色
  "Neo-Mix"     = "#1F77B4",  # 蓝色
  "Ag-specific" = "#74C476",  # 绿色
  "Non-specific"= "#EF3B2C"   # 红色
)

############################################################
############################################################

theme_neotcrseek <- function(base_size = 25) {

  theme_classic(base_size = base_size) +
    theme(
      text = element_text(family = "Arial", face = "bold", color = "black"),

      axis.title.x = element_text(size = base_size + 2, face = "bold"),
      axis.title.y = element_text(size = base_size + 2, face = "bold"),

      axis.text.x = element_text(size = base_size - 2, face = "bold"),
      axis.text.y = element_text(size = base_size - 2, face = "bold"),

      axis.line = element_line(linewidth = 0.8),
      axis.ticks = element_line(linewidth = 0.8),

      legend.title = element_text(size = base_size, face = "bold"),
      legend.text  = element_text(size = base_size - 2, face = "bold"),

      panel.grid = element_blank(),
      strip.text = element_text(size = base_size - 2, face = "bold")
    )
}

############################################################
############################################################

geom_box_with_points <- function(width = 0.5) {

  list(
    geom_boxplot(
      width = width,
      outlier.shape = NA,
      linewidth = 0.7,
      color = "black"
    ),
    geom_quasirandom(
      width = 0.18,
      size = 2.2,
      alpha = 0.6
    )
  )
}

############################################################
############################################################

add_stat_compare <- function(comparisons, alternative = "two.sided") {

  stat_compare_means(
    comparisons = comparisons,
    method = "wilcox.test",
    label = "p.format",
    size = 7,
    tip.length = 0.01,
    family = "Arial",
    method.args = list(alternative = alternative)
  )
}

############################################################
############################################################

scale_log10_frequency <- function() {
  scale_y_continuous(
    trans = "log10",
    expand = expansion(mult = c(0.05, 0.15))
  )
}

scale_log2_fc <- function() {
  scale_y_continuous(
    expand = expansion(mult = c(0.05, 0.20))
  )
}

