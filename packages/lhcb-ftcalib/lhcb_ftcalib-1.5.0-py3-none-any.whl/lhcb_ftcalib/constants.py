# Oscillation parameters
DeltaM_d     = 0.5069
DeltaGamma_d = 0
DeltaM_s     = 17.765
DeltaGamma_s = 0.083

# Covariance scaling for weighted fits
CovarianceCorrectionMethod = "SquaredHesse"  # "SumW2", "None"

# Propgate uncertainties of the calibrated mistags through tagger combination
propagate_errors = False

# Calculate uncertainties of the calibrated mistags. May cost some time, so this is optional
calculate_omegaerr = True

# Use averaged representation of the calibration to write calibrated mistag to
# tuples. It is probably not optimal to never account for mistag asymmetries on
# calibration datasets, but this default mimics the EPM behaviour
ignore_mistag_asymmetry_for_apply = True

# Assign the p+ / p- calibrations to the subsamples of tagging decisions instead of the predicted production flavour
decision_based_likelihood = False
