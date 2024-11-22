//! Google Fonts Subsets
//!
//! This is the collection of nam files (codepoint subsets) that are used
//! to subset fonts before serving on the Google Fonts CSS API.
//!
//! It exports the subsets as arrays of codepoints - for example,
//! the `latin` subset is exported as `LATIN: [u32; ...] = [0x0, 0x0d, ...];`.
//!
//! It also exports the `SUBSETS` array, which is a list of all subsets in
//! the form of `(&str, &[u32])` tuples.
//! This is useful for iterating over all subsets.
include!(concat!(env!("OUT_DIR"), "/subsets.rs"));
