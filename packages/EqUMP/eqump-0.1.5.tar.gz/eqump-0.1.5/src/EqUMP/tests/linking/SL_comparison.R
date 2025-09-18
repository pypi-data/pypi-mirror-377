#!/usr/bin/env Rscript

# Stocking-Lord comparison script for R-Python validation
# Accepts JSON input with item parameters and returns linking constants

library(equateIRT)
library(jsonlite)

# Read command line arguments
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) {
  stop("Usage: Rscript SL_comparison.R <input_json_file>")
}

input_file <- args[1]

# Read input JSON
input_data <- fromJSON(input_file)

# Extract item parameters
a_base <- as.numeric(input_data$a_base)
b_base <- as.numeric(input_data$b_base)
a_new <- as.numeric(input_data$a_new)
b_new <- as.numeric(input_data$b_new)

# Create coefficient matrices following est3pl format
# Column names must match est3pl: "c.i", "beta.1i", "beta.2i"
# For 2PL model: c.i=0, beta.1i=b (difficulty), beta.2i=a (discrimination)
coef_base <- cbind(c.i = rep(0, length(a_base)), 
                   beta.1i = b_base, 
                   beta.2i = a_base)
coef_new <- cbind(c.i = rep(0, length(a_new)), 
                  beta.1i = b_new, 
                  beta.2i = a_new)

# Set row names for items
rownames(coef_base) <- paste0("I", 1:length(a_base))
rownames(coef_new) <- paste0("I", 1:length(a_new))

# Create the data structure that modIRT expects
coef_list <- list(
  base = coef_base,
  new = coef_new
)

# Create modIRT object without variance matrices (let equateIRT handle defaults)
mods <- modIRT(
  coef = coef_list,
  names = c("base", "new"),
  display = FALSE
)

# Perform Stocking-Lord linking
linking_result <- direc(
  mods = mods,
  which = c("base", "new"),
  method = "Stocking-Lord",
  D = 1,
  quadrature = TRUE,
  nq = 81  # Match Python default theta points
)

# Extract linking constants
AB <- eqc(linking_result)

# Prepare output
output <- list(
  A = AB$A,
  B = AB$B,
  se_A = AB$se.A,
  se_B = AB$se.B
)

# Output as JSON
cat(toJSON(output, auto_unbox = TRUE))
