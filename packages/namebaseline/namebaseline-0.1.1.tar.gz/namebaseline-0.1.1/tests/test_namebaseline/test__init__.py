"""
Tests
"""
import pathlib
import tempfile
import random
import os

import pytest
import pandas as pd

import namebaseline as nb


def test_convert_characters():
    """test convert() with names"""
    sut = nb.StrToFloatConverter()
    sut.charset = list("abcdefghijklmnopqrstuvwxyz")
    assert sut.convert("a") == 0.0  # Calc: 0*26^-1
    assert sut.convert("a") == 0.0  # Calc: 0*26^-1
    assert sut.convert("aa") == 0.0  # Calc: 0*26^-1 + 0*26^-2
    # Calc: 0*26^-1 + 1*26^-2 = 0.001479
    assert sut.convert("ab") == pytest.approx(0.00147928994)

    # Calc: 12*26^-1 = 0.461538461538
    assert sut.convert("m") == pytest.approx(0.461538461538)
    # Calc: 12*26^-1 + 0*26^-2= 0.461538461538
    assert sut.convert("ma") == pytest.approx(0.461538461538)
    # Calc: 12*26^-1 + 12*26^-2 = 0.479289940828
    # Calc: 12*26^-1 + 25*26^-1 = 0.498520710059
    assert sut.convert("mz") == pytest.approx(0.498520710059)
    # Calc: 13*26^-1 = 0.5
    assert sut.convert("n") == pytest.approx(0.5)

    # Calc: 25*26^-1 = 0.961538461538
    assert sut.convert("z") == pytest.approx(0.961538461538)
    # Calc: 25*26^-1 + 0*26^-2 = 0.961538461538
    assert sut.convert("za") == pytest.approx(0.961538461538)
    # Calc: 25*26^-1 + 25*26^-2 = 0.998520710059
    assert sut.convert("zz") == pytest.approx(0.998520710059)
    # Calc: 25*26^-1 + 25*26^-2 + 25*26^3 = 0.999943104233
    assert sut.convert("zzz") == pytest.approx(0.999943104233)
    # Calc: 25*26^-1 + 25*26^-2 + 25*26^3 + 25*26^4 = 0.999997811701
    assert sut.convert("zzzz") == pytest.approx(0.999997811701)

def test_convert_email():
    """Test convert() with email addresses"""
    sut = nb.StrToFloatConverter()
    sut.charset = list("abcdefghijklmnopqrstuvwxyz")
    # Calc: 0*26^-1 + 0 + 19*26^-2 + 4*26^-3 + 18*26^-4 + 19*26^-5
    # + 0 + 2*26^-6 + 14*26^-7 + 12*26^-8 = 0.028375088737
    assert sut.convert("a@test.com") == pytest.approx(0.028375088737)
    # Calc: 19*26^-1 + 4*26^-2 + 18*26^-3 + 19*26^-4 + 0 + 19*26^-5
    # + 4*26^-6 + 18*26^-7 + 19*26^-8 + 0 + 2*26^-9 + 14*26^-10
    # + 12*26^-11 = 0.737753706434
    assert sut.convert("test@test.com") == pytest.approx(0.737753706434)
    # Calc: 25*26^-1 + 0 + 19*26^-2 + 4*26^-3 + 18*26^-4 + 19*26^-5
    # + 0 + 2*26^-6 + 14*26^-7 + 12*26^-8 = 0.989913550275
    assert sut.convert("z@test.com") == pytest.approx(0.989913550275)

def test_convert_nochars_should_raise_valueerror():
    """test convert() values that are considered empty"""
    sut = nb.StrToFloatConverter(ignore_missing=True)
    sut.charset = list("abcdefghijklmnopqrstuvwxyz")
    assert sut.convert("") == -1.0
    assert sut.convert("*()@")  == -1.0

def test_build_charset():
    """test build_charset() with a single string"""
    sut = nb.StrToFloatConverter()
    sut.build_charset((
        "the quick brown fox jumps over the lazy dog"
    ))
    assert sut.charset == list("abcdefghijklmnopqrstuvwxyz")

def test_build_charset_multilines():
    """test build_charset() with an array of strings"""
    sut = nb.StrToFloatConverter()
    sut.build_charset("the quick brown fox jumps over the lazy dog".split(" "))
    assert sut.charset == list("abcdefghijklmnopqrstuvwxyz")

def test_convert_characters_with_char_translator():
    """test convert() using a custom char_translator"""
    sut = nb.StrToFloatConverter(
        char_translator=lambda x: 'a' if x == 'b' else x
    )
    sut.charset = list("abcdefghijklmnopqrstuvwxyz")
    assert sut.convert("a") == 0.0  # Calc: 0*26^-1
    assert sut.convert("A") == 0.0  # Calc: 0*26^-1
    assert sut.convert("aa") == 0.0  # Calc: 0*26^-1 + 0*26^-2
    # Calc: 0*26^-1 + 1*26^-2 = 0.001479

    # ab -> aa -> 0
    assert sut.convert("ab") == pytest.approx(0.0)

    # Calc: 25*26^-1 = 0.961538461538
    assert sut.convert("z") == pytest.approx(0.961538461538)
    # Calc: 25*26^-1 + 0*26^-2 = 0.961538461538
    assert sut.convert("za") == pytest.approx(0.961538461538)
    # zb -> za
    assert sut.convert("zb") == pytest.approx(0.961538461538)

def test_convert_characters_with_str_translator():
    """test convert() with a custom str_translator"""
    translator = str.maketrans("b", "a", "c")
    sut = nb.StrToFloatConverter(
        str_translator=lambda x: x.translate(translator)
    )
    sut.charset = list("abcdefghijklmnopqrstuvwxyz")
    assert sut.convert("a") == 0.0  # Calc: 0*26^-1
    assert sut.convert("A") == 0.0  # Calc: 0*26^-1
    assert sut.convert("aa") == 0.0  # Calc: 0*26^-1 + 0*26^-2
    # Calc: 0*26^-1 + 1*26^-2 = 0.001479

    # ab -> aa -> 0
    assert sut.convert("ab") == pytest.approx(0.0)

    # ac -> a -> 0
    assert sut.convert("a") == pytest.approx(0.0)

    # Calc: 25*26^-1 = 0.961538461538
    assert sut.convert("z") == pytest.approx(0.961538461538)
    # Calc: 25*26^-1 + 0*26^-2 = 0.961538461538
    assert sut.convert("za") == pytest.approx(0.961538461538)
    # zb -> za
    assert sut.convert("zb") == pytest.approx(0.961538461538)

def test_convert_characters_with_str_translator_removespaces():
    """test convert() with a translator that removes spaces"""
    translator = str.maketrans("", "", " ")
    sut = nb.StrToFloatConverter(
        str_translator=lambda x: x.translate(translator)
    )
    sut.charset = list("abcdefghijklmnopqrstuvwxyz")
    assert sut.convert("a b") == 0.0014792899408284023

def test_str_cumdf_null_bins():
    """Test str_cumdf() with no binning"""
    converter = nb.StrToFloatConverter()
    converter.charset = list("abcdefghijklmnopqrstuvwxyz")
    values = pd.Series([
        "a",
        "A",
        "aa",
        "ab",
        "m",
        "ma",
        "mm",
        "mz",
        "n",
        "z",
        "za",
        "zz",
        "zzz",
        "zzzz",
    ])
    cdf = nb.str_cumdf(values, converter, num_bins=None)
    expected_cdf = pd.DataFrame({
        "value": [
            0.0,
            0.0014792899408284023,
            0.46153846153846156,
            0.47928994082840237,
            0.49852071005917165,
            0.5,
            0.9615384615384616,
            0.9985207100591716,
            0.9999431042330451,
            0.999997811701271
        ],
        "count": [
            3.0,
            1.0,
            2.0,
            1.0,
            1.0,
            1.0,
            2.0,
            1.0,
            1.0,
            1.0,
        ],
        "cumsum": [
            0.21428571428571427,
            0.2857142857142857,
            0.42857142857142855,
            0.5,
            0.571429,
            0.642857,
            0.785714,
            0.857143,
            0.928571,
            1.0,
        ],
    })
    assert (cdf.keys() == expected_cdf.keys()).all()
    for k in cdf:
        for j in range(cdf[k].shape[0]):
            assert float(cdf[k].iloc[j]) == pytest.approx(expected_cdf[k].iloc[j]), \
                f"key:{k} iloc:{j}"

def test_str_cumdf_10bins():
    """Test str_cumdf() with 10 bins"""
    converter = nb.StrToFloatConverter()
    converter.charset = list("abcdefghijklmnopqrstuvwxyz")
    values = pd.Series([
        "a",
        "A",
        "aa",
        "ab",
        "m",
        "ma",
        "mm",
        "", # Should be excluded
        "mz",
        "n",
        "z",
        "za",
        "zz",
        "zzz",
        "zzzz",
    ])
    cdf = nb.str_cumdf(values, converter, 10)
    expected_cdf = pd.DataFrame({
        "value": [
            0.0,
            0.1,
            0.2,
            0.3,
            0.4,
            0.5,
            0.6,
            0.7,
            0.8,
            0.9,
            1.0
        ],
        "count": [
            4.0,
            0.0,
            0.0,
            0.0,
            4.0,
            1.0,
            0.0,
            0.0,
            0.0,
            5.0,
            0.0,
        ],
        "cumsum": [
            0.2857142857142857,
            0.2857142857142857,
            0.2857142857142857,
            0.2857142857142857,
            0.571429,
            0.642857,
            0.642857,
            0.642857,
            0.642857,
            1.0,
            1.0
        ],
    })
    assert (cdf.keys() == expected_cdf.keys()).all()
    for k in cdf:
        for j in range(cdf[k].shape[0]):
            assert float(cdf[k].iloc[j]) == pytest.approx(expected_cdf[k].iloc[j]), \
                f"key:{k} iloc:{j}"

def test_read_cdf():
    """test read_cdf()"""
    path = pathlib.Path(__file__).parent / "_data" / "baseline.json"
    baseline = nb.read_cdf(path)
    assert isinstance(baseline, pd.DataFrame)
    assert baseline.iloc[0]["value"] == 0.0

def test_write_cdf():
    """test write_cdf()"""
    num_rows = 1000
    baseline = pd.DataFrame()
    baseline.insert(0, "value", [0.0001 * n for n in range(num_rows)])
    baseline.insert(1, "count", [random.randint(0, 10000) for n in range(num_rows)])
    baseline['cumsum'] = baseline['value'].cumsum()
    baseline['cumsum'] = baseline['cumsum'] / baseline['cumsum'].max()
    path = tempfile.mkstemp()
    os.close(path[0])
    nb.write_cdf(path[1], baseline)
    assert pathlib.Path(path[1]).stat().st_size > 0

def test_chi2_gof_test_followsbaseline():
    """test chi2_gof_test() with a CDF against itself"""
    path = pathlib.Path(__file__).parent / "_data"
    baseline = nb.read_cdf(path / "baseline.json")
    result = nb.chi2_gof_test(baseline, baseline)
    assert result.follows_baseline
    assert result.x2 == pytest.approx(0.0, abs=1e-6)

def test_chi2_gof_test_doesntfollowbaseline():
    """test chi2_gof_test() with a CDF against a known different CDF"""
    path = pathlib.Path(__file__).parent / "_data"
    baseline = nb.read_cdf(path / "baseline.json")
    sus = nb.read_cdf(path / "suspicious.json")
    result = nb.chi2_gof_test(baseline, sus)
    assert result.follows_baseline is False
    assert result.x2 == pytest.approx(211940.9393039284)

def test_chi2_gof_test_mismatch():
    """test chi2_gof_test() with CDF that has different binning than the baseline.
    mismatched.json is missing bin # 1000"""
    path = pathlib.Path(__file__).parent / "_data"
    baseline = nb.read_cdf(path / "baseline.json")
    mismatched = nb.read_cdf(path / "mismatched.json")
    with pytest.raises(ValueError):
        _ = nb.chi2_gof_test(baseline, mismatched)
