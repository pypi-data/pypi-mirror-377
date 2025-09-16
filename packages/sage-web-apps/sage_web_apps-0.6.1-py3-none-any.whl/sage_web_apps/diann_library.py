#!/usr/bin/env python3
"""
Convert Sage search results to DIA-NN spectral library format.
"""

import argparse
import sys
from pathlib import Path
import polars as pl


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert Sage search results to DIA-NN spectral library format"
    )
    
    parser.add_argument(
        "folder",
        type=Path,
        help="Folder containing results.sage.tsv and matched_fragments.sage.tsv files"
    )
    
    parser.add_argument(
        "--fdr",
        type=float,
        default=0.01,
        help="FDR threshold (default: 0.01 for 1%%)"
    )
    
    parser.add_argument(
        "--fdr-type",
        choices=["spectrum", "peptide", "protein"],
        default="spectrum",
        help="FDR type to filter on (default: spectrum)"
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (default: diann_library.tsv in input folder)"
    )
    
    return parser.parse_args()


def validate_input_files(folder: Path):
    """Validate that required input files exist."""
    results_file = folder / "results.sage.tsv"
    fragments_file = folder / "matched_fragments.sage.tsv"
    
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")
    
    if not results_file.exists():
        raise FileNotFoundError(f"Results file not found: {results_file}")
    
    if not fragments_file.exists():
        raise FileNotFoundError(f"Fragments file not found: {fragments_file}")
    
    return results_file, fragments_file


def load_and_filter_data(results_file: Path, fragments_file: Path, fdr: float, fdr_type: str):
    """Load and filter the Sage results data."""
    # Map FDR type to column name
    fdr_column_map = {
        "spectrum": "spectrum_q",
        "peptide": "peptide_q", 
        "protein": "protein_q"
    }
    
    fdr_column = fdr_column_map[fdr_type]
    
    print(f"Loading data and filtering with {fdr_type} FDR <= {fdr}")
    
    # Load and filter results
    lib = pl.read_csv(str(results_file), separator='\t').filter(
        pl.col(fdr_column).le(fdr) & pl.col("label").eq(1)
    ).join(
        pl.read_csv(str(fragments_file), separator='\t'),
        on="psm_id"
    )
    
    print(f"Loaded {len(lib)} PSMs after filtering")
    return lib


def build_diann_library(lib: pl.DataFrame) -> pl.DataFrame:
    """Convert Sage data to DIA-NN library format."""
    return lib.select(
        (pl.col("calcmass") / pl.col("charge"))
        .add(1.0072764)
        .cast(pl.Float32)
        .alias("PrecursorMz"),
        pl.col("fragment_mz_calculated").alias("ProductMz"),
        pl.concat_str(
            pl.col("fragment_type"),
            pl.col("fragment_ordinals").cast(pl.String),
            pl.lit("^"),
            pl.col("fragment_charge").cast(pl.String),
        ).alias("Annotation"),
        pl.col("proteins").str.split(";").list.first().alias("ProteinId"),
        pl.col("peptide").str.replace_all("[^A-Z]", "").alias("PeptideSequence"),
        pl.col("peptide")
        .str.replace_all("M[+15.9949]", "M(UniMod:35)", literal=True)
        .str.replace_all("C[+57.0215]", "C(UniMod:4)", literal=True)
        .alias("ModifiedPeptideSequence"),
        pl.col("charge").cast(pl.Int64).alias("PrecursorCharge"),
        pl.col("fragment_intensity").alias("LibraryIntensity"),
        pl.col("rt").alias("RT"),
        pl.lit("").alias("PrecursorIonMobility"),
        pl.col("fragment_type").alias("FragmentType"),
        pl.col("fragment_charge").alias("FragmentCharge"),
        pl.col("fragment_ordinals").alias("FragmentSeriesNumber"),
        pl.lit("").alias("FragmentLossType"),
        pl.col("proteins").alias("AllMappedProteins"),
        pl.when(pl.col("proteins").str.split(";").list.len().eq(1))
        .then(pl.lit(1))
        .otherwise(pl.lit(0))
        .alias("Proteotypic"),
    )


def main():
    """Main function."""
    try:
        args = parse_arguments()
        
        # Validate input files
        results_file, fragments_file = validate_input_files(args.folder)
        
        # Set output file
        if args.output is None:
            output_file = args.folder / "diann_library.tsv"
        else:
            output_file = args.output
        
        # Load and filter data
        lib = load_and_filter_data(results_file, fragments_file, args.fdr, args.fdr_type)
        
        if len(lib) == 0:
            print(f"Warning: No PSMs found after filtering with {args.fdr_type} FDR <= {args.fdr}")
            return
        
        # Convert to DIA-NN format
        print("Converting to DIA-NN library format...")
        diann_lib = build_diann_library(lib)
        
        # Write output
        print(f"Writing library to: {output_file}")
        diann_lib.write_csv(str(output_file), separator='\t')
        
        print(f"Successfully created DIA-NN library with {len(diann_lib)} entries")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()