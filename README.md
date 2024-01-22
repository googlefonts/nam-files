# gfsubsets

This is the collection of nam files (codepoint subsets) that are used to subset fonts before serving on the Google Fonts CSS API.

## The subset files

The subset definitions are contained in two forms; the "editable" definitions
are found in the `subsets-input` directory, and the machine readable defitions
can be found in `Lib/gfsubsets/data`.

The machine readable files consist of text files with one Unicode codepoint
(a hexadecimal number beginning with `0x`) on each line; everything after the
codepoint is a comment. Blank lines and comment lines beginning `#` are
ignored.

The editable definitions are similar, but for convenience allow the following
"directives":

* Two codepoints separated by `..` denote an (inclusive) range; all codepoints
  within the range are included.
* The symbol `-` before a codepoint or range excludes it from the output set.
* The directive `@include(filename)` includes the codepoints in `filename`.
* The directive `@block(XYZ)` includes the codepoints in the Unicode block
  named `XYZ`.
* The directive `@script(XYZ)` includes all codepoints with either the
  Unicode `Script` property equal to `XYZ` or the `ScriptExtensions` property
  equal to XYZ

These editable definitions are turned into their machine-readable equivalents
using the script `scripts/preprocess_namfile.py`.

## Python interface

This repository also includes the Python module `gfsubsets` which provides
an interface to these subset definitions. It exports the following functions:

* `CodepointsInFont(filename)`: Lists the Unicode codepoints supported by the font
* `ListSubsets()`: Returns the name of all defined subsets.
* `SubsetsForCodepoint(cp)`: Returns the names of all subsets including the codepoint.
* `SubsetForCodepoint(cp)`: Returns the name of the "most relevant" subset including the codepoint.
* `CodepointsInSubset(subset)`: Returns a set of codepoints included in the subset.
* `SubsetsInFont(filename, min_pct, ext_min_pct)`: Returns the name of subsets "well" supported by a font.
