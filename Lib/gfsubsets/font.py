import contextlib
from typing import List, Optional

from fontTools import ttLib
from shaperglot import Checker, Language, Languages

from gfsubsets.subsets import SUBSETS

_PLATFORM_ID_MICROSOFT = 3
_PLATFORM_ENC_UNICODE_BMP = 1
_PLATFORM_ENC_UNICODE_UCS4 = 10
_PLATFORM_ENCS_UNICODE = (_PLATFORM_ENC_UNICODE_BMP, _PLATFORM_ENC_UNICODE_UCS4)


def UnicodeCmapTables(font):
    """Find unicode cmap tables in font.

    Args:
      font: A TTFont.
    Yields:
      cmap tables that contain unicode mappings
    """
    for table in font["cmap"].tables:
        if (
            table.platformID == _PLATFORM_ID_MICROSOFT
            and table.platEncID in _PLATFORM_ENCS_UNICODE
        ):
            yield table


def CodepointsInFont(font_filename):
    """Returns the set of codepoints present in the font file specified.

    Args:
      font_filename: The name of a font file.
    Returns:
      A set of integers, each representing a codepoint present in font.
    """

    font_cps = set()
    with contextlib.closing(ttLib.TTFont(font_filename)) as font:
        for t in UnicodeCmapTables(font):
            font_cps.update(t.cmap.keys())

    return font_cps


def supported_languages(file_path) -> List[str]:
    checker = Checker(file_path)
    langs = Languages()
    supported: List[Language] = [
        lang for lang in sorted(langs.keys()) if checker.check(langs[lang]).score > 80
    ]
    return supported


def subset_for_lang(lang: Language) -> Optional[str]:
    from gfsubsets import CodepointsInSubset

    bases = set(ord(cp) for base in lang.bases for cp in base)
    if not bases:
        return None

    potential_subsets = []
    for subset in SUBSETS:
        cps = CodepointsInSubset(subset)
        if bases.issubset(cps):
            potential_subsets.append((subset, len(bases) / len(cps)))
    # Find the potential subset which most tightly matches the language's bases
    if not potential_subsets:
        return None
    return max(potential_subsets, key=lambda x: x[1])[0]


def SubsetsInFont(
    file_path: str,
    satisfies_ratio_threshold: float = 0.5,
    usage_ratio_threshold: float = 0.1,
) -> List[str]:
    """
    Returns the subsets of a font that cover the most codepoints for the languages supported by the font,
    as defined by shaperglot.

    For non-linguistic subsets, a heuristic is used which balances the number of codepoints covered in the font
    against the cost of adding that subset (i.e. the ratio between the number of codepoints covered and the number of codepoints
    in the subset)

    Args:
        file_path: Path to the font file.
        satisfies_ratio_threshold: Threshold for the ratio of codepoints covered to the number of codepoints in the subset.
        usage_ratio_threshold: Threshold for the ratio of codepoints covered to the total number of un-covered codepoints in the font.
    """
    from gfsubsets import CodepointsInSubset

    subsets = set([])

    all_cps = CodepointsInFont(file_path)
    languages = Languages()

    for lang_id in supported_languages(file_path):
        lang = languages[lang_id]
        subset = subset_for_lang(lang)
        if subset:
            subsets.add(subset)
            all_cps -= CodepointsInSubset(subset)
    # Now find subsets for the remaining, non-linguistic codepoints (music, symbols etc.)
    # Subsets must satisfy a majority of the remaining codepoints, but at the same time
    # we want to be careful here not just to add an entire subset for one or two codepoints.
    for subset in SUBSETS:
        if not all_cps:
            break
        num_cps = len(CodepointsInSubset(subset))
        num_satisfied = len(CodepointsInSubset(subset) & all_cps)
        satisfies_ratio = num_satisfied / len(all_cps)
        usage_ratio = num_satisfied / num_cps
        # print(
        #     f"Considering {subset} (satisfies_ratio={satisfies_ratio:.2f}, usage_ratio={usage_ratio:.2f})"
        # )
        if satisfies_ratio > satisfies_ratio_threshold and (
            usage_ratio > usage_ratio_threshold or subset == "latin-ext"
        ):
            subsets.add(subset)
            all_cps -= CodepointsInSubset(subset)
    return list(subsets)
