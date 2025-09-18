# install.packages(c("mirt", "equateIRT"))  # if needed
library(mirt)
library(equateIRT)

# toy data: 5 forms with common items (package vignette example)
data("data2pl", package = "equateIRT")

# 1) Separate calibrations (2PL here; set itemtype per your test)
mfits <- lapply(data2pl, function(X) mirt(X, 1, itemtype = "2PL", SE = TRUE))

# 2) Wrap fits into modIRT (equateIRT ≥ 2.5.0 can ingest mirt objects directly)
forms <- paste0("test", 1:5)
mods  <- modIRT(est.mods = mfits, names = forms, display = FALSE)

# 3) Direct Stocking–Lord linking: Form 1 → Form 2
#    Use quadrature (GH) for the SL integral; increase nq for stability if needed.
l12 <- direc(
  mods       = mods,
  which      = c("test1", "test2"),
  method     = "Stocking-Lord",
  D          = 1,          # match your calibration (mirt default)
  quadrature = TRUE,
  nq         = 41          # GH points
)

summary(l12)     # shows A, B and SEs
eqc(l12)         # extract A/B neatly
# itm(l12)         # item tables incl. test1 parameters mapped onto test2's scale
# 
# # 4) True‑score / Observed‑score equating (Form1 scores to Form2 scale)
# score(l12, method = "TSE")                 # theta grid + equated true scores
# score(l12, method = "OSE", scores = 10:20) # observed-score equating for raw 10..20
