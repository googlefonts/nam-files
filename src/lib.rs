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
use std::collections::HashSet;

include!(concat!(env!("OUT_DIR"), "/subsets.rs"));

const CONTROL_CHARS: [u32; 4] = [0x0000, 0x000D, 0x0020, 0x00A0];

pub fn subsets_in_font(
    codepoints: &HashSet<u32>,
    min_pct: f32,
    ext_min_pct: Option<f32>,
) -> Vec<&'static str> {
    let active_codepoints = codepoints
        .iter()
        .filter(|cp| !CONTROL_CHARS.contains(cp))
        .collect::<HashSet<_>>();
    let mut subsets = vec![];
    for (subset, subset_codepoints) in SUBSETS.iter() {
        let mut subset_codepoints = subset_codepoints.iter().collect::<HashSet<_>>();
        if subset == &"Khmer" {
            // Remove LATIN
            subset_codepoints.retain(|cp| !LATIN.contains(cp));
        }
        let target_pct = if subset.ends_with("-ext") {
            ext_min_pct.unwrap_or(min_pct)
        } else {
            min_pct
        };

        let overlap = active_codepoints.intersection(&subset_codepoints).count() as f32;
        if 100.0 * overlap / subset_codepoints.len() as f32 >= target_pct {
            subsets.push(*subset);
        }
    }
    subsets
}
