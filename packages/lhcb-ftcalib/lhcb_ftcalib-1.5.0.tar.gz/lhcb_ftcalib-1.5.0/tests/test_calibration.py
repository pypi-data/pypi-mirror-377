import os
import pytest
import numpy as np
import uproot
import lhcb_ftcalib as ft
from utils import DataIntegrity, delete_file, allclose


def test_prepare_tests():
    if not os.path.exists("tests/calib"):
        os.mkdir("tests/calib")

    # Generate toy data for calibration testing
    if not os.path.exists("tests/calib/toy_data.root"):
        poly1 = ft.PolynomialCalibration(2, ft.link.mistag)
        generator = ft.toy_tagger.ToyDataGenerator(0, 20)

        with uproot.recreate("tests/calib/toy_data.root") as File:
            File["BU_TOY"] = generator(
                N    = 30000,
                func = poly1,
                params = [[0, 0, 0, 0],
                          [0.01, 0.3, 0.01, 0],
                          [0.01, 0, 0.01, 0.3]],
                tagger_types = ["OSKaon", "SSPion", "OSMuon"],
                osc = False, lifetime = 0, DM = 0, DG = 0, Aprod = 0)

            File["BD_TOY"] = generator(
                N = 30000,
                func = poly1,
                params = [[0, 0, 0, 0],
                          [0.01, 0.3, 0.01, 0],
                          [0.01, 0, 0.01, 0.3]],
                tagger_types = ["OSKaon", "SSPion", "OSMuon"],
                osc = True, lifetime = 1.52, DM = 0.5065, DG = 0, Aprod = 0)


def TagDataEquals(d1, d2):
    if d1 is None and d2 is None:
        return True
    equal = True
    equal &= d1._full_data.equals(d2._full_data)
    equal &= d1._tagdata.equals(d2._tagdata)

    equal &= d1.N     == d2.N
    equal &= d1.Nt    == d2.Nt
    equal &= d1.Nw    == d2.Nw
    equal &= d1.Neff  == d2.Neff
    equal &= d1.Nwt   == d2.Nwt
    equal &= d1.Ns    == d2.Ns
    equal &= d1.Nts   == d2.Nts
    equal &= d1.Nws   == d2.Nws
    equal &= d1.Neffs == d2.Neffs
    equal &= d1.Nwts  == d2.Nwts
    return equal


def compare_dataframe_to_file(filename, key, df):
    # Tests the content of a root file to a dataframe for equality within
    # rounding errors to make sure API and CLI give same results
    assert os.path.exists(filename)
    fdata = uproot.open(filename)[key].arrays(library="pd")
    for branch in fdata.columns.values:
        if branch in df:
            print(f"Comparing branch {branch} ...")
            b1 = np.array(fdata[branch])
            b2 = np.array(df[branch])
            if not all(np.isclose(b1, b2)):
                print("FAIL")
                print("CLI ", b1[b1 != b2])
                print("API ", b2[b1 != b2])
                raise AssertionError
            print("PASSED")


def test_calibrate_Bu():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/calib/test_calibrate_Bu"
    delete_file(testfile + ".json")
    F = "tests/calib/toy_data.root"

    df = uproot.open(F)["BU_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY"], library="pd")
    tc = ft.TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    with DataIntegrity(tc):
        tc.calibrate()
        tc.get_dataframe(calibrated=True)

    # Test plotting while we are here
    os.makedirs("tests/testplots", exist_ok=True)
    tc.plot_calibration_curves(savepath="tests/testplots", format="pdf")
    tc.plot_calibration_curves(savepath="tests/testplots", format="png")
    tc.plot_calibration_curves(savepath="tests/testplots", format="json")

    delete_file(testfile + ".json")


def test_calibrate_combine_Bu():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/calib/test_calibrate_combine_Bu"
    delete_file(testfile + ".json")
    F = "tests/calib/toy_data.root"

    df = uproot.open(F)["BU_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY"], library="pd")
    tc = ft.TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    with DataIntegrity(tc):
        tc.calibrate()
        apidata = tc.get_dataframe(calibrated=True)
        combination = tc.combine_taggers("Combination", calibrated=True)
        combdata = combination.get_dataframe(calibrated=False)
    for v in combdata.columns.values:
        apidata[v] = combdata[v]

    delete_file(testfile + ".json")


def test_calibrate_combine_calibrate_Bu():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/calib/test_calibrate_combine_calibrate_Bu"
    delete_file(testfile + ".json")
    F = "tests/calib/toy_data.root"

    df = uproot.open(F)["BU_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY"], library="pd")
    tc = ft.TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    with DataIntegrity(tc):
        tc.calibrate()
        apidata = tc.get_dataframe(calibrated=True)
        combination = tc.combine_taggers("Combination", calibrated=True)
        combination.calibrate()
        combdata = combination.get_dataframe(calibrated=False)
        combdata_calib = combination.get_dataframe(calibrated=True)
    for v in combdata.columns.values:
        apidata[v] = combdata[v]
    for v in combdata_calib.columns.values:
        apidata[v] = combdata_calib[v]

    delete_file(testfile + ".json")


def test_calibrate_Bd():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/calib/test_calibrate_Bd"
    delete_file(testfile + ".json")
    F = "tests/calib/toy_data.root"

    df = uproot.open(F)["BD_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY", "TAU"], library="pd")
    tc = ft.TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    with DataIntegrity(tc):
        tc.calibrate()
        tc.get_dataframe()

    delete_file(testfile + ".json")


def test_calibrate_Bd_selection_vartype1():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/calib/test_calibrate_Bd_sel_v1"
    delete_file(testfile + ".json")
    F = "tests/calib/toy_data.root"

    df = uproot.open(F)["BD_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY", "TAU"], library="pd")
    selection = df.TAU > 0.5
    tc = ft.TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    with DataIntegrity(tc):
        tc.calibrate()
        tc.get_dataframe()

    delete_file(testfile + ".json")


def test_calibrate_Bd_selection_vartype2():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/calib/test_calibrate_Bd_sel_v2"
    delete_file(testfile + ".json")
    F = "tests/calib/toy_data.root"

    df = uproot.open(F)["BD_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY", "TAU", "eventNumber"], library="pd")
    selection = df.eventNumber % 2 == 0
    tc = ft.TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    with DataIntegrity(tc):
        tc.calibrate()
        tc.get_dataframe()

    delete_file(testfile + ".json")


def test_calibrate_combine_Bd():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/calib/test_calibrate_combine_Bd"
    delete_file(testfile + ".json")
    F = "tests/calib/toy_data.root"

    df = uproot.open(F)["BD_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY", "TAU"], library="pd")
    tc = ft.TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    with DataIntegrity(tc):
        tc.calibrate()
        combination = tc.combine_taggers("Combination", calibrated=True)
        apidata = tc.get_dataframe(calibrated=True)
        combdata = combination.get_dataframe(calibrated=False)
    for v in combdata.columns.values:
        apidata[v] = combdata[v]

    delete_file(testfile + ".json")


def test_calibrate_combine_calibrate_Bd():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/calib/test_calibrate_combine_calibrate_Bd"
    delete_file(testfile + ".json")
    F = "tests/calib/toy_data.root"

    df = uproot.open(F)["BD_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY", "TAU"], library="pd")
    tc = ft.TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    with DataIntegrity(tc):
        tc.calibrate()
        combination = tc.combine_taggers("Combination", calibrated=True)
        combination.calibrate()
        apidata = tc.get_dataframe(calibrated=True)
        combdata = combination.get_dataframe(calibrated=False)
        combdata_calib = combination.get_dataframe(calibrated=True)
    for v in combdata.columns.values:
        apidata[v] = combdata[v]
    for v in combdata_calib.columns.values:
        apidata[v] = combdata_calib[v]

    delete_file(testfile + ".json")


def test_calibrate_combine_calibrate_Bd_selection():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/calib/test_calibrate_combine_calibrate_Bd_sel"
    delete_file(testfile + ".json")
    F = "tests/calib/toy_data.root"

    df = uproot.open(F)["BD_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY", "TAU", "eventNumber"], library="pd")

    selection = df.eventNumber % 2 == 0
    tc = ft.TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    with DataIntegrity(tc):
        tc.calibrate()
        combination = tc.combine_taggers("Combination", calibrated=True)
        combination.calibrate()
        apidata = tc.get_dataframe(calibrated=True)
        combdata = combination.get_dataframe(calibrated=False)
        combdata_calib = combination.get_dataframe(calibrated=True)
    for v in combdata.columns.values:
        apidata[v] = combdata[v]
    for v in combdata_calib.columns.values:
        apidata[v] = combdata_calib[v]

    delete_file(testfile + ".json")


def test_parallel_calibration_consistency():
    testfile = "tests/calib/test_parallel_calibration_consistency"
    delete_file(testfile + ".json")
    F = "tests/calib/toy_data.root"

    df = uproot.open(F)["BD_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY", "TAU", "eventNumber"], library="pd")

    selection = df.eventNumber % 2 == 0
    tc = ft.TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)

    tc2 = ft.TaggerCollection()
    tc2.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc2.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)

    tc.calibrate()
    tc2.calibrate(parallel=True)

    res1 = tc.get_dataframe(calibrated=True)
    res2 = tc2.get_dataframe(calibrated=True)

    for col in res1.columns.values:
        assert allclose(res1[col], res2[col]), "Mismatch for " + col

    delete_file(testfile + ".json")


@pytest.mark.parametrize(
    ("func", "expected"),
    [
        (ft.PolynomialCalibration(2, ft.link.mistag), True),
        (ft.PolynomialCalibration(3, ft.link.logit), True),
        (ft.NSplineCalibration(3, ft.link.mistag), True),
        (ft.NSplineCalibration(4, ft.link.logit), True),
        (ft.BSplineCalibration(4, ft.link.mistag), True),
        (ft.BSplineCalibration(5, ft.link.logit), True),
    ]
)
def test_calibrate_save_load(func, expected):
    # Write calibrations to file and load them. Compare whether calibration
    # functions and the ones loaded from file generate the same omega value
    testfile = "tests/calib/test_calibrate_save_load"
    delete_file(testfile + ".json")
    calibfile = "tests/calib/test_calibration"
    delete_file(calibfile + ".json")
    F = "tests/calib/toy_data.root"

    df = uproot.open(F)["BD_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY", "TAU"], library="pd", entry_stop=10000)
    tc = ft.TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.set_calibration(func)
    with DataIntegrity(tc):
        tc.calibrate()
    origdata = tc.get_dataframe(calibrated=True)

    ft.save_calibration(tc, title=calibfile + ".json")

    tc_flavour = ft.TargetTaggerCollection()
    tc_flavour.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc_flavour.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc_flavour.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc_flavour.load_calibrations(calibfile + ".json", style="flavour")
    tc_flavour.apply(ignore_delta=True)
    flavourdata = tc_flavour.get_dataframe(calibrated=True)

    tc_delta = ft.TargetTaggerCollection()
    tc_delta.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc_delta.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc_delta.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc_delta.load_calibrations(calibfile + ".json", style="delta")
    tc_delta.apply(ignore_delta=True)
    deltadata = tc_delta.get_dataframe(calibrated=True)

    for t in range(3):
        assert tc[t].func.npar == tc_delta[t].func.npar
        assert tc[t].func.npar == tc_flavour[t].func.npar
        assert tc[t].func.link == tc_delta[t].func.link
        assert tc[t].func.link == tc_flavour[t].func.link

        TagDataEquals(tc[t].stats, tc_flavour[t].stats)
        TagDataEquals(tc[t].stats, tc_delta[t].stats)

    print("Difference between delta and flavour:")
    print((deltadata - flavourdata).describe())
    print("Difference between orig and flavour:")
    print((origdata - flavourdata).describe())
    print("Difference between delta and orig:")
    print((deltadata - origdata).describe())

    assert all([allclose(deltadata[c], flavourdata[c]) for c in origdata.columns])
    assert all([allclose(origdata[c], flavourdata[c]) for c in origdata.columns])
    assert all([allclose(origdata[c], deltadata[c]) for c in origdata.columns])

    delete_file(calibfile + ".json")
    delete_file(testfile + ".json")


def test_error_propagation_combination():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/calib/test_error_propagation_combination"
    delete_file(testfile + ".json")
    F = "tests/calib/toy_data.root"

    df = uproot.open(F)["BD_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY", "TAU"], library="pd")
    tc = ft.TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc[0].set_calibration(ft.PolynomialCalibration(npar=2, link=ft.link.mistag))
    tc[1].set_calibration(ft.PolynomialCalibration(npar=3, link=ft.link.mistag))
    tc[2].set_calibration(ft.PolynomialCalibration(npar=2, link=ft.link.logit))
    tc.calibrate()

    combination = tc.combine_taggers("Combination", calibrated=True)
    tagpower0 = tc[0].stats.tagging_power(calibrated=True, inselection=False)
    tagpower1 = tc[1].stats.tagging_power(calibrated=True, inselection=False)
    tagpower2 = tc[2].stats.tagging_power(calibrated=True, inselection=False)
    tagpower_combined = combination.stats.tagging_power(calibrated=False, inselection=False)
    tagpower_combined_selected = combination.stats.tagging_power(calibrated=False, inselection=True)

    ft.constants.propagate_errors = True
    combination_propagated = tc.combine_taggers("Combination new", calibrated=True)
    tagpower_combined_propagated = combination_propagated.stats.tagging_power(calibrated=False, inselection=False)
    tagpower_combined_selected_propagated = combination_propagated.stats.tagging_power(calibrated=False, inselection=True)
    ft.constants.propagate_errors = False

    assert tagpower0[0] + tagpower1[0] + tagpower2[0] >= tagpower_combined[0]
    assert tagpower0[0] + tagpower1[0] + tagpower2[0] >= tagpower_combined_propagated[0]
    assert tagpower_combined[0] == tagpower_combined_propagated[0]
    assert tagpower_combined_selected[0] == tagpower_combined_selected_propagated[0]
    assert np.array_equal(tagpower_combined_propagated, tagpower_combined_selected_propagated)

    delete_file(testfile + ".json")


def test_error_propagation_combination_consistency():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/calib/test_error_propagation_combination_consistency"
    delete_file(testfile + ".json")
    F = "tests/calib/toy_data.root"

    df = uproot.open(F)["BD_TOY"].arrays(["TOY0_ETA", "TOY0_DEC", "FLAV_DECAY", "TAU"], library="pd")
    tc = ft.TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.calibrate()

    combination = tc.combine_taggers("Combination", calibrated=True)
    tagpower = tc[0].stats.tagging_power(calibrated=True, inselection=False)
    tagpower_combined = combination.stats.tagging_power(calibrated=False, inselection=False)

    ft.constants.propagate_errors = True
    combination_propagated = tc.combine_taggers("Combination new", calibrated=True)
    tagpower_combined_propagated = combination_propagated.stats.tagging_power(calibrated=False, inselection=False)

    # Truncate omega just in case omega>0.5. Thise values cannot be compared since the epm ignores them explicitly in combinations
    dataref = tc[0].stats._full_data
    overflow = dataref.omega > 0.5
    underflow = dataref.omega < 0
    dataref.loc[overflow, "omega_err"] = 0
    dataref.loc[underflow, "omega_err"] = 0
    dataref.loc[overflow, "omega"] = 0.5
    dataref.loc[underflow, "omega"] = 0

    assert allclose(tc[0].stats._full_data.omega, combination.stats._full_data.eta)
    assert allclose(tc[0].stats._full_data.omega, combination_propagated.stats._full_data.eta)
    assert allclose(tc[0].stats._full_data.omega_err, combination_propagated.stats._full_data.eta_err)
    ft.constants.propagate_errors = False

    assert np.isclose(tagpower_combined[0], tagpower[0])
    assert np.isclose(tagpower_combined[0], tagpower_combined_propagated[0])
    assert allclose(tagpower_combined_propagated, tagpower, atol=1e-4)

    delete_file(testfile + ".json")
