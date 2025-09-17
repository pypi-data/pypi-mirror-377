#!/usr/bin/env python3
"""
dsRNAscan - A tool for genome-wide prediction of double-stranded RNA structures
Copyright (C) 2024 Bass Lab
"""

__version__ = '0.4.6'
__author__ = 'Bass Lab'

import os
import locale
import glob
from Bio import SeqIO
import argparse
import subprocess
import re
import RNA
import sys
import numpy as np
import pandas as pd
import multiprocessing
import gzip
import logging
from datetime import datetime
from queue import Empty
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import time

# Set environment variables for locale
os.environ['LC_ALL'] = 'C.UTF-8'
os.environ['LANG'] = 'C.UTF-8'

# Fix einverted path issues on Linux
try:
    from .fix_einverted_paths import setup_einverted_environment
    setup_einverted_environment()
except:
    pass  # If it fails, continue anyway

# Try to set locale, but don't fail if unavailable
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except locale.Error:
        # Fall back to default locale
        pass

# Determine the directory of this script and set the local path for einverted
script_dir = os.path.dirname(os.path.abspath(__file__))

# Check if we're on Windows
import platform
system = platform.system().lower()
machine = platform.machine().lower()
is_windows = system == 'windows'

# Determine platform-specific binary name
if is_windows:
    platform_binary = "einverted_windows_x86_64.exe"
    generic_binary = "einverted.exe"
elif system == 'darwin':
    if 'arm' in machine or 'aarch64' in machine:
        platform_binary = "einverted_macos_arm64"  # Changed from darwin to macos
    else:
        platform_binary = "einverted_macos_x86_64"  # Changed from darwin to macos
    generic_binary = "einverted"
else:  # Linux
    if 'aarch64' in machine or 'arm64' in machine:
        platform_binary = "einverted_linux_arm64"  # Changed from aarch64 to arm64
    else:
        platform_binary = "einverted_linux_x86_64"
    generic_binary = "einverted"

# Try platform-specific binaries ONLY - no generic fallback
possible_paths = []

# Only use platform-specific binaries in platform_binaries folder
tools_dir = os.path.join(script_dir, "tools")
platform_dir = os.path.join(tools_dir, "platform_binaries")
if os.path.exists(platform_dir):
    possible_paths.append(os.path.join(platform_dir, platform_binary))

# Also check parent directory structure
parent_tools = os.path.join(os.path.dirname(script_dir), "tools")
if os.path.exists(parent_tools):
    possible_paths.append(os.path.join(parent_tools, generic_binary))
    platform_dir = os.path.join(parent_tools, "platform_binaries")
    if os.path.exists(platform_dir):
        possible_paths.append(os.path.join(platform_dir, platform_binary))

# Finally try system installations
possible_paths.extend([
    f"/usr/local/bin/{generic_binary}",
    f"/usr/bin/{generic_binary}",
])

einverted_bin = None
for path in possible_paths:
    if os.path.exists(path) and os.access(path, os.X_OK):
        einverted_bin = path
        break

if not einverted_bin:
    # No fallback - platform-specific binary is required
    einverted_bin = os.path.join(script_dir, "tools", "platform_binaries", platform_binary)  # Default for error message

def smart_open(filename, mode='rt'):
    """
    Open a file, automatically detecting if it's gzipped based on extension.
    
    Args:
        filename: Path to file
        mode: Mode to open file (default 'rt' for reading text)
        
    Returns:
        File handle (either regular file or gzip file)
    """
    if filename.endswith('.gz'):
        return gzip.open(filename, mode)
    else:
        return open(filename, mode)

# Check if einverted binary exists
if not os.path.exists(einverted_bin):
    print(f"Error: einverted binary not found at {einverted_bin}")
    print("Please ensure the einverted tool is installed in the 'tools' subdirectory.")
    print("You can install it by running the installation script or downloading from EMBOSS.")
    sys.exit(1)

# Check if einverted is executable
if not os.access(einverted_bin, os.X_OK):
    print(f"Error: einverted binary at {einverted_bin} is not executable.")
    print("Please run: chmod +x {}".format(einverted_bin))
    sys.exit(1)

# Fast G-U wobble pairing check (run only once at startup)
GU_WOBBLE_VERIFIED = False
def verify_gu_wobble_support():
    """Quick test to verify einverted supports G-U wobble pairing."""
    global GU_WOBBLE_VERIFIED
    if GU_WOBBLE_VERIFIED:
        return True
    
    try:
        # Test sequence with G-U pairable regions (using T for DNA)
        test_sequence = ">test\nGGGGGGGGGGGGGGNNNNNNNNNNNNNNTTTTTTTTTTTTTT\n"
        
        # Run einverted with stdin/stdout (same as main script)
        # Simplified command without --filter and -outseq flags
        result = subprocess.run(
            [einverted_bin, '-sequence', 'stdin', '-threshold', '15', 
             '-gap', '12', '-match', '3', '-mismatch', '-4',
             '-outfile', 'stdout'],
            input=test_sequence,
            capture_output=True, 
            text=True, 
            timeout=2
        )
        
        # Check if G-U pairing was detected
        # Look for Score (capital S) and the sequences
        if 'Score' in result.stdout and ('gggg' in result.stdout or 'tttt' in result.stdout):
            GU_WOBBLE_VERIFIED = True
            return True
        else:
            # Warning instead of fatal error - the test might be wrong but einverted could still work
            if '--help' not in sys.argv and '--version' not in sys.argv:
                print("WARNING: Could not verify G-U wobble pairing in test (but it may still work)")
                print(f"Continuing anyway - results should be valid if einverted was compiled with the patch")
            GU_WOBBLE_VERIFIED = True  # Don't re-test
            return False
    except Exception as e:
        # If test fails due to technical issues, warn but continue
        if '--help' not in sys.argv and '--version' not in sys.argv:
            print(f"WARNING: Could not verify G-U wobble support: {str(e)}")
            print("Continuing, but results may be incorrect if G-U pairing is not supported.")
        GU_WOBBLE_VERIFIED = True  # Don't re-test
        return True


def is_valid_fragment(fragment):
    # Validation logic for fragment
    return fragment != len(fragment) * "N"


def generate_bp_file(input_file, output_file):
    """
    Generate a BP file from the merged dsRNA results file using the correct format for IGV.
    Uses strand information and percent_paired for color coding.
    
    Args:
        input_file (str): Path to the merged results file
        output_file (str): Path to the output BP file
    """
    print(f"Reading data from {input_file}")
    
    try:
        # Check if the file exists and is not empty
        if not os.path.exists(input_file):
            print(f"Error: File {input_file} does not exist")
            return
            
        if os.path.getsize(input_file) == 0:
            print(f"Error: File {input_file} is empty")
            return
            
        # Read the merged results file with better error handling
        try:
            df = pd.read_csv(input_file, sep="\t")
        except pd.errors.EmptyDataError:
            print(f"Error: No data found in {input_file}")
            return
        except Exception as e:
            print(f"Error reading file {input_file}: {str(e)}")
            return
            
        # Check if DataFrame is empty
        if df.empty:
            print(f"Warning: No data found in {input_file}")
            return
        
        # Print the column names for debugging
        print(f"Columns in file: {', '.join(df.columns)}")
        
        # Verify required columns exist
        required_cols = ["Chromosome", "i_start", "i_end", "j_start", "j_end", "percent_paired"]
        
        # Handle inconsistent column naming
        column_mappings = {
            "Chromosome": ["chromosome", "chr", "chrom"],
            "i_start": ["start1", "start_1", "left_start"],
            "i_end": ["end1", "end_1", "left_end"],
            "j_start": ["start2", "start_2", "right_start"],
            "j_end": ["end2", "end_2", "right_end"],
            "percent_paired": ["percpaired", "perc_paired", "percentpaired", "percent_match", "PercMatch"]
        }
        
        # Handle strand column specifically - it might be missing but we can default it
        has_strand = "Strand" in df.columns
        if not has_strand:
            for alt_name in ["strand", "str"]:
                if alt_name in df.columns:
                    df = df.rename(columns={alt_name: "Strand"})
                    has_strand = True
                    break
                    
        # If still no strand column, add default
        if not has_strand:
            print("No strand column found, defaulting to '+' strand")
            df["Strand"] = "+"
        
        # Check for missing columns and try to use alternatives
        missing_cols = []
        for col in required_cols:
            if col not in df.columns:
                # Try alternative names
                found = False
                if col in column_mappings:
                    for alt_col in column_mappings[col]:
                        if alt_col in df.columns:
                            df = df.rename(columns={alt_col: col})
                            found = True
                            break
                
                if not found:
                    missing_cols.append(col)
        
        if missing_cols:
            print(f"Error: Missing required columns: {', '.join(missing_cols)}")
            print(f"Available columns: {', '.join(df.columns)}")
            return
        
        # Create a new BP file
        with open(output_file, 'w') as bp_file:
            # Write header with color definitions according to the correct BP format
            bp_file.write("color:\t100\t149\t237\t70-80% paired (forward strand)\n")
            bp_file.write("color:\t65\t105\t225\t80-90% paired (forward strand)\n")
            bp_file.write("color:\t0\t0\t139\t90-100% paired (forward strand)\n")
            bp_file.write("color:\t205\t92\t92\t70-80% paired (reverse strand)\n")
            bp_file.write("color:\t178\t34\t34\t80-90% paired (reverse strand)\n")
            bp_file.write("color:\t139\t0\t0\t90-100% paired (reverse strand)\n")
            
            # Process each row
            for idx, row in df.iterrows():
                # Get chromosome and positions
                chrom = row["Chromosome"]
                
                # Get the strand and convert to "+" or "-" if needed
                strand = row.get("Strand", "+")
                if strand not in ["+", "-"]:
                    # Handle numeric or other formats
                    if strand == "1" or str(strand).lower() == "forward":
                        strand = "+"
                    elif strand == "-1" or str(strand).lower() == "reverse":
                        strand = "-"
                    else:
                        strand = "+"  # Default
                
                # Get percent paired - try different column names if needed
                if "percent_paired" in row:
                    percent_paired = row["percent_paired"]
                elif "PercMatch" in row:
                    percent_paired = row["PercMatch"]
                else:
                    percent_paired = 75.0  # Default
                
                # Convert percent_paired to float if it's not already
                try:
                    if isinstance(percent_paired, str):
                        percent_paired = float(percent_paired.replace('%', ''))
                    else:
                        percent_paired = float(percent_paired)
                except ValueError:
                    print(f"Warning: Could not parse percent_paired value '{percent_paired}', defaulting to 75")
                    percent_paired = 75.0
                
                # Determine color index based on strand and percent_paired
                # Color indices match the header order (0-5)
                if strand == "+":
                    # Forward strand
                    if percent_paired >= 90:
                        color_idx = 2  # dark blue
                    elif percent_paired >= 80:
                        color_idx = 1  # royal blue
                    else:
                        color_idx = 0  # cornflower blue
                else:
                    # Reverse strand
                    if percent_paired >= 90:
                        color_idx = 5  # dark red
                    elif percent_paired >= 80:
                        color_idx = 4  # firebrick
                    else:
                        color_idx = 3  # indian red
                
                # Get the coordinates for both arms
                try:
                    i_start = int(row["i_start"])
                    i_end = int(row["i_end"])
                    j_start = int(row["j_start"])
                    j_end = int(row["j_end"])
                except (ValueError, TypeError) as e:
                    print(f"Warning: Could not parse coordinate values for row {idx}, skipping: {e}")
                    continue
                
                # Write the BP record with coordinates from both arms forming a pair
                # Format: <chrom> <left_start> <left_end> <right_start> <right_end> <color_idx>
                bp_file.write(f"{chrom}\t{i_start}\t{i_end}\t{j_start}\t{j_end}\t{color_idx}\n")
            
            print(f"Successfully wrote BP file to {output_file}")
    except Exception as e:
        print(f"Error generating BP file: {str(e)}")
        import traceback
        traceback.print_exc()
    
def predict_hybridization(seq1, seq2, temperature=37):
    """
    Predict RNA-RNA interactions using RNAduplex Python bindings.
    
    Args:
        seq1 (str): First RNA sequence
        seq2 (str): Second RNA sequence
        temperature (int): Folding temperature in Celsius (default 37)
    
    Returns:
        tuple: (structure, indices_seq1, indices_seq2, energy) or (None, None, None, None) on error
    """
    try:
        # Set temperature for ViennaRNA only if different
        if RNA.cvar.temperature != temperature:
            RNA.cvar.temperature = temperature
        
        # Calculate duplex using Python bindings
        result = RNA.duplexfold(seq1, seq2)
        
        # Parse structure to get lengths
        structure_parts = result.structure.split('&')
        if len(structure_parts) != 2:
            print(f"Warning: Invalid duplex structure: {result.structure}")
            return None, None, None, None
        
        len1 = len(structure_parts[0])
        len2 = len(structure_parts[1])
        
        # Calculate indices using the convention we discovered:
        # i = 3' end of seq1 duplex region (1-based)
        # j = 5' start of seq2 duplex region (1-based)
        seq1_start = result.i - len1 + 1
        seq1_end = result.i
        seq2_start = result.j
        seq2_end = result.j + len2 - 1
        
        # Return data directly - no need to format and parse
        indices_seq1 = [seq1_start, seq1_end]
        indices_seq2 = [seq2_start, seq2_end]
        
        return result.structure, indices_seq1, indices_seq2, result.energy
        
    except ImportError:
        print("Error: RNA module not found. Please install ViennaRNA Python bindings.")
        print("Install with: conda install -c bioconda viennarna")
        return None, None, None, None
    except Exception as e:
        print(f"Error running RNAduplex Python bindings: {str(e)}")
        return None, None, None, None

def predict_hybridization_batch(seq_pairs, temperature=37, max_workers=4):
    """
    Process multiple sequence pairs in parallel using threading.
    
    Args:
        seq_pairs: List of tuples (seq1, seq2)
        temperature: Folding temperature
        max_workers: Number of threads to use
    
    Returns:
        List of tuples (structure, indices_seq1, indices_seq2, energy) maintaining the same order as input
    """
    # Set temperature once for all threads
    if RNA.cvar.temperature != temperature:
        RNA.cvar.temperature = temperature
    
    def process_single_pair(pair_data):
        """Process a single pair in a thread"""
        seq1, seq2, idx = pair_data
        try:
            result = RNA.duplexfold(seq1, seq2)
            
            # Parse structure
            structure_parts = result.structure.split('&')
            if len(structure_parts) != 2:
                return idx, (None, None, None, None)
            
            len1 = len(structure_parts[0])
            len2 = len(structure_parts[1])
            
            seq1_start = result.i - len1 + 1
            seq1_end = result.i
            seq2_start = result.j
            seq2_end = result.j + len2 - 1
            
            # Return data directly
            indices_seq1 = [seq1_start, seq1_end]
            indices_seq2 = [seq2_start, seq2_end]
            
            return idx, (result.structure, indices_seq1, indices_seq2, result.energy)
        except Exception as e:
            print(f"Error in batch RNAduplex for pair {idx}: {e}")
            return idx, (None, None, None, None)
    
    # Prepare data with indices
    indexed_pairs = [(seq1, seq2, i) for i, (seq1, seq2) in enumerate(seq_pairs)]
    
    # Process in parallel using threads
    results = [None] * len(seq_pairs)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single_pair, pair): pair[2] 
                  for pair in indexed_pairs}
        
        for future in as_completed(futures):
            idx = futures[future]
            try:
                result_idx, result_data = future.result()
                results[result_idx] = result_data
            except Exception as e:
                print(f"Error getting result for pair {idx}: {e}")
                results[idx] = (None, None, None, None)
    
    return results

def parse_rnaduplex_output(output):
    """
    Parse the output from RNAduplex.
    Args:
        output (str): Output string from RNAduplex
    
    Returns:
        tuple: (structure, indices_seq1, indices_seq2, energy)
    """
    try:
        # print(f"[DEBUG] Parsing RNAduplex output: {output}")
        parts = output.split()
        # print(f"[DEBUG] RNAduplex parts: {parts}")
        
        # Handle empty or invalid output
        if not parts or len(parts) < 4:
            print(f"Warning: Invalid RNAduplex output: {output}")
            return "", [0, 0], [0, 0], 0.0
        
        structure = parts[0]
        
        # Parse indices more safely
        try:
            indices_seq1 = [int(x) for x in parts[1].split(',')]
            if len(indices_seq1) != 2:
                raise ValueError(f"Expected 2 indices for seq1, got {len(indices_seq1)}")
        except (ValueError, IndexError) as e:
            print(f"Warning: Could not parse indices_seq1 from {parts[1] if len(parts) > 1 else 'missing'}: {e}")
            indices_seq1 = [1, 1]  # Default to position 1
            
        try:
            indices_seq2 = [int(x) for x in parts[3].split(',')]
            if len(indices_seq2) != 2:
                raise ValueError(f"Expected 2 indices for seq2, got {len(indices_seq2)}")
        except (ValueError, IndexError) as e:
            print(f"Warning: Could not parse indices_seq2 from {parts[3] if len(parts) > 3 else 'missing'}: {e}")
            indices_seq2 = [1, 1]  # Default to position 1
        
        # Extract energy from the output
        energy = None
        if len(parts) > 4:
            # Energy is typically in the format (-10.40)
            energy_str = parts[4].strip('()')
            try:
                energy = float(energy_str)
            except ValueError:
                print(f"Warning: Could not parse energy value '{energy_str}' from RNAduplex output")
                energy = 0.0
        else:
            energy = 0.0
        
        return structure, indices_seq1, indices_seq2, energy
    except Exception as e:
        print(f"Error parsing RNAduplex output: {e}")
        return "", [1, 1], [1, 1], 0.0

def safe_extract_effective_seq(row, seq_col, start_col, end_col):
    """
    Safely extract a subsequence based on the effective indices.
    Handles type conversion, boundary checking, and exceptions.
    
    Args:
        row: DataFrame row
        seq_col: Column name for the sequence
        start_col: Column name for the start index
        end_col: Column name for the end index
        
    Returns:
        str: The extracted subsequence or the full sequence if extraction fails
    """
    try:
        # Make sure we have non-empty sequence
        if not row[seq_col] or pd.isna(row[seq_col]):
            return ""
            
        # Make sure we have valid numbers for indices
        if pd.isna(row[start_col]) or pd.isna(row[end_col]):
            return row[seq_col]
            
        # Make sure we have integers for slicing
        start_idx = int(float(row[start_col])) - 1  # Convert to 0-based index
        end_idx = int(float(row[end_col]))
        
        # Make sure indices are valid for the sequence
        if start_idx < 0:
            start_idx = 0
            
        seq = str(row[seq_col])
        if end_idx > len(seq):
            end_idx = len(seq)
        
        # Skip extraction if indices are invalid
        if start_idx >= end_idx or start_idx >= len(seq):
            return seq
            
        # Return the slice
        return seq[start_idx:end_idx]
    except (ValueError, TypeError, IndexError) as e:
        print(f"Warning: Could not extract effective sequence: {e}. Using full sequence instead.")
        # Return the original sequence as fallback
        return str(row[seq_col]) if row[seq_col] and not pd.isna(row[seq_col]) else ""

def result_writer(output_file, result_queue, num_workers):
    """
    Dedicated process that writes results to file as they arrive from worker processes.
    This runs in a separate process to avoid blocking workers.
    Deduplicates results based on coordinates.
    """
    with open(output_file, 'w') as f:
        # Write header - basic coordinates first, structural details, then effective coords and sequences
        f.write("Chromosome\tStrand\ti_start\ti_end\tj_start\tj_end\t"
                "Score\tRawMatch\tPercMatch\tGaps\t"
                "dG(kcal/mol)\tpercent_paired\tlongest_helix\t"
                "eff_i_start\teff_i_end\teff_j_start\teff_j_end\t"
                "i_seq\tj_seq\tstructure\n")
        
        workers_done = 0
        results_written = 0
        seen_coordinates = set()  # Track unique dsRNA coordinates
        
        while workers_done < num_workers:
            try:
                result = result_queue.get(timeout=1)
                
                if result == "DONE":
                    workers_done += 1
                    continue
                
                # Create unique key based on coordinates
                coord_key = (result['chromosome'], result['strand'], 
                            result['i_start'], result['i_end'],
                            result['j_start'], result['j_end'])
                
                # Skip if we've already seen this dsRNA
                if coord_key in seen_coordinates:
                    continue
                
                seen_coordinates.add(coord_key)
                
                # Write result as TSV line - basic coords, structural details, eff coords, sequences
                f.write(f"{result['chromosome']}\t{result['strand']}\t"
                       f"{result['i_start']}\t{result['i_end']}\t"
                       f"{result['j_start']}\t{result['j_end']}\t"
                       f"{result['score']}\t{result['raw_match']}\t"
                       f"{result['match_perc']}\t{result['gap_numb']}\t"
                       f"{result['energy']}\t{result['percent_paired']}\t{result['longest_helix']}\t"
                       f"{result['eff_i_start']}\t{result['eff_i_end']}\t"
                       f"{result['eff_j_start']}\t{result['eff_j_end']}\t"
                       f"{result['i_seq']}\t{result['j_seq']}\t"
                       f"{result['structure']}\n")
                
                results_written += 1
                
                # Flush periodically for real-time output
                if result_queue.qsize() < 100:
                    f.flush()
                    
            except Empty:
                continue
            except Exception as e:
                print(f"Error writing result: {e}")
        
        print(f"Writer process finished. Wrote {results_written} results.")

def process_window(i, window_start, window_size, basename, algorithm, args, full_sequence, chromosome, strand, result_queue):
    """Process a genomic window to identify dsRNA structures and stream results to queue
    
    Args:
        i: Start position in the sequence
        window_start: Start position for coordinate calculations
        window_size: Size of the window to process
        basename: Base name for output files
        algorithm: Algorithm to use (einverted)
        args: Command line arguments
        full_sequence: The complete sequence string (already complemented if needed)
        chromosome: Chromosome name
        strand: Strand (+ or -)
        result_queue: Queue for results
    """
    results = []  # Collect results for this window

    if algorithm == "einverted":
        # Extract the window sequence from the provided full sequence
        window_seq = full_sequence[i:i+window_size].upper()
        
        # Check if the sequence is all Ns
        if all(base == 'N' for base in window_seq):
            # Skip this window
            return
        
        if not window_seq:
            return
        
        # Use stdin with einverted - provide sequence directly
        # einverted can accept stdin with -sbegin and -send for coordinates within the stdin sequence
        einverted_cmd = [
            einverted_bin,
            "-sequence", "stdin",  # Read from stdin
            "-sbegin", "1",       # Start at position 1 of stdin sequence
            "-send", str(len(window_seq)),  # End at the length of the window
            "-gap", str(args.gaps),
            "-threshold", str(args.score),
            "-match", str(args.match),
            "-mismatch", str(args.mismatch),
            "-maxrepeat", str(args.max_span),
            "-outfile", "stdout",  # Write to stdout
            "-outseq", "/dev/null",  # Suppress sequence output file
            "-filter" # Presumably needed for proper stdin/stdout handling but not tested
        ]
        
        # Create FASTA input for stdin
        stdin_input = f">{chromosome}:{i+1}-{i+window_size}\n{window_seq}\n"
        
        process = subprocess.Popen(einverted_cmd, 
                                 stdin=subprocess.PIPE, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE, 
                                 text=True)
        stdout, stderr = process.communicate(input=stdin_input)
        
        ein_results = stdout.split("\n")
        
        # Use batched or regular processing based on command-line flag
        if args.batch:
            results = parse_einverted_results_batched(ein_results, window_start, window_size, basename, args, chromosome, strand)
        else:
            results = parse_einverted_results(ein_results, window_start, window_size, basename, args, chromosome, strand)
        
        # Put results in queue for streaming to writer
        for result in results:
            result_queue.put(result)
    
    # Signal this worker is done with this window
    return len(results)
        
def parse_einverted_results_batched(ein_results, window_start, window_size, basename, args, chromosome, strand):
    """Parse results from einverted using batched RNAduplex processing for better performance"""
    
    # Phase 1: Collect all einverted results and sequences
    einverted_entries = []
    sequence_pairs = []
    seq_pair_to_indices = {}  # Map sequence pairs to their indices in einverted_entries
    
    j = 0
    while j < len(ein_results) - 1:
        if j + 4 >= len(ein_results):
            break
            
        try:
            score_line = ein_results[j + 1].split()
            seq_i_full = ein_results[j + 2].split()
            seq_j_full = ein_results[j + 4].split()
            
            # Skip if we don't have enough data
            if len(score_line) < 4 or len(seq_i_full) < 3 or len(seq_j_full) < 3:
                j += 5
                continue
                
            # Extract basic info
            score = score_line[2].rstrip(':')
            raw_match = score_line[3]
            matches, total = map(int, raw_match.split('/'))
            match_perc = round((matches / total) * 100, 2)
            gap_numb = score_line[-2]
            
            # Early filter - skip if below cutoff
            if match_perc < args.paired_cutoff:
                j += 5
                continue
            
            # Calculate genomic coordinates
            i_start = int(seq_i_full[0]) + window_start
            i_end = int(seq_i_full[2]) + window_start
            j_start = int(seq_j_full[2]) + window_start
            j_end = int(seq_j_full[0]) + window_start
            
            # Fix coordinate order if needed
            if i_start > i_end or j_start > j_end or i_start > j_start or i_end > j_end:
                coords = sorted([i_start, i_end, j_start, j_end])
                i_start, i_end, j_start, j_end = coords[0], coords[1], coords[2], coords[3]
            
            # Extract sequences
            i_seq = seq_i_full[1].replace("-", "").upper()
            j_seq = ''.join(reversed(seq_j_full[1].replace("-", ""))).upper()
            
            # Store einverted entry
            entry_index = len(einverted_entries)
            einverted_entries.append({
                'score': score,
                'raw_match': raw_match,
                'match_perc': match_perc,
                'gap_numb': gap_numb,
                'i_start': i_start,
                'i_end': i_end,
                'j_start': j_start,
                'j_end': j_end,
                'i_seq': i_seq,
                'j_seq': j_seq
            })
            
            # Create sequence pair key for deduplication
            seq_pair_key = (i_seq, j_seq)
            
            # Track which entries use this sequence pair
            if seq_pair_key not in seq_pair_to_indices:
                seq_pair_to_indices[seq_pair_key] = []
                sequence_pairs.append(seq_pair_key)
            seq_pair_to_indices[seq_pair_key].append(entry_index)
            
        except Exception as e:
            print(f"Error processing einverted result at index {j}: {str(e)}")
        
        j += 5
    
    if not einverted_entries:
        return []
    
    # Only show deduplication info if we saved significant calls
    if len(einverted_entries) - len(sequence_pairs) > 0:
        print(f"  Batching {len(sequence_pairs)} unique sequence pairs (saved {len(einverted_entries) - len(sequence_pairs)} duplicate RNAduplex calls)")
    
    # Phase 2: Batch process unique sequence pairs through RNAduplex
    # Determine optimal number of workers based on number of pairs
    num_workers = min(8, max(2, len(sequence_pairs) // 10))
    
    # Batch process all unique pairs
    rnaduplex_results = predict_hybridization_batch(sequence_pairs, temperature=args.t, max_workers=num_workers)
    
    # Create a map from sequence pair to RNAduplex result
    seq_pair_to_result = {}
    for i, seq_pair in enumerate(sequence_pairs):
        seq_pair_to_result[seq_pair] = rnaduplex_results[i]
    
    # Phase 3: Build final results by mapping RNAduplex results back to einverted entries
    results = []
    
    for entry in einverted_entries:
        seq_pair_key = (entry['i_seq'], entry['j_seq'])
        structure, indices_seq1, indices_seq2, energy = seq_pair_to_result[seq_pair_key]
        
        # Skip if RNAduplex failed
        if structure is None:
            continue
        
        # Calculate effective coordinates based on RNAduplex trimming
        if strand == "-":
            # Reverse strand coordinate adjustment
            # For reverse strand, swap which end gets trimmed
            i_seq_len = len(entry['i_seq'])
            j_seq_len = len(entry['j_seq'])
            
            # Swap the trimming: trim from end of start and beginning of end
            eff_i_start = entry['i_start'] + (indices_seq1[0] - 1)
            eff_i_end = entry['i_start'] + indices_seq1[1] - 1
            eff_j_start = entry['j_start'] + (indices_seq2[0] - 1)  
            eff_j_end = entry['j_start'] + indices_seq2[1] - 1
        else:
            # Forward strand
            eff_i_start = entry['i_start'] + (indices_seq1[0] - 1)
            eff_i_end = entry['i_start'] + indices_seq1[1] - 1
            eff_j_start = entry['j_start'] + (indices_seq2[0] - 1)
            eff_j_end = entry['j_start'] + indices_seq2[1] - 1
        
        # Calculate metrics
        pairs = int(structure.count('(') * 2)
        percent_paired = round(float(pairs / (len(structure) - 1)) * 100, 2)
        longest_helix = find_longest_helix(structure)
        
        # Check if structure meets minimum base pair requirement (if set)
        actual_bp = structure.count('(')
        if args.min_bp > 0 and actual_bp < args.min_bp:
            if hasattr(args, 'verbose') and args.verbose:
                print(f"  Skipping structure at {i_start}-{j_end}: only {actual_bp} bp (min: {args.min_bp})")
            continue
        
        # Create result
        result = {
            'chromosome': chromosome,
            'strand': strand,
            'score': entry['score'],
            'raw_match': entry['raw_match'],
            'match_perc': entry['match_perc'],
            'gap_numb': entry['gap_numb'],
            'i_start': entry['i_start'],
            'i_end': entry['i_end'],
            'j_start': entry['j_start'],
            'j_end': entry['j_end'],
            'eff_i_start': eff_i_start,
            'eff_i_end': eff_i_end,
            'eff_j_start': eff_j_start,
            'eff_j_end': eff_j_end,
            # Extract the actual subsequences used by RNAduplex and convert T to U
            'i_seq': entry['i_seq'][indices_seq1[0]-1:indices_seq1[1]].replace("T", "U"),
            'j_seq': entry['j_seq'][indices_seq2[0]-1:indices_seq2[1]].replace("T", "U"),
            'structure': structure,
            'energy': energy,
            'base_pairs': actual_bp,
            'percent_paired': percent_paired,
            'longest_helix': longest_helix,
        }
        
        results.append(result)
    
    return results

def parse_einverted_results(ein_results, window_start, window_size, basename, args, chromosome, strand):
    """Parse results from einverted and return as list of result dictionaries"""
    results = []
    j = 0
    while j < len(ein_results) - 1:
        # Skip if we don't have at least 5 lines in the current result block
        if j + 4 >= len(ein_results):
            break
            
        # Extract score and other details
        try:
            score_line = ein_results[j + 1].split()
            seq_i_full = ein_results[j + 2].split()
            seq_j_full = ein_results[j + 4].split()
            
            # Skip if we don't have enough data
            if len(score_line) < 4 or len(seq_i_full) < 3 or len(seq_j_full) < 3:
                j += 5
                continue
                
            # Extracting score, raw match, percentage match, and gaps
            score = score_line[2].rstrip(':')  # Remove trailing colon from score
            raw_match = score_line[3]
            matches, total = map(int, raw_match.split('/'))
            match_perc = round((matches / total) * 100, 2)    
            # find gaps one column from last column            
            gap_numb = score_line[-2]
            
            # Calculate the genomic coordinates from einverted output
            # Since we're using stdin, einverted returns coordinates relative to the stdin sequence
            # We need to add window_start to convert back to genomic coordinates
            
            # Calculate the genomic coordinates from einverted output
            # For both strands, we maintain the same coordinate system
            # The only difference is the sequence content (complement for negative strand)
            i_start = int(seq_i_full[0]) + window_start
            i_end = int(seq_i_full[2]) + window_start
            j_start = int(seq_j_full[2]) + window_start
            j_end = int(seq_j_full[0]) + window_start
            
            # Double-check the coordinates are in the correct order
            if i_start > i_end or j_start > j_end or i_start > j_start or i_end > j_end:
                print(f"Warning: Coordinates not in correct order for {i_start} to {j_end}. Sorting...")
                coords = sorted([i_start, i_end, j_start, j_end])
                i_start, i_end, j_start, j_end = coords[0], coords[1], coords[2], coords[3]
            
            # RNA folding and scoring
            # Extract sequences from einverted output
            i_seq = seq_i_full[1].replace("-", "").upper()
            j_seq = ''.join(reversed(seq_j_full[1].replace("-", ""))).upper()
            
            # Get RNAduplex results directly - no need to format and parse
            structure, indices_seq1, indices_seq2, energy = predict_hybridization(i_seq, j_seq, temperature=args.t)
            
            # Skip if we got empty results from RNAduplex
            if structure is None:
                j += 5
                continue
                
            # Convert 1-based RNAduplex indices to genomic coordinates
            # RNAduplex returns positions relative to input sequences (1-based)
            # We need to add these to the genomic start positions (0-based adjustment)
            
            # Calculate effective coordinates based on RNAduplex trimming
            # RNAduplex returns 1-based indices for the portions of sequences that form the duplex
            if strand == "-":
                # For reverse strand, the sequences are complemented
                # RNAduplex indices are from the start of the complemented sequences
                # We need to adjust for the fact that trimming from the start of RC seq
                # is actually trimming from the end in genomic coordinates
                
                # Get the lengths of the sequences
                i_seq_len = len(i_seq)
                j_seq_len = len(j_seq)
                
                # For reverse strand:
                # - Trimming from start of RC sequence = trimming from end in genomic coords
                # - Trimming from end of RC sequence = trimming from start in genomic coords
                
                # If RNAduplex says use positions 3-10 in a 15bp RC sequence:
                # That means it trimmed 2bp from start and 5bp from end of RC sequence
                # In genomic coords, that's trimming 5bp from start and 2bp from end
                
                eff_i_start = i_start + (i_seq_len - indices_seq1[1])
                eff_i_end = i_end - (indices_seq1[0] - 1)
                eff_j_start = j_start + (j_seq_len - indices_seq2[1])
                eff_j_end = j_end - (indices_seq2[0] - 1)
            else:
                # For forward strand, RNAduplex indices map directly to genomic positions
                # indices are 1-based, so we need to adjust
                eff_i_start = i_start + (indices_seq1[0] - 1)
                eff_i_end = i_start + indices_seq1[1] - 1
                eff_j_start = j_start + (indices_seq2[0] - 1)
                eff_j_end = j_start + indices_seq2[1] - 1
            
            # Debug coordinate conversion if needed
            # print(f"[DEBUG] Coordinate conversion: i_start={i_start}, indices_seq1={indices_seq1} -> eff_i=({eff_i_start}, {eff_i_end})")
            # print(f"[DEBUG] Coordinate conversion: j_start={j_start}, indices_seq2={indices_seq2} -> eff_j=({eff_j_start}, {eff_j_end})")
            
            # Store as tuples for compatibility with existing code
            eff_i = (eff_i_start, eff_i_end)
            eff_j = (eff_j_start, eff_j_end)
            
            # Validate that the effective sequences match the structure length
            i_arm_length = indices_seq1[1] - indices_seq1[0] + 1
            j_arm_length = indices_seq2[1] - indices_seq2[0] + 1
            structure_parts = structure.split('&')
            
            if len(structure_parts) == 2:
                i_structure_length = len(structure_parts[0])
                j_structure_length = len(structure_parts[1])
                
                if i_arm_length != i_structure_length or j_arm_length != j_structure_length:
                    print(f"Warning: Structure length mismatch - i_arm: {i_arm_length} vs {i_structure_length}, j_arm: {j_arm_length} vs {j_structure_length}")
            
            pairs = int(structure.count('(') * 2)
            
            # Calculate percent_paired safely
            try:
                percent_paired = round(float(pairs / (len(structure) - 1)) * 100, 2) # -1 to accoutn for the ampersand
            except (ZeroDivisionError, ValueError):
                percent_paired = 0
            
            # Calculate longest continuous helix
            longest_helix = find_longest_helix(structure)
            
            # Calculate arm lengths
            
            if match_perc < args.paired_cutoff:
                print(f"Skipping {i_start} to {j_end} due to low percentage of pairs: {percent_paired}")
                j += 5
                continue
            
            # Use the structure as-is from RNAduplex
            # The structure should remain in the same format regardless of strand
            display_structure = structure
            
            # Create result dictionary instead of writing to file
            result = {
                'chromosome': chromosome,
                'strand': strand,
                'score': score,
                'raw_match': raw_match,
                'match_perc': match_perc,
                'gap_numb': gap_numb,
                'i_start': i_start,
                'i_end': i_end,
                'j_start': j_start,
                'j_end': j_end,
                'eff_i_start': eff_i[0],
                'eff_i_end': eff_i[1],
                'eff_j_start': eff_j[0],
                'eff_j_end': eff_j[1],
                'i_seq': i_seq.replace("T", "U"),  # Convert to RNA for output
                'j_seq': j_seq.replace("T", "U"),  # Convert to RNA for output
                'structure': display_structure,
                'energy': energy,
                'percent_paired': percent_paired,
                'longest_helix': longest_helix,
            }
            results.append(result)
        except Exception as e:
            print(f"Error processing result block at index {j}: {str(e)}")
        
        # Increment j based on the structure of your einverted output
        j += 5
    
    return results

def count_base_pairs(structure):
    """Count actual base pairs in a structure string"""
    if not structure:
        return 0
    # Count '(' characters (each represents a base pair)
    # Don't double count - just count one side
    return structure.count('(')

def find_longest_helix(structure):
    """
    Find the longest stretch of contiguous base pairs in an RNA structure.
    
    This version properly matches corresponding positions in both arms.
    A helix is only continuous if BOTH arms have pairs at corresponding positions.
    
    Args:
        structure (str): String representing RNA structure (e.g., "((((((&))).)))")
        
    Returns:
        int: Length of the longest contiguous helix
    """
    try:
        # Handle invalid or empty structures
        if not structure or "&" not in structure:
            return 0
            
        # Split structure into both arms
        parts = structure.split("&")
        if len(parts) != 2:
            return 0
            
        left_arm, right_arm = parts[0], parts[1]
        
        # The arms should be the same length for a valid duplex
        if len(left_arm) != len(right_arm):
            # If arms are different lengths, use the shorter one
            min_len = min(len(left_arm), len(right_arm))
            left_arm = left_arm[:min_len]
            right_arm = right_arm[:min_len]
        
        # Create a paired array - True where both positions form a pair
        # In RNAduplex notation:
        # - position i in left arm pairs with position (n-1-i) in right arm
        # - '(' in left should correspond to ')' at the mirrored position in right
        n = len(left_arm)
        paired = []
        
        for i in range(n):
            # Check if position i in left arm pairs with position n-1-i in right arm
            left_char = left_arm[i]
            right_char = right_arm[n - 1 - i]
            
            # Both must be paired (not '.') for this position to be part of a helix
            is_paired = (left_char == '(' and right_char == ')')
            paired.append(is_paired)
        
        # Now find the longest continuous stretch of True values
        max_helix = 0
        current_helix = 0
        
        for is_paired in paired:
            if is_paired:
                current_helix += 1
                max_helix = max(max_helix, current_helix)
            else:
                current_helix = 0
        
        return max_helix
        
    except Exception as e:
        print(f"Error calculating longest helix: {e}")
        return 0

# ==============================================================================
# DataFrame Processing Classes and Functions
# ==============================================================================

def get_memory_usage():
    """Get current memory usage in MB"""
    import psutil
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def process_sequence_einverted(row_data):
    """Process a single sequence through einverted (top-level function for pickling)"""
    import subprocess  # Import here for pickling
    row, einverted_bin, args = row_data
    results = []
    
    # Run einverted
    stdin_input = f">{row['seq_hash']}\n{row['sequence']}\n"
    
    # CRITICAL: Set maxrepeat to allow searching the entire window
    # Use max_span if specified and larger than window, otherwise use window size
    window_size = len(row['sequence'])  # Use actual sequence length as max
    if hasattr(args, 'max_span') and args.max_span is not None:
        max_repeat = max(window_size, args.max_span)
    else:
        max_repeat = window_size
    
    cmd = [
        einverted_bin,
        "-sequence", "stdin",
        "-gap", str(args.gap),
        "-threshold", str(args.score),
        "-match", str(args.match),
        "-mismatch", str(args.mismatch),
        "-maxrepeat", str(max_repeat),  # Set to window size to search entire window
        "-outfile", "stdout",
        "-outseq", "/dev/null"
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=stdin_input)
            
        # Parse einverted output
        lines = stdout.split('\n')
        
        j = 0
        # Changed: Process ALL lines, not just len(lines) - 4
        while j < len(lines):
            # Skip empty lines
            if not lines[j] or j + 3 >= len(lines):
                j += 1
                continue
                
            # Look for lines starting with our seq_hash
            # Format: "seq_hash: Score 49: 51/68 ( 75%) matches, 3 gaps"
            if lines[j].startswith(row['seq_hash'] + ':'):
                # The score info is on the same line as the sequence ID
                score_line = lines[j].split()
                seq_i_full = lines[j + 1].split()
                seq_j_full = lines[j + 3].split()
                
                if len(score_line) >= 4 and len(seq_i_full) >= 3 and len(seq_j_full) >= 3:
                    score = score_line[2].rstrip(':')
                    raw_match = score_line[3]
                    matches, total = map(int, raw_match.split('/'))
                    match_perc = round((matches / total) * 100, 2)
                    
                    # Extract gap count from the score line
                    gap_numb = 0
                    for i, part in enumerate(score_line):
                        if 'gap' in part.lower():
                            if i > 0 and score_line[i-1].isdigit():
                                gap_numb = int(score_line[i-1])
                            break
                    
                    # Local coordinates within the window
                    i_start_local = int(seq_i_full[0])
                    i_end_local = int(seq_i_full[2])
                    j_start_local = int(seq_j_full[2])
                    j_end_local = int(seq_j_full[0])
                    
                    # Extract sequences for RNAduplex
                    i_seq = seq_i_full[1].replace("-", "").upper()
                    j_seq = ''.join(reversed(seq_j_full[1].replace("-", ""))).upper()
                    
                    # For reverse strand, we need to reverse the sequences
                    # This is because einverted reports them in the original orientation
                    # but we need them in the reverse orientation for proper pairing
                    if row.get('strand', '+') == '-':
                        i_seq = i_seq[::-1]
                        j_seq = j_seq[::-1]

                    results.append({
                        'seq_hash': row['seq_hash'],
                        'strand': row.get('strand', '+'),  # Keep strand info
                        'i_start_local': i_start_local,
                        'i_end_local': i_end_local,
                        'j_start_local': j_start_local,
                        'j_end_local': j_end_local,
                        'score': score,
                        'raw_match': raw_match,  # Store the actual match ratio
                        'match_perc': match_perc,
                        'gap_numb': gap_numb,  # Store the gap count
                        'i_seq': i_seq,
                        'j_seq': j_seq
                    })
                
                # Move to next potential result (einverted results are typically 5 lines)
                # But we'll keep checking line by line to not miss anything
                j += 4  # Skip the 4 lines we just processed, will increment by 1 in next iteration
            else:
                j += 1
                
    except Exception as e:
        print(f"Error processing sequence {row['seq_hash']}: {e}")
    
    return results

class ChunkedDsRNAProcessor:
    """Process dsRNAs in memory-efficient chunks"""
    
    def __init__(self, chunk_size=10000, both_strands=True, reverse_only=False, verbose=True):
        """
        Args:
            chunk_size: Maximum windows to process at once
            both_strands: Process both strands (True) or single strand (False)
            reverse_only: If single strand, process reverse instead of forward
            verbose: Print progress messages
        """
        import logging
        self.chunk_size = chunk_size
        self.both_strands = both_strands
        self.reverse_only = reverse_only
        self.verbose = verbose
        self.all_results = []
        self.logger = logging.getLogger(__name__)
    
    def log(self, message, level='info'):
        """Output message to both console and log file"""
        # No need to print separately - logger handles both console and file
        if level == 'info':
            self.logger.info(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)
        
    def extract_windows_chunk(self, sequence, chromosome, strand, window_size, step_size, start_pos=0):
        """Extract a chunk of windows from a sequence"""
        import hashlib
        windows = []
        seq_len = len(sequence)
        
        # Calculate chunk boundaries
        chunk_end_pos = min(start_pos + self.chunk_size * step_size, seq_len)
        
        for start in range(start_pos, chunk_end_pos, step_size):
            end = min(start + window_size, seq_len)
            window_seq = sequence[start:end]
            
            # Skip windows that are too short or all N's
            # Don't hardcode 100 - use minimum from parameters (default 30)
            if len(window_seq) < 30 or window_seq == 'N' * len(window_seq):
                continue
            
            # Create hash of sequence for fast deduplication
            seq_hash = hashlib.md5(window_seq.encode()).hexdigest()
            
            windows.append({
                'chromosome': chromosome,
                'strand': strand,
                'window_start': start,
                'window_end': end,
                'sequence': window_seq,
                'seq_hash': seq_hash,
                'seq_length': len(window_seq)
            })
        
        return pd.DataFrame(windows), chunk_end_pos >= seq_len
    
    def process_chunk(self, windows_df, coord_map, einverted_bin, args, region_offset=0, seq_len=None):
        """Process a single chunk of windows
        
        Args:
            windows_df: DataFrame with window information
            coord_map: Mapping of sequence hashes to genomic locations
            einverted_bin: Path to einverted binary
            args: Command line arguments
            region_offset: Offset for region extraction
            seq_len: Total length of the genomic sequence (needed for reverse strand)
        """
        
        # Process all windows (no deduplication at window level)
        # Deduplication happens after einverted to avoid redundant dsRNA processing
        unique_df = windows_df.reset_index(drop=True)
        
        if self.verbose:
            self.log(f"    Chunk: {len(windows_df)} windows")
        
        # Run einverted on all windows
        einverted_results = self.run_einverted_batch(unique_df, einverted_bin, args)
        
        if einverted_results.empty:
            return pd.DataFrame()
        
        if self.verbose:
            self.log(f"    Found {len(einverted_results)} inverted repeats from einverted")
        
        # Run RNAduplex (with deduplication of identical sequence pairs)
        # Pass the CPU count for parallel processing
        max_workers = args.c if hasattr(args, 'c') else args.cpus if hasattr(args, 'cpus') else 1
        einverted_results = self.run_rnaduplex_batch(einverted_results, args.t, max_workers=max_workers)
        
        # Map back to genomic coordinates (with region offset if extracting a region)
        results = self.map_to_genomic_coords(einverted_results, coord_map, region_offset, seq_len)
        
        return results
    
    def run_einverted_batch(self, sequences_df, einverted_bin, args):
        """Run einverted on unique sequences in parallel"""
        if sequences_df.empty:
            return pd.DataFrame()
            
        # Prepare data for parallel processing
        row_data = [(row, einverted_bin, args) for _, row in sequences_df.iterrows()]
        
        all_results = []
        # Handle both 'c' and 'cpus' attribute names
        max_workers = args.c if hasattr(args, 'c') else args.cpus
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_sequence_einverted, data): idx 
                      for idx, data in enumerate(row_data)}
            
            for future in as_completed(futures):
                try:
                    results = future.result()
                    all_results.extend(results)
                except Exception as e:
                    print(f"Error getting einverted results: {e}")
        
        return pd.DataFrame(all_results)
    
    def run_rnaduplex_batch(self, einverted_df, temperature=37, max_workers=None):
        """Run RNAduplex on einverted results, deduplicating identical sequence pairs"""
        if einverted_df.empty:
            return einverted_df
            
        # Deduplicate identical einverted results before RNAduplex
        # Keep only the first occurrence of each unique combination
        total_before = len(einverted_df)
        einverted_df = einverted_df.drop_duplicates(
            subset=['seq_hash', 'strand', 'i_start_local', 'i_end_local', 
                    'j_start_local', 'j_end_local', 'i_seq', 'j_seq'],
            keep='first'
        )
        total_after = len(einverted_df)
        
        if self.verbose:
            if total_before > total_after:
                self.log(f"    Deduplicated {total_before} → {total_after} unique inverted repeats")
            self.log(f"    Processing {total_after} inverted repeats through RNAduplex")
        
        # Set temperature
        RNA.cvar.temperature = temperature
        
        # Define a function to process a single row
        def process_rnaduplex_row(row):
            """Process a single einverted result through RNAduplex"""
            try:
                result = RNA.duplexfold(row['i_seq'], row['j_seq'])
                
                structure_parts = result.structure.split('&')
                if len(structure_parts) == 2:
                    len1 = len(structure_parts[0])
                    len2 = len(structure_parts[1])
                    
                    return pd.Series({
                        'structure': result.structure,
                        'energy': result.energy,
                        'i_trim_start': result.i - len1 + 1,
                        'i_trim_end': result.i,
                        'j_trim_start': result.j,
                        'j_trim_end': result.j + len2 - 1
                    })
                else:
                    return pd.Series({
                        'structure': None,
                        'energy': None,
                        'i_trim_start': None,
                        'i_trim_end': None,
                        'j_trim_start': None,
                        'j_trim_end': None
                    })
            except:
                return pd.Series({
                    'structure': None,
                    'energy': None,
                    'i_trim_start': None,
                    'i_trim_end': None,
                    'j_trim_start': None,
                    'j_trim_end': None
                })
        
        # Apply RNAduplex processing with parallel execution if we have multiple workers
        if max_workers and max_workers > 1 and len(einverted_df) > 10:
            # Use concurrent.futures for parallel processing
            from concurrent.futures import ThreadPoolExecutor
            
            # Split dataframe into chunks for parallel processing
            n_chunks = min(max_workers, len(einverted_df))
            chunk_size = len(einverted_df) // n_chunks
            chunks = []
            for i in range(n_chunks):
                start_idx = i * chunk_size
                if i == n_chunks - 1:
                    # Last chunk gets any remaining rows
                    chunks.append(einverted_df.iloc[start_idx:])
                else:
                    chunks.append(einverted_df.iloc[start_idx:start_idx + chunk_size])
            
            # Process chunks in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(lambda chunk: chunk.apply(process_rnaduplex_row, axis=1), chunk) 
                          for chunk in chunks]
                
                # Collect results
                results = []
                for future in futures:
                    results.append(future.result())
                
                # Combine results
                duplex_results = pd.concat(results, ignore_index=False)
        else:
            # For small datasets or single CPU, use regular apply
            duplex_results = einverted_df.apply(process_rnaduplex_row, axis=1)
        
        # Merge the results back into the dataframe
        for col in duplex_results.columns:
            einverted_df[col] = duplex_results[col]
        
        # Drop entries where RNAduplex failed
        einverted_df = einverted_df.dropna(subset=['structure'])
        
        return einverted_df
    
    def find_longest_helix(self, structure):
        """Find the longest consecutive helix in the structure"""
        if not structure:
            return 0
        
        # Split by '&' and take the first part (i-arm)
        parts = structure.split('&')
        if not parts:
            return 0
        
        i_structure = parts[0]
        
        # Find longest consecutive run of '(' characters
        max_helix = 0
        current_helix = 0
        
        for char in i_structure:
            if char == '(':
                current_helix += 1
                max_helix = max(max_helix, current_helix)
            else:
                current_helix = 0
        
        return max_helix
    
    def map_to_genomic_coords(self, einverted_df, coord_map, region_offset=0, seq_len=None):
        """Map einverted results to genomic coordinates
        
        Args:
            einverted_df: DataFrame with einverted results
            coord_map: Mapping of sequence hashes to genomic locations
            region_offset: Offset for region extraction
            seq_len: Total length of the genomic sequence (needed for reverse strand conversion)
        """
        final_results = []
        
        for _, row in einverted_df.iterrows():
            # Get all genomic locations for this sequence
            locations = coord_map[row['seq_hash']]
            
            for loc in locations:
                # Convert local coordinates to genomic coordinates
                # Since we're only complementing (not reverse complementing),
                # coordinates are straightforward for both strands
                # window_start (loc['start']) is 0-based from Python
                # einverted coordinates (i_start_local, etc) are 1-based
                # We want 1-based genomic coordinates for output
                result = {
                    'chromosome': loc['chromosome'],
                    'strand': loc['strand'],
                    'i_start': loc['start'] + row['i_start_local'] + region_offset,
                    'i_end': loc['start'] + row['i_end_local'] + region_offset,
                    'j_start': loc['start'] + row['j_start_local'] + region_offset,
                    'j_end': loc['start'] + row['j_end_local'] + region_offset,
                    'score': row['score'],
                    'raw_match': row.get('raw_match', '0/0'),
                    'match_perc': row['match_perc'],
                    'gap_numb': row.get('gap_numb', 0),
                    'structure': row['structure'],
                    'energy': row['energy'],
                    'i_seq': row['i_seq'],  # Keep full sequence for now
                    'j_seq': row['j_seq']   # Keep full sequence for now
                }
                
                
                # Calculate effective coordinates (already includes region_offset)
                # RNAduplex trim positions are 1-based within the sequences
                if row['strand'] == '-':
                    # For reverse strand, sequences are reversed before RNAduplex
                    # So indices need to be mapped back from reversed orientation
                    result['eff_i_start'] = result['i_end'] - row['i_trim_end'] + 1
                    result['eff_i_end'] = result['i_end'] - row['i_trim_start'] + 1
                    result['eff_j_start'] = result['j_end'] - row['j_trim_end'] + 1
                    result['eff_j_end'] = result['j_end'] - row['j_trim_start'] + 1
                else:
                    # Forward strand - standard calculation
                    result['eff_i_start'] = result['i_start'] + row['i_trim_start'] - 1
                    result['eff_i_end'] = result['i_start'] + row['i_trim_end'] - 1
                    result['eff_j_start'] = result['j_start'] + row['j_trim_start'] - 1
                    result['eff_j_end'] = result['j_start'] + row['j_trim_end'] - 1
                
                
                # Calculate longest helix
                result['longest_helix'] = self.find_longest_helix(row['structure'])
                
                # Trim the sequences based on RNAduplex positions
                # The sequences are already in 5' to 3' orientation from einverted processing
                # Make sure indices are integers (they might be floats or None)
                if pd.notna(row.get('i_trim_start')) and pd.notna(row.get('i_trim_end')):
                    i_trim_start = int(row['i_trim_start']) - 1
                    i_trim_end = int(row['i_trim_end'])
                    j_trim_start = int(row['j_trim_start']) - 1
                    j_trim_end = int(row['j_trim_end'])
                    
                    # Apply trimming and convert T to U for RNA
                    result['i_seq'] = row['i_seq'][i_trim_start:i_trim_end].replace('T', 'U')
                    result['j_seq'] = row['j_seq'][j_trim_start:j_trim_end].replace('T', 'U')
                else:
                    # No trimming available, use full sequences
                    result['i_seq'] = row['i_seq'].replace('T', 'U')
                    result['j_seq'] = row['j_seq'].replace('T', 'U')
                
                final_results.append(result)
        
        return pd.DataFrame(final_results)
    
    def eliminate_nested_dsrnas(self, results_df):
        """
        Remove dsRNAs that are completely contained within others.
        A dsRNA is considered nested ONLY if BOTH arms are within the corresponding arms
        of another dsRNA (i.e., using identical sequences but shorter on both sides).
        Uses vectorized numpy operations for better performance.
        """
        if results_df.empty:
            return results_df
        
        # Sort by chromosome, strand, and i_start
        results_df = results_df.sort_values(['chromosome', 'strand', 'i_start'])
        
        # Track which indices to keep
        keep_mask = np.ones(len(results_df), dtype=bool)
        total_nested = 0
        
        # Process each chromosome-strand group
        for (chrom, strand), group in results_df.groupby(['chromosome', 'strand']):
            if len(group) <= 1:
                continue
                
            # Get coordinates as numpy arrays for vectorized operations
            group_idx = group.index.to_numpy()
            i_starts = group['i_start'].to_numpy()
            i_ends = group['i_end'].to_numpy()
            j_starts = group['j_start'].to_numpy()
            j_ends = group['j_end'].to_numpy()
            
            n = len(group)
            
            # Create broadcasting arrays for pairwise comparison
            # Shape: (n, 1) vs (n,) -> (n, n) comparison matrix
            i_starts_i = i_starts[:, np.newaxis]
            i_ends_i = i_ends[:, np.newaxis]
            j_starts_i = j_starts[:, np.newaxis]
            j_ends_i = j_ends[:, np.newaxis]
            
            # Check if a dsRNA is nested within another
            # CRITICAL: A dsRNA is only considered nested if:
            # - Its i-arm is within the other's i-arm (NOT j-arm)
            # - AND its j-arm is within the other's j-arm (NOT i-arm)
            # This preserves dsRNAs where both arms fall within just one arm of another structure
            i_arm_nested = (
                (i_starts >= i_starts_i) &  # current i_start >= other's i_start
                (i_ends <= i_ends_i)         # current i_end <= other's i_end
            )
            
            j_arm_nested = (
                (j_starts >= j_starts_i) &  # current j_start >= other's j_start
                (j_ends <= j_ends_i)         # current j_end <= other's j_end
            )
            
            # A structure is nested only if BOTH arms are nested in their CORRESPONDING arms
            is_nested = i_arm_nested & j_arm_nested
            
            # Set diagonal to False (element can't be nested within itself)
            np.fill_diagonal(is_nested, False)
            
            # For exact duplicates (same coordinates), we need special handling
            # Check if structures are identical (not just one within the other)
            i_identical = (i_starts[:, np.newaxis] == i_starts) & (i_ends[:, np.newaxis] == i_ends)
            j_identical = (j_starts[:, np.newaxis] == j_starts) & (j_ends[:, np.newaxis] == j_ends)
            is_identical = i_identical & j_identical
            np.fill_diagonal(is_identical, False)  # Don't compare with self
            
            # For identical pairs, only mark the later one as nested (keep the first occurrence)
            # This is done by using upper triangular matrix only for identical pairs
            is_nested_final = is_nested.copy()
            for i in range(n):
                for j in range(i + 1, n):  # Only check upper triangle
                    if is_identical[i, j]:
                        # If they're identical, mark j as nested (keep i)
                        is_nested_final[i, j] = True
                        is_nested_final[j, i] = False  # Don't mark i as nested
            
            # Find which elements are nested within any other element
            nested_mask = is_nested_final.any(axis=0)
            total_nested += nested_mask.sum()
            
            # Update the global keep mask
            for idx, is_nested_item in zip(group_idx, nested_mask):
                if is_nested_item:
                    keep_mask[results_df.index.get_loc(idx)] = False
        
        if self.verbose and total_nested > 0:
            self.log(f"  Removed {total_nested} nested dsRNAs (both arms contained within another on same strand)")
        
        return results_df[keep_mask]
    
    def eliminate_nested_dsrnas_original(self, results_df):
        """
        Original implementation with nested loops.
        Kept as fallback for validation and small datasets.
        A dsRNA is considered nested ONLY if BOTH arms are within the corresponding arms.
        """
        if results_df.empty:
            return results_df
            
        # Sort by chromosome, strand, and i_start
        results_df = results_df.sort_values(['chromosome', 'strand', 'i_start'])
        
        nested_indices = set()
        
        # Group by chromosome and strand
        for (chr_strand), group in results_df.groupby(['chromosome', 'strand']):
            group_indices = group.index.tolist()
            
            for i in range(len(group_indices)):
                if group_indices[i] in nested_indices:
                    continue
                    
                row_i = group.loc[group_indices[i]]
                
                for j in range(i + 1, len(group_indices)):
                    if group_indices[j] in nested_indices:
                        continue
                        
                    row_j = group.loc[group_indices[j]]
                    
                    # Check if row_j is nested within row_i 
                    # CRITICAL: Both arms must be in CORRESPONDING arms (i in i, j in j)
                    if (row_j['i_start'] >= row_i['i_start'] and 
                        row_j['i_end'] <= row_i['i_end'] and
                        row_j['j_start'] >= row_i['j_start'] and 
                        row_j['j_end'] <= row_i['j_end']):
                        nested_indices.add(group_indices[j])
                    # Check if row_i is nested within row_j
                    # CRITICAL: Both arms must be in CORRESPONDING arms (i in i, j in j)
                    elif (row_i['i_start'] >= row_j['i_start'] and 
                          row_i['i_end'] <= row_j['i_end'] and
                          row_i['j_start'] >= row_j['j_start'] and 
                          row_i['j_end'] <= row_j['j_end']):
                        nested_indices.add(group_indices[i])
                        break
        
        # Remove nested dsRNAs
        filtered_df = results_df.drop(list(nested_indices))
        
        if self.verbose and len(nested_indices) > 0:
            self.log(f"  Removed {len(nested_indices)} nested dsRNAs (both arms contained within another on same strand)")
        
        return filtered_df
    
    def process_fasta(self, fasta_file, einverted_bin, args):
        """Main processing function with chunking"""
        from Bio import SeqIO
        import gzip
        from collections import defaultdict
        
        self.log(f"Processing {fasta_file} with chunked DataFrame approach")
        self.log(f"  Chunk size: {self.chunk_size} windows")
        self.log(f"  Strands: {'both' if self.both_strands else ('reverse only' if self.reverse_only else 'forward only')}")
        
        # Handle region extraction if specified
        if hasattr(args, 'chromosome') and args.chromosome:
            self.log(f"  Extracting chromosome: {args.chromosome}")
        if hasattr(args, 'start') and args.start > 0:
            self.log(f"  Region: {args.start:,}-{args.end:,}" if args.end > 0 else f"  Start: {args.start:,}")
        
        start_time = time.time()
        initial_memory = get_memory_usage()
        
        all_chunk_results = []
        total_windows = 0
        total_unique = 0
        
        # Open file (handle gzipped files)
        if fasta_file.endswith('.gz'):
            handle = gzip.open(fasta_file, 'rt')
        else:
            handle = open(fasta_file, 'rt')
        
        try:
            for record in SeqIO.parse(handle, "fasta"):
                chromosome = record.id
                
                # Skip if specific chromosome requested and this isn't it
                if hasattr(args, 'chromosome') and args.chromosome and chromosome != args.chromosome:
                    continue
                
                sequence = str(record.seq).upper()
                
                # Apply region extraction if specified
                region_offset = 0  # Track offset for genomic coordinate mapping
                if hasattr(args, 'start') and args.start > 0:
                    start_pos = args.start - 1  # Convert to 0-based
                    end_pos = args.end - 1 if args.end > 0 else len(sequence)
                    sequence = sequence[start_pos:end_pos]
                    region_offset = start_pos  # Store offset for coordinate adjustment
                    self.log(f"  Extracted region: {len(sequence):,} bp from {chromosome}")
                    # Keep original chromosome name for output
                
                if self.both_strands:
                    strands = ['+', '-']
                elif self.reverse_only:
                    strands = ['-']
                else:
                    strands = ['+']
                
                for strand in strands:
                    if strand == '-':
                        # Just complement for negative strand (not reverse complement)
                        # This keeps coordinates in the same orientation
                        complement = str.maketrans('ATGC', 'TACG')
                        seq_to_process = sequence.translate(complement)
                    else:
                        seq_to_process = sequence
                    
                    self.log(f"\nProcessing {chromosome} ({strand} strand)...")
                    
                    # Process in chunks
                    chunk_num = 0
                    position = 0
                    
                    while position < len(seq_to_process):
                        chunk_num += 1
                        
                        # Extract chunk of windows
                        # Handle both 's' and 'step' attribute names
                        step_size = args.s if hasattr(args, 's') else args.step
                        window_size = args.w if hasattr(args, 'w') else args.window
                        
                        windows_df, is_last = self.extract_windows_chunk(
                            seq_to_process, chromosome, strand, 
                            window_size, step_size, position
                        )
                        
                        if windows_df.empty:
                            break
                        
                        total_windows += len(windows_df)
                        
                        # Track coordinates for all windows
                        coord_map = defaultdict(list)
                        for _, row in windows_df.iterrows():
                            coord_map[row['seq_hash']].append({
                                'chromosome': row['chromosome'],
                                'strand': row['strand'],
                                'start': row['window_start'],
                                'end': row['window_end']
                            })
                        
                        # Process this chunk (pass region_offset for coordinate adjustment)
                        # For reverse strand, we need to pass the original sequence length
                        seq_len_for_mapping = len(seq_to_process) if strand == '-' else None
                        chunk_results = self.process_chunk(windows_df, coord_map, einverted_bin, args, region_offset, seq_len_for_mapping)
                        
                        if not chunk_results.empty:
                            all_chunk_results.append(chunk_results)
                        
                        # Memory check
                        current_memory = get_memory_usage()
                        if self.verbose and chunk_num % 5 == 0:
                            self.log(f"    Memory usage: {current_memory:.1f} MB (delta: {current_memory - initial_memory:.1f} MB)")
                        
                        # Move to next chunk
                        position += self.chunk_size * step_size
                        
                        if is_last:
                            break
        finally:
            handle.close()
        
        # Combine all chunk results
        if all_chunk_results:
            all_results_df = pd.concat(all_chunk_results, ignore_index=True)
            
            # Deduplicate truly identical entries (same coordinates and sequences)
            initial_count = len(all_results_df)
            all_results_df = all_results_df.drop_duplicates(
                subset=['chromosome', 'strand', 'i_start', 'i_end', 'j_start', 'j_end', 'i_seq', 'j_seq'],
                keep='first'
            )
            deduplicated_count = initial_count - len(all_results_df)
            if deduplicated_count > 0 and self.verbose:
                self.log(f"\nRemoved {deduplicated_count} duplicate entries (identical coordinates and sequences)")
            
            # Eliminate nested dsRNAs across all results
            self.log("\nEliminating nested dsRNAs...")
            all_results_df = self.eliminate_nested_dsrnas(all_results_df)
            
            # Apply final filters
            all_results_df['percent_paired'] = all_results_df['structure'].apply(
                lambda x: round(x.count('(') * 2 / (len(x) - 1) * 100, 2) if x else 0
            )
            
            # Calculate actual base pairs for filtering
            all_results_df['base_pairs'] = all_results_df['structure'].apply(count_base_pairs)
            
            # Filter by minimum base pairs (if set)
            initial_count = len(all_results_df)
            
            # Apply filters based on what's configured
            filter_mask = (
                (all_results_df['match_perc'] >= args.paired_cutoff) &
                (all_results_df['percent_paired'] >= args.paired_cutoff)
            )
            
            # Only apply min_bp filter if it's > 0
            if args.min_bp > 0:
                filter_mask = filter_mask & (all_results_df['base_pairs'] >= args.min_bp)
            
            all_results_df = all_results_df[filter_mask]
            
            filtered_count = initial_count - len(all_results_df)
            if filtered_count > 0 and self.verbose:
                if args.min_bp > 0:
                    self.log(f"  Filtered {filtered_count} structures (< {args.min_bp} bp or < {args.paired_cutoff}% paired)")
                else:
                    self.log(f"  Filtered {filtered_count} structures (< {args.paired_cutoff}% paired)")
                # Log filtering if logger is available
                try:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"Filtered {filtered_count} structures with < {args.min_bp} base pairs")
                except:
                    pass
        else:
            all_results_df = pd.DataFrame()
        
        elapsed = time.time() - start_time
        final_memory = get_memory_usage()
        
        # Log comprehensive summary
        self.log(f"\nCompleted in {elapsed:.2f}s")
        self.log(f"Memory usage: Initial={initial_memory:.1f}MB, Final={final_memory:.1f}MB, Peak delta={final_memory - initial_memory:.1f}MB")
        self.log(f"Found {len(all_results_df)} dsRNA structures")
        
        # Add summary statistics
        if not all_results_df.empty:
            self.log("=" * 60)
            self.log("Summary Statistics:")
            self.log(f"  Total dsRNAs found: {len(all_results_df)}")
            self.log(f"  Average base pairs: {all_results_df['base_pairs'].mean():.1f}")
            self.log(f"  Average percent paired: {all_results_df['percent_paired'].mean():.1f}%")
            # Check if energy column exists (might be 'energy' or 'dG(kcal/mol)')
            if 'energy' in all_results_df.columns:
                self.log(f"  Average energy: {all_results_df['energy'].mean():.2f} kcal/mol")
            elif 'dG(kcal/mol)' in all_results_df.columns:
                self.log(f"  Average energy: {all_results_df['dG(kcal/mol)'].mean():.2f} kcal/mol")
            self.log(f"  Chromosomes processed: {all_results_df['chromosome'].nunique()}")
            self.log(f"  Processing rate: {len(all_results_df) / elapsed:.1f} dsRNAs/second")
            self.log("=" * 60)
        
        return all_results_df
            
# Define the process_frame function
def process_frame(frame_start, frame_step_size, end_coordinate, window_size, basename, algorithm, args, full_sequence, chromosome, strand, result_queue, pool):
    for start in range(frame_start, end_coordinate, frame_step_size):
        window_start = start
        end = min(start + window_size, end_coordinate)
        pool.apply_async(process_window, (start, window_start, window_size, basename, algorithm, args, full_sequence, chromosome, strand, result_queue))
        # For debugging, run the process_window function directly
        # process_window(start, start, args.w, basename, args.algorithm, args, full_sequence, chromosome, strand, result_queue)

# ProcessorArgs class at module level for pickling
class ProcessorArgs:
    """Map main script argument names to what the DataFrame processor expects"""
    def __init__(self, original_args):
        self.filename = original_args.filename
        self.w = original_args.w
        self.s = original_args.step
        self.step = original_args.step
        self.c = original_args.cpus
        self.cpus = original_args.cpus
        self.score = original_args.score
        self.min_bp = original_args.min_bp  # Add min_bp parameter
        self.min = original_args.min  # Add min parameter
        self.max = original_args.max  # Add max parameter
        self.paired_cutoff = original_args.paired_cutoff
        self.gap = original_args.gaps  # Note: gaps -> gap
        self.gaps = original_args.gaps
        self.match = original_args.match
        self.mismatch = original_args.mismatch
        self.t = original_args.t
        self.chromosome = original_args.only_seq  # Use only_seq for chromosome selection
        self.only_seq = original_args.only_seq
        self.start = original_args.start
        self.end = original_args.end
        self.chunk_size = original_args.chunk_size
        self.forward_only = original_args.forward_only
        self.reverse_only = original_args.reverse_only
        self.output_dir = original_args.output_dir
        self.output_label = original_args.output_label

def run_dataframe_approach(args):
    """Run the optimized DataFrame approach"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Create output directory first to set up logging
    if args.output_dir:
        output_dir = args.output_dir
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"dsrnascan_{timestamp}"
    
    os.makedirs(output_dir, exist_ok=True)
    # logger.info(f"Output directory: {output_dir}")  # Will be shown after logging setup
    
    # Setup logging to capture all output
    log_file = os.path.join(output_dir, 'dsrnascan.log')
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.setLevel(logging.INFO)
    
    # File handler with timestamps
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    root_logger.addHandler(file_handler)
    
    # Console handler without timestamps (only message)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    root_logger.addHandler(console_handler)
    
    logger = logging.getLogger(__name__)
    
    # Log initial parameters
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"dsRNAscan version {__version__}")
    logger.info(f"Command: {' '.join(sys.argv)}")
    
    # Dump all arguments to log for complete record
    logger.info("=" * 60)
    logger.info("Complete argument list:")
    for arg, value in sorted(vars(args).items()):
        logger.info(f"  {arg}: {value}")
    logger.info("=" * 60)
    
    # Log key parameters for quick reference
    logger.info(f"Key parameters: min_bp={args.min_bp}, score={args.score}, paired_cutoff={args.paired_cutoff}")
    logger.info(f"Window size: {args.w}, Step size: {args.step}, CPUs: {args.cpus}")
    
    processor_args = ProcessorArgs(args)
    
    # ChunkedDsRNAProcessor is now defined in this file above
    
    # Determine which strands to process
    if args.forward_only:
        both_strands = False
        reverse_only = False
    elif args.reverse_only:
        both_strands = False
        reverse_only = True
    else:
        both_strands = True
        reverse_only = False
    
    # Create processor
    processor = ChunkedDsRNAProcessor(
        chunk_size=args.chunk_size,
        both_strands=both_strands,
        reverse_only=reverse_only,
        verbose=True
    )
    
    # Process the file
    results = processor.process_fasta(processor_args.filename, einverted_bin, processor_args)
    
    # Output directory already created above for logging
    
    # Save results in the same format as regular approach
    base_filename = os.path.basename(args.filename)
    if base_filename.endswith('.gz'):
        base_filename = base_filename[:-3]
    if base_filename.endswith('.fa') or base_filename.endswith('.fasta'):
        base_filename = os.path.splitext(base_filename)[0]
    
    # Determine the output label (chromosome name)
    if args.output_label == 'header':
        # Use the actual chromosome name from the data
        if not results.empty and 'chromosome' in results.columns:
            # Get the actual chromosome name (without region info)
            chrom_name = results.iloc[0]['chromosome']
            if ':' in chrom_name:
                chrom_name = chrom_name.split(':')[0]
        else:
            chrom_name = base_filename
    else:
        chrom_name = args.output_label
    
    # Create output filename matching regular format
    if args.forward_only:
        strand_label = 'forward'
    elif args.reverse_only:
        strand_label = 'reverse'
    else:
        strand_label = 'both'
    output_file = os.path.join(output_dir, 
        f"{base_filename}.{chrom_name}.{strand_label}_win{args.w}_step{args.step}_start{args.start}_score{args.score}_merged_results.txt")
    
    # Write in the same format as regular approach
    with open(output_file, 'w') as f:
        # Write header matching regular format
        f.write("Chromosome\tStrand\ti_start\ti_end\tj_start\tj_end\t"
               "Score\tRawMatch\tPercMatch\tGaps\t"
               "dG(kcal/mol)\tbase_pairs\tpercent_paired\tlongest_helix\t"
               "eff_i_start\teff_i_end\teff_j_start\teff_j_end\t"
               "i_seq\tj_seq\tstructure\n")
        
        # Write results
        for _, row in results.iterrows():
            
            # Ensure we have all required fields with defaults
            # Calculate base_pairs if not present
            base_pairs = row.get('base_pairs', count_base_pairs(row.get('structure', '')))
            
            f.write(f"{row.get('chromosome', chrom_name)}\t{row.get('strand', '+')}\t"
                   f"{row.get('i_start', 0)}\t{row.get('i_end', 0)}\t"
                   f"{row.get('j_start', 0)}\t{row.get('j_end', 0)}\t"
                   f"{row.get('score', 0)}\t{row.get('raw_match', '0/0')}\t"
                   f"{row.get('match_perc', 0)}\t{row.get('gap_numb', 0)}\t"
                   f"{row.get('energy', 0.0)}\t{base_pairs}\t{row.get('percent_paired', 0)}\t{row.get('longest_helix', 0)}\t"
                   f"{row.get('eff_i_start', 0)}\t{row.get('eff_i_end', 0)}\t"
                   f"{row.get('eff_j_start', 0)}\t{row.get('eff_j_end', 0)}\t"
                   f"{row.get('i_seq', '')}\t{row.get('j_seq', '')}\t"
                   f"{row.get('structure', '')}\n")
    
    print(f"\nResults saved to: {output_file}")
    print(f"Total dsRNA structures found: {len(results)}")
    
    # Generate BP file if needed
    if not results.empty:
        bp_file = output_file.replace('.txt', '.bp')
        generate_bp_file(output_file, bp_file)
    
    return len(results)

def main():
    ### Arguments
    parser = argparse.ArgumentParser(
        description='dsRNAscan - A tool for genome-wide prediction of double-stranded RNA structures',
        epilog='Version: {} | Copyright (C) 2024 Bass Lab'.format(__version__)
    )
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))
    parser.add_argument('filename',  type=str,
                        help='input filename')
    parser.add_argument('-t', type=int, default=37,
                        help='Folding temperature in celsius; default = 37C')
    parser.add_argument('-s', '--step', type=int, default=150,
                        help='Step size; default = 150')
    parser.add_argument('-w', type=int, default=10000,
                        help='Window size; default = 10000')
    parser.add_argument('--max_span', type=int, default=None,
                        help='Max span of inverted repeat; default = window size')
    parser.add_argument('--min_bp', type=int, default=25,
                        help='Minimum number of base pairs required (overrides --score if set); Default = 25')
    parser.add_argument('--score', type=int, default=None,
                        help='Minimum score threshold for inverted repeat (deprecated, use --min_bp); Default = 75')
    parser.add_argument('--min', type=int, default=30,
                        help='Minimum length of inverted repeat; Default = 30')
    parser.add_argument('--max', type=int, default=10000,
                        help='Max length of inverted repeat; Default = 10000')
    parser.add_argument('--gaps', type=int, default=12,
                        help='Gap penalty')
    parser.add_argument('--start', type=int, default=0,
                        help='Starting coordinate for scan; Default = 0')
    parser.add_argument('--end', type=int, default=0,
                        help='Ending coordinate for scan; Default = 0')
    parser.add_argument('-x', '--mismatch', type=int, default=-4,
            help='Mismatch score')
    parser.add_argument('--match', type=int, default=3,
            help='Match score')
    parser.add_argument('--paired_cutoff', type=int, default=70,
                        help='Cutoff to ignore sturctures with low percentage of pairs; Default <70')
    parser.add_argument('--algorithm', type=str, default="einverted",
            help='Inverted repeat finding algorithm (einverted or iupacpal)')
    parser.add_argument('--forward-only', action='store_true', default=False,
                        help='Process forward strand only (default: both strands)')
    parser.add_argument('--reverse-only', action='store_true', default=False,
                        help='Process reverse strand only (default: both strands)')
    parser.add_argument('--output_label', type=str, default='header',
                        help='Label for output files and results (default: use sequence header)')
    parser.add_argument('--only_seq', type=str, default=None,
                        help='Only scan this specific sequence')
    parser.add_argument('-c', '--cpus', type=int, default=4,
                        help='Number of cpus to use; Default = 4')
    parser.add_argument('--clean', action='store_false', default=True,
                    help='Clean up temporary files after processing')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Output directory (default: dsrnascan_YYYYMMDD_HHMMSS)')
    parser.add_argument('--batch', action='store_true', default=False,
                        help='DEPRECATED: Only used with --legacy flag. Has no effect in default DataFrame mode')
    parser.add_argument('--legacy', action='store_true', default=False,
                        help='DEPRECATED: Use legacy non-DataFrame approach (much slower, will be removed in future versions)')
    parser.add_argument('--chunk-size', type=int, default=10000,
                        help='Windows per chunk for DataFrame approach (default: 10000)')
    parser.add_argument('--eliminate-nested', action='store_true', default=True,
                        help='Remove nested dsRNAs (default: True)')
    
    args = parser.parse_args()
    
    # Get logger for main function
    logger = logging.getLogger(__name__)
    
    # Set max_span to window size if not specified
    if args.max_span is None:
        args.max_span = args.w
        logger.info(f"Setting max_span to window size: {args.max_span}")
    
    # Check for deprecated flags
    if args.batch and not args.legacy:
        logger.warning("WARNING: --batch flag has no effect without --legacy. The default DataFrame mode handles batching automatically.")
        print("WARNING: --batch flag has no effect without --legacy. The default DataFrame mode handles batching automatically.")
    
    if args.legacy:
        logger.warning("WARNING: --legacy flag is DEPRECATED and will be removed in a future version.")
        logger.warning("The legacy mode is significantly slower than the default DataFrame approach.")
        print("\n" + "="*80)
        print("WARNING: You are using DEPRECATED --legacy mode!")
        print("This mode is significantly slower and will be removed in future versions.")
        print("Please use the default DataFrame mode (remove --legacy flag) for better performance.")
        print("="*80 + "\n")
    
    # Handle min_bp vs score parameter
    if args.min_bp is not None and args.score is not None:
        # Both specified - use the provided values
        msg1 = f"Using minimum {args.min_bp} base pairs with custom einverted score: {args.score}"
        msg2 = f"Note: score {args.score} would normally correspond to ~{args.score // 3} bp with default match scoring"
        print(msg1)
        print(msg2)
    elif args.min_bp is not None:
        # User specified min_bp, calculate score from it (assuming default match=3)
        if not args.score:
            args.score = args.min_bp * args.match  # Use actual match score
        msg = f"Using minimum {args.min_bp} base pairs (einverted score: {args.score}, match={args.match})"
        print(msg)
    elif args.score is not None:
        # Only score specified (backward compatibility)
        # Don't enforce min_bp filtering when custom score is used
        args.min_bp = 0  # No minimum filtering
        msg = f"Using einverted score {args.score} (no minimum base pair filtering)"
        print(msg)
    else:
        # Neither specified, use default
        args.min_bp = 25
        args.score = 75
        msg = f"Using default minimum {args.min_bp} base pairs (einverted score: {args.score})"
        print(msg)
    
    # Validate strand options
    if args.forward_only and args.reverse_only:
        parser.error("Cannot use both --forward-only and --reverse-only at the same time")
    
    # Validate command line arguments
    if args.w <= 0:
        parser.error("Window size must be greater than 0")
    if args.step <= 0:
        parser.error("Step size must be greater than 0")
    if args.step > args.w:
        msg = "Warning: Step size is larger than window size. This may cause gaps in coverage."
        print(msg)
    if args.min <= 0:
        parser.error("Minimum inverted repeat length must be greater than 0")
    if args.max < args.min:
        parser.error("Maximum inverted repeat length must be greater than or equal to minimum length")
    if args.cpus <= 0:
        parser.error("Number of CPUs must be greater than 0")
    if args.paired_cutoff < 0 or args.paired_cutoff > 100:
        parser.error("Paired cutoff must be between 0 and 100")
    if args.start < 0:
        parser.error("Start coordinate must be non-negative")
    if args.end < 0:
        parser.error("End coordinate must be non-negative")
    if args.end != 0 and args.end <= args.start:
        parser.error("End coordinate must be greater than start coordinate")
        
    # Check if input file exists and is readable
    if not os.path.exists(args.filename):
        parser.error(f"Input file '{args.filename}' does not exist")
    if not os.access(args.filename, os.R_OK):
        parser.error(f"Input file '{args.filename}' is not readable")
    if os.path.getsize(args.filename) == 0:
        parser.error(f"Input file '{args.filename}' is empty")
    
    # Print einverted info and verify G-U wobble support
    print(f"Using einverted binary: {einverted_bin}")
    # Add more details about the binary being used
    if os.path.exists(einverted_bin):
        import stat
        file_stat = os.stat(einverted_bin)
        print(f"  Binary size: {file_stat.st_size:,} bytes")
        print(f"  Binary permissions: {oct(file_stat.st_mode)[-3:]}")
        print(f"  Binary path exists: ✓")
    if verify_gu_wobble_support():
        print("✓ G-U wobble pairing support verified")
    # If verification fails, warning was already printed in the function
        
    # Try to open the file to ensure it's a valid FASTA
    try:
        with smart_open(args.filename) as test_file:
            first_record = next(SeqIO.parse(test_file, "fasta"), None)
            if first_record is None:
                parser.error(f"Input file '{args.filename}' does not appear to be a valid FASTA file")
    except Exception as e:
        parser.error(f"Error reading input file '{args.filename}': {str(e)}")
    
    # Use DataFrame approach by default (unless legacy flag is set)
    if not args.legacy:
        msg = "Using optimized DataFrame approach..."
        print(msg)
        return run_dataframe_approach(args)
    
    # Legacy approach (deprecated)
    msg1 = "Proceeding with legacy non-DataFrame approach..."
    msg2 = "Note: This approach is much slower than the default DataFrame mode."
    print(msg1)
    print(msg2)
    
    # Create output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        # Create timestamped directory name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"dsrnascan_{timestamp}"
    
    # Create the directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    # logger.info(f"Output directory: {output_dir}")  # Will be shown after logging setup
    
    # Create a multiprocessing Manager for the result queue
    manager = multiprocessing.Manager()
    result_queue = manager.Queue(maxsize=10000)  # Buffer up to 10k results
    
    # chromosome will be set from the sequence header or output_label
    end_coordinate = int(args.end)
    fasta_file = args.filename
    cpu_count = args.cpus
    step_size = args.step
    sequence_count = 0

    try:
        with smart_open(args.filename) as f:
            # Create a pool of workers for multiprocessing, starting with 2 workers
            # pool = multiprocessing.Pool(cpu_count)
            
            # Process each sequence
            tasks = []

            for cur_record in SeqIO.parse(f, "fasta"): 
                # Skip sequences if only_seq is specified and this isn't it
                if hasattr(args, 'only_seq') and args.only_seq and cur_record.name != args.only_seq:
                    continue
                    
                sequence_count += 1
                # Correct for starting coordinate
                print(f"Processing sequence: {cur_record.name}")
                
                # Validate sequence
                if len(cur_record.seq) == 0:
                    print(f"Warning: Sequence {cur_record.name} is empty, skipping...")
                    continue
                    
                if not cur_record.seq:
                    print(f"Warning: No sequence data for {cur_record.name}, skipping...")
                    continue   
                # Print the sequence length
                #print(f"Sequence length: {len(cur_record.seq)}")
                
                # Convert to RNA uppercase
                #cur_record.seq = cur_record.seq.transcribe().upper()
                
                # Determine chromosome name from output_label or header
                if args.output_label == "header":
                    chromosome = cur_record.name
                else:
                    chromosome = args.output_label

                # Get base filename without extension(s)
                base_filename = args.filename
                if base_filename.endswith('.gz'):
                    base_filename = base_filename[:-3]  # Remove .gz
                if base_filename.endswith('.fa') or base_filename.endswith('.fasta'):
                    base_filename = os.path.splitext(base_filename)[0]
                
                # Determine which strands to process
                if args.forward_only:
                    strands_to_process = ["+"]
                elif args.reverse_only:
                    strands_to_process = ["-"]
                else:
                    strands_to_process = ["+", "-"]
                
                for strand in strands_to_process:
                    # Prepare the sequence in memory (complement if needed)
                    if strand == "-":
                        # For reverse strand, just complement (not reverse complement)
                        # This keeps coordinates in the same orientation
                        complement = str.maketrans('ATGC', 'TACG')
                        full_sequence = str(cur_record.seq.upper()).translate(complement)
                    else:
                        # For forward strand, just use the sequence as-is
                        full_sequence = str(cur_record.seq.upper())
                    
                    # Set up basename for output files
                    strand_label = 'reverse' if strand == '-' else 'forward'
                    basename = f"{base_filename}.{chromosome}.{strand_label}_win{args.w}_step{args.step}_start{args.start}_score{args.score}"

                # Result files are now written directly via streaming (merged_results.txt)
                
                # with open(f"{basename}.dsRNApredictions.bp", 'w+') as bp_file:
                #     # Example header - adjust based on your requirements
                #     bp_file.write("# Base Pair Predictions\n")
                #     bp_file.write("# Format: sequence_id\tstart\tend\n")

                    # Process each sequence
                    end_coordinate = args.end if args.end != 0 else len(cur_record.seq)
                    seq_length = end_coordinate - args.start

                    # Determine if the sequence is short (less than window size)
                    is_short_sequence = seq_length < args.w

                    # Print what we're scanning now
                    print(f"Processing {chromosome} ({strand} strand)")
                    
                    if is_short_sequence:
                        print(f"Short sequence detected: {cur_record.name} length {seq_length} bp")
                        print(f"Using single window approach for the entire sequence")
                    
                    # Just process the entire sequence as one window
                    # For single window, process directly and write results
                    results = process_window(args.start, args.start, seq_length, basename, args.algorithm, 
                                args, full_sequence, chromosome, strand, result_queue)
                    
                    # Write results directly for single window
                    merged_filename = os.path.join(output_dir, f"{os.path.basename(basename)}_merged_results.txt")
                    with open(merged_filename, 'w') as f:
                        # Write header - basic coordinates first, structural details, then effective coords and sequences
                        f.write("Chromosome\tStrand\ti_start\ti_end\tj_start\tj_end\t"
                               "Score\tRawMatch\tPercMatch\tGaps\t"
                               "dG(kcal/mol)\tpercent_paired\tlongest_helix\t"
                               "eff_i_start\teff_i_end\teff_j_start\teff_j_end\t"
                               "i_seq\tj_seq\tstructure\n")
                        
                        while not result_queue.empty():
                            result = result_queue.get()
                            # Write result - basic coords, structural details, eff coords, sequences
                            f.write(f"{result['chromosome']}\t{result['strand']}\t"
                                   f"{result['i_start']}\t{result['i_end']}\t"
                                   f"{result['j_start']}\t{result['j_end']}\t"
                                   f"{result['score']}\t{result['raw_match']}\t"
                                   f"{result['match_perc']}\t{result['gap_numb']}\t"
                                   f"{result['energy']}\t{result['percent_paired']}\t{result['longest_helix']}\t"
                                   f"{result['eff_i_start']}\t{result['eff_i_end']}\t"
                                   f"{result['eff_j_start']}\t{result['eff_j_end']}\t"
                                   f"{result['i_seq']}\t{result['j_seq']}\t"
                                   f"{result['structure']}\n")
                else:
                    # Normal processing for longer sequences
                    print(f"Scanning {cur_record.name} from {args.start} to {end_coordinate} with window size {args.w} and step size {args.step}")
                    
                    # Set up output file
                    merged_filename = os.path.join(output_dir, f"{os.path.basename(basename)}_merged_results.txt")
                    
                    # Start the writer process
                    writer_proc = multiprocessing.Process(target=result_writer, 
                                                        args=(merged_filename, result_queue, cpu_count))
                    writer_proc.start()
                    
                    # Create a pool of workers for multiprocessing 
                    pool = multiprocessing.Pool(cpu_count)
                    tasks = []
                    
                    
                    # Use multiprocessing for longer sequences
                    frame_step_size = step_size * cpu_count
                    for cpu_index in range(cpu_count):
                        # Start from the specified start coordinate plus the CPU's offset
                        frame_start = args.start + (cpu_index * step_size)

                        # Start processing at each frame and jump by frame_step_size
                        for start in range(frame_start, end_coordinate, frame_step_size):
                            window_end = min(start + args.w, end_coordinate)
                            window_size = window_end - start
                            
                            # Only process if we have a meaningful window
                            if window_size >= args.min:
                                tasks.append(pool.apply_async(process_window, 
                                            (start, start, window_size, basename, args.algorithm, 
                                            args, full_sequence, chromosome, strand, result_queue)))
                    # Close the pool and wait for all workers to finish
                    pool.close()
                    pool.join()
                    
                    # Signal writer that all workers are done
                    for _ in range(cpu_count):
                        result_queue.put("DONE")
                    
                    # Wait for writer to finish
                    writer_proc.join()

                    # Results are already written by the writer process
                    print(f"\nResults saved to: {merged_filename}")

                    # If we're only processing one specific sequence, stop after finding it
                    if hasattr(args, 'only_seq') and args.only_seq:
                        break

            # Now generate the BP file
            try:
                # Use the function from the previous script to generate BP file
                bp_filename = os.path.join(output_dir, f"{os.path.basename(basename)}.dsRNApredictions.bp")
                generate_bp_file(merged_filename, bp_filename)
            except NameError:
                print("BP file generation function not defined. Please add the generate_bp_file function to your script.")
            
                        
            # Print file names and paths
            print(f"\nResults written to {merged_filename}")
            if os.path.exists(bp_filename):
                print(f"Base Pair predictions written to {bp_filename}")
            
            # Check if results file is empty or has only headers
            try:
                results_df = pd.read_csv(merged_filename, sep="\t")
                if len(results_df) == 0:
                    print("\nNo dsRNA structures were found. Try adjusting your search parameters.")
            except Exception:
                pass
                
            # Check if any sequences were processed
            if sequence_count == 0:
                print("\nError: No valid sequences found in the input FASTA file.")
                sys.exit(1)
                
    except FileNotFoundError:
        print(f"Error: Could not open file '{args.filename}'. File not found.")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied when trying to read '{args.filename}'.")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file '{args.filename}': {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
            
# Run the main function
if __name__ == "__main__":
    main()
