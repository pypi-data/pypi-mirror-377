"""
namebaseline - Determines if a list of names follows a baseline
distribution function.
"""

from typing import Callable, Iterable, NamedTuple
import pathlib
import importlib.metadata

import pandas as pd
import scipy.stats

__VERSION__ = importlib.metadata.version("namebaseline")

CharTranslator = Callable[[str], str]
StrTranslator = Callable[[str], str]

DEFAULT_CHARSET_LOWER = list(r"abcdefghijklmnopqrstuvwxyz0123456789")
DEFAULT_CHARSET_FULL = list(r"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")

DEFAULT_STR_TRANSLATOR = str.maketrans(
    "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿĀāĂăĄą"\
    "ĆćĈĉĊċČčĎďĐđĒēĔĕĖėĘęĚěĜĝĞğĠġĢģĤĥĦħĨĩĪīĭĮįİıĴĵĶķĸĹĺĻļĽľĿŀŁłŃńŅņŇňŉŊŋ"\
    "ŌōŎŏŐőŒœŔŕŖŗŘřŚśŜŝŞşŠšŢţŤťŦŧũŪūŭŮůŰűŲųŴŵŶŷŸŹźŻżŽžḁḂḆḉḋḍḏḐḑḓḔḕḙḛ"\
    "ḣḤḥḦḧḨḫḬḭḮḯḲḳḵḷḻḼḽḾḿṀṁṂṃṅṆṇṋṍṏṑṔṕṙṝṞṟṠṡṣṥṦṨṩṬṭṯṰṱṳṹṼṾṿẁẄẆẏẑẗẘẙ"\
    "ẚẞẠạẢảấẦầẨẩẪẫậẮắẰằẲẳẴẵẶặẸẹẺẻẽếềỂểỄễỆệỉỊịỌọỏỐốồỔổỗộỚớờỞởỠỡợ"\
    "ỤụủỨứừỬửữựỳỵỷỸỹἑὂΆῖῥῶ",
    "AAAAAAACEEEEIIIIDNOOOOOOUUUUYBBaaaaaaaceeeeiiiidnoooooouuuuybyAaAaAa"\
    "CcCcCcCcDdDdEeEeEeEeEeGgGgGgGgHhHhIiIiiIiIiJjKkKLlLlLlLlLlNnNnNnnNn"\
    "OoOoOoOoRrRrRrSsSsSsSsTtTtTtuUuuUuUuUuWwYyYZzZzZzaBbcdddDddEeee"\
    "hHhHhHhIiIiKkkllLlMmMmMmnNnnoooPprrRrSsssSSsTttTtuuVVvwWWyztwy"\
    "aBAaAaaAaAaAaaAaAaAaAaAaEeEeeeeEeEeEeiIiOooOooOoooOooOoOoo"\
    "UuuUuuUuuuyyyYyeoAipw",
    r"")

def default_str_translator(v: str) -> str:
    """The default str translator function"""
    return v.translate(DEFAULT_STR_TRANSLATOR)

class StrToFloatConverter:
    """Converts strings to floating point values"""

    def __init__(self, ignore_case: bool = True,
                 char_translator: CharTranslator|None = None,
                 str_translator: StrTranslator|None = default_str_translator,
                 ignore_missing: bool = True):
        self._ignore_case : bool = ignore_case
        self._char_translator = char_translator
        self._str_translator = str_translator
        self._ignore_missing : bool = ignore_missing
        # Default to ASCII character set
        self.charset = DEFAULT_CHARSET_FULL
        if ignore_case:
            self.charset = DEFAULT_CHARSET_LOWER

    def build_charset(self, corpus: Iterable[str], ignore_whitespace: bool = True):
        """Build a character set from a corpus of strings"""
        charset: set[str] = set()
        for s in corpus:
            if ignore_whitespace:
                s = s.replace(" ", "")
            charset.update(list(s))
        self.charset = list(sorted(charset))

    def convert(self, v: str) -> float:
        """Converts a string to a floating point value between 0 and 1.
        Returns -1 if no characters were used in the calculation.
        :param v: The string to convert
        :param ignorecase: Treat all characters as lowercase
        """
        accumulator = 0.0
        length = 0
        base = len(self.charset)
        if callable(self._str_translator):
            v = self._str_translator(v)
        if self._ignore_case:
            v = v.lower()
        for c in v:
            if callable(self._char_translator):
                c = self._char_translator(c)
            if c not in self.charset:
                if self._ignore_missing:
                    continue
                raise ValueError(f"'{c}' not in charset. String: {v}")
            exp = -length - 1
            accumulator += self.charset.index(c) * (base ** exp)
            length += 1
        if length == 0:
            return -1
        return accumulator

def read_cdf(file: str|pathlib.Path) -> pd.DataFrame:
    """Reads a CDF from a file that was saved using write_cdf()"""
    return pd.read_json(file)

def write_cdf(file: str|pathlib.Path, df: pd.DataFrame):
    """Write a CDF to a file for later retrieval"""
    df.to_json(file)

def str_cumdf(values: pd.Series, converter: StrToFloatConverter|None = None,
              num_bins: int|None = 1000, strip_empty: bool = True) -> pd.DataFrame:
    """Calculate the cumulative distribution function for a series of string values.
    The resulting DataFrame will consist of:
        values: bins in the range of 0...1, with the value being the left edge of the bin
        count: the number of observations in the bin
        cumsum: the cumulative distribution function
    """
    if converter is None:
        converter = StrToFloatConverter()
    counts = pd.DataFrame(dtype=(float,float))
    counts['value'] = values.apply(converter.convert)

    result = None

    if isinstance(num_bins, int):
        # Generate bins
        tuples = [(-1.0, 0.0)] # Initial bin is for non-convertible strings
        labels = [-1.0]
        interval = 1.0 / num_bins
        lower = 0.0
        while lower < 1.0:
            tuples.append((lower, lower + interval))
            labels.append(lower)
            lower += interval
        bins = pd.IntervalIndex.from_tuples(tuples, closed="left")

        # Create histogram
        counts['bin'] = pd.cut(counts['value'], bins, retbins=False)
        counts['value'] = counts['bin'].apply(lambda x: x.left)

        result = counts.value_counts(subset=['value'], dropna=False)\
            .reset_index()
    else:
        result = counts.value_counts(subset=['value'], dropna=False)\
            .reset_index()

    result.sort_values(by=["value"], inplace=True)
    if strip_empty:
        # Exclude values < 0 from cumsum
        result.drop(result[result['value'] < 0].index, inplace=True)
    result['cumsum'] = result['count'].cumsum()
    # Scale values to a cumulative distribution function from 0...1
    result['cumsum'] = result['cumsum'] / result['cumsum'].max()
    return result

class Chi2Stats(NamedTuple):
    """Data class for the Chi2 Goodness-of-Fit Test Results"""
    follows_baseline: bool
    x2: float
    x2_crit: float
    alpha: float
    df: float
    n: int

def chi2_gof_test(baseline: pd.DataFrame, sample: pd.DataFrame, alpha: float=0.05) -> Chi2Stats:
    """Chi2 Goodness-of-Fit test between the baseline CDF and the sample
    H_0: the sample follows the baseline, H_a: the sample does not follow the baseline
    """
    rows, _ = baseline.shape
    for i in range(rows):
        # Sanity check the rows
        if baseline.iloc[i]['value'] != sample.iloc[i]['value']:
            raise ValueError(
                f"Mismatch between sample and baseline CDF. baseline[{i}] "\
                f"({baseline.iloc[i]['value']}) != sample[{i}] "\
                f"({sample.iloc[i]['value']})")

    n_sample_size = sample['count'].sum()
    df = baseline.shape[0]-1

    x2_crit: float = scipy.stats.chi2.ppf(1-alpha, df)

    x2 = 0.0

    for i in range(rows):
        if i == 0:
            e_i = n_sample_size * (baseline.iloc[i]['cumsum'])
        else:
            e_i = n_sample_size * (baseline.iloc[i]['cumsum'] - baseline.iloc[i-1]['cumsum'])
        if e_i == 0.0:
            # Skip where expected counts == 0 to avoid divide-by-zero
            continue
        x = ((sample.iloc[i]['count'] - e_i) ** 2) / e_i
        x2 += x

    return Chi2Stats(
        follows_baseline = bool(x2 <= x2_crit),
        x2 = x2,
        x2_crit=x2_crit,
        alpha=alpha,
        df=df,
        n=n_sample_size
    )
