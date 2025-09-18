library(equateIRT)

# packaged 3PL estimates/covariances for 5 forms
data(est3pl)
forms <- paste0("test", 1:5)

mods <- modIRT(
  coef   = est3pl$coef,
  var    = est3pl$var,
  names  = forms,
  display = FALSE
)

# Stocking–Lord linking: Form 1 → Form 2
l12 <- direc(
  mods       = mods,
  which      = c("test1", "test2"),
  method     = "Stocking-Lord",
  D          = 1,          # match the D used when these params were estimated
  quadrature = TRUE,
  nq         = 41
)

summary(l12)
AB <- eqc(l12); AB

# # Convert item or person parameters explicitly (optional)
# # (difficulty b -> b*A + B; discrimination a -> a/A; c unchanged)
# conv_items <- convert(A = AB$A, B = AB$B, coef = coef(mods$test1))
# conv_theta <- convert(A = AB$A, B = AB$B, person.par = seq(-3, 3, length.out = 7))
# head(conv_items); conv_theta
