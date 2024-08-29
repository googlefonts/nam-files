from collections import defaultdict
from gfsubsets import ListSubsets, CodepointsInSubset

ALLOWED = set(
    [
        0x0,
        0x20,
        0x000D,  # CARRIAGE RETURN
        0x002D,  # HYPHEN-MINUS
        0x00A0,  # NO-BREAK SPACE
        0x25CC,  # DOTTED CIRCLE
        0x200B,  # ZERO WIDTH SPACE
        0x200C,  # ZERO WIDTH NON-JOINER
        0x200D,  # ZERO WIDTH JOINER
        0x2010,  # HYPHEN
    ]
)

# Latin kernel gets *everywhere*
ALLOWED |= set(range(0x30, 0x7F))

SKIP_SUBSETS = [
    "chinese-simplified",
    "chinese-traditional",
    "chinese-hongkong",
    "japanese",
    "yi",
    "meroitic",
]

# Grandfather existing problems; we just don't want to make things worse.
EXISTING = [
    0x001D,
    range(0x0021, 0x002D),
    range(0x002E, 0x0030),
    0x00A7,
    range(0x00AB, 0x00AE),
    range(0x00B0, 0x00B2),
    0x00B7,
    0x00BB,
    0x00D7,
    0x00F7,
    range(0x0102, 0x0104),
    range(0x0110, 0x0112),
    range(0x0128, 0x012A),
    0x0131,
    range(0x0168, 0x016A),
    range(0x01A0, 0x01A2),
    range(0x01AF, 0x01B1),
    0x02BC,
    0x02C7,
    0x02DA,
    range(0x0300, 0x030A),
    range(0x030B, 0x030D),
    range(0x0323, 0x0325),
    0x0329,
    range(0x0330, 0x0332),
    range(0x0374, 0x0376),
    range(0x0391, 0x03A2),
    range(0x03A3, 0x03AA),
    range(0x03B1, 0x03CA),
    0x03D1,
    range(0x03D5, 0x03D7),
    0x03DA,
    0x03DC,
    0x03DE,
    range(0x03E2, 0x03F2),
    range(0x03F4, 0x03F6),
    range(0x0483, 0x0485),
    0x0487,
    0x0589,
    0x060C,
    range(0x061B, 0x061D),
    0x061F,
    0x0621,
    0x0627,
    0x0640,
    range(0x064B, 0x0656),
    range(0x0660, 0x066D),
    0x0670,
    0x06D4,
    range(0x06F0, 0x06FA),
    0x093D,
    range(0x0951, 0x0953),
    range(0x0964, 0x0970),
    range(0x09E6, 0x09F0),
    range(0x09F4, 0x09F8),
    range(0x0A66, 0x0A70),
    range(0x0AE6, 0x0AF0),
    0x0BAA,
    0x0BB5,
    range(0x0BE6, 0x0BF4),
    range(0x0CE6, 0x0CF0),
    range(0x1040, 0x104A),
    range(0x1735, 0x1737),
    range(0x1801, 0x1804),
    0x1805,
    0x1CD0,
    range(0x1CD2, 0x1CD4),
    range(0x1CD5, 0x1CDB),
    range(0x1CDC, 0x1CDE),
    range(0x1CE0, 0x1CE2),
    range(0x1CE9, 0x1CEB),
    0x1CED,
    range(0x1CF2, 0x1CFA),
    range(0x1EF2, 0x1EFA),
    0x2002,
    range(0x200E, 0x2010),
    0x2011,
    range(0x2013, 0x2015),
    range(0x2018, 0x201B),
    range(0x201C, 0x201F),
    0x2020,
    0x2022,
    0x2026,
    range(0x2032, 0x2034),
    range(0x2039, 0x203B),
    0x2044,
    0x204F,
    0x205A,
    0x20A8,
    range(0x20AA, 0x20AC),
    0x20B4,
    0x20B9,
    0x20DB,
    0x20F0,
    range(0x2190, 0x219A),
    0x2212,
    0x2215,
    range(0x2218, 0x221A),
    0x2299,
    range(0x22C4, 0x22C7),
    range(0x2308, 0x230C),
    range(0x231C, 0x2320),
    0x237C,
    0x23AF,
    0x23D0,
    range(0x2460, 0x2476),
    0x25AF,
    0x25B3,
    0x25B7,
    0x25BD,
    0x25C1,
    0x25CA,
    0x25FB,
    0x262C,
    range(0x2669, 0x2672),
    range(0x2800, 0x2900),
    range(0x2921, 0x2923),
    0x2981,
    0x29BF,
    0x29EB,
    0x2E31,
    0x2E41,
    range(0x3000, 0x3003),
    range(0x3008, 0x3010),
    0xA66F,
    range(0xA78B, 0xA78D),
    range(0xA830, 0xA83A),
    0xA8F1,
    0xA92E,
    0xA9CF,
    range(0xFD3E, 0xFD40),
    0xFDF2,
    0xFDFD,
    0xFE00,
    range(0xFE24, 0xFE27),
    range(0xFE2E, 0xFE30),
    range(0x10100, 0x10103),
    range(0x10107, 0x10134),
    range(0x10137, 0x10140),
    range(0x102E0, 0x102FC),
    0x10AF2,
    range(0x10E60, 0x10E7F),
    range(0x11FD0, 0x11FD2),
    0x11FD3,
    range(0x1D2E0, 0x1D2F4),
    range(0x1EE00, 0x1EE04),
    range(0x1EE05, 0x1EE20),
    range(0x1EE21, 0x1EE23),
    0x1EE24,
    0x1EE27,
    range(0x1EE29, 0x1EE33),
    range(0x1EE34, 0x1EE38),
    0x1EE39,
    0x1EE3B,
    0x1EE42,
    0x1EE47,
    0x1EE49,
    0x1EE4B,
    range(0x1EE4D, 0x1EE50),
    range(0x1EE51, 0x1EE53),
    0x1EE54,
    0x1EE57,
    0x1EE59,
    0x1EE5B,
    0x1EE5D,
    0x1EE5F,
    range(0x1EE61, 0x1EE63),
    0x1EE64,
    range(0x1EE67, 0x1EE6B),
    range(0x1EE6C, 0x1EE73),
    range(0x1EE74, 0x1EE78),
    range(0x1EE79, 0x1EE7D),
    0x1EE7E,
    range(0x1EE80, 0x1EE8A),
    range(0x1EE8B, 0x1EE9C),
    range(0x1EEA1, 0x1EEA4),
    range(0x1EEA5, 0x1EEAA),
    range(0x1EEAB, 0x1EEBC),
    range(0x1EEF0, 0x1EEF2),
]
for e in EXISTING:
    if isinstance(e, int):
        ALLOWED.add(e)
    else:
        ALLOWED |= set(e)


def test_overlaps():
    cp_coverage = defaultdict(list)
    for subset in ListSubsets():
        if subset in SKIP_SUBSETS:
            continue
        for cp in CodepointsInSubset(subset, unique_glyphs=True):
            if cp in ALLOWED:
                continue
            cp_coverage[cp].append(subset)
    failed = []
    for cp, subsets in sorted(cp_coverage.items()):
        if len(subsets) > 1:
            print(f"Codepoint U+{cp:04X} is in multiple subsets: {', '.join(subsets)}")
            failed.append(cp)
    assert not failed