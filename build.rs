use std::{env, fs, io::Write, path::Path};

use glob::glob;

fn main() {
    let out_dir = env::var_os("OUT_DIR").unwrap();
    let dest_path = Path::new(&out_dir).join("subsets.rs");
    let mut out_handle = fs::File::create(&dest_path).unwrap();
    let mut all_subsets: Vec<String> = vec![];

    for file in glob("Lib/gfsubsets/data/*_unique-glyphs.nam")
        .expect("Couldn't glob")
        .flatten()
    {
        let contents = fs::read_to_string(&file).expect("Couldn't read file");
        let orig_name = file
            .file_stem()
            .unwrap()
            .to_str()
            .unwrap()
            .replace("_unique-glyphs", "");
        let array_name = orig_name.replace("-", "_").to_uppercase();
        let mut codepoints = Vec::new();
        for line in contents.lines() {
            if !line.starts_with("0x") {
                continue;
            }
            let codepoint = line.split_whitespace().next().unwrap();
            codepoints.push(codepoint);
        }
        out_handle
            .write_all(
                format!(
                    "/// Codepoints for the subset '{}'\npub const {}: [u32; {}] = [{}];\n",
                    orig_name,
                    array_name,
                    codepoints.len(),
                    codepoints.join(", ")
                )
                .as_bytes(),
            )
            .unwrap();
        all_subsets.push(format!("(\"{}\", &{}),", orig_name, array_name));
    }
    out_handle
        .write_all(
            format!(
                "/// All subsets in the form of (name, array)\npub const SUBSETS: [(&str, &[u32]); {}] = [{}];\n",
                all_subsets.len(),
                all_subsets.join("\n")
            )
            .as_bytes(),
        )
        .expect("Couldn't write");
    out_handle.flush().unwrap();
    println!("cargo::rerun-if-changed=Lib/gfsubsets/data");
}
