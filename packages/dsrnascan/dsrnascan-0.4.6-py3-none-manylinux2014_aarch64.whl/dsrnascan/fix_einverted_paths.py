#!/usr/bin/env python
"""
Quick fix for einverted path issues - creates expected directory structure
"""
import os
import platform
import subprocess
from pathlib import Path

def setup_einverted_environment():
    """Create the directory structure that einverted expects"""
    
    # Determine what path the binary expects based on platform
    if platform.system() == "Linux":
        expected_path = Path("/tmp/EMBOSS-6.6.0/emboss/acd")
    else:
        # macOS and others probably work already
        return True
    
    # Create the directory if it doesn't exist
    expected_path.mkdir(parents=True, exist_ok=True)
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Copy minimal required files
    acd_files = ["einverted.acd", "codes.english", "knowntypes.standard"]
    
    for filename in acd_files:
        source = script_dir / "emboss_acd" / filename
        dest = expected_path / filename
        
        if source.exists() and not dest.exists():
            # Create minimal file if source doesn't exist
            if filename == "einverted.acd":
                dest.write_text("""application: einverted [
  documentation: "Finds inverted repeats"
  groups: "Nucleic:Repeats"
]
section: input [
  information: "Input"
  type: "page"
]
  seqall: sequence [
    parameter: "Y"
    type: "DNA"
  ]
endsection: input
section: required [
  information: "Required" 
  type: "page"
]
  integer: gap [
    standard: "Y"
    default: "12"
  ]
  integer: threshold [
    standard: "Y" 
    default: "50"
  ]
  integer: match [
    standard: "Y"
    default: "3"
  ]
  integer: mismatch [
    standard: "Y"
    default: "-4"
  ]
  integer: maxrepeat [
    standard: "Y"
    default: "2000"
  ]
endsection: required
section: output [
  information: "Output"
  type: "page"
]
  outfile: outfile [
    parameter: "Y"
  ]
  seqout: outseq [
    nullok: "Y"
  ]
endsection: output
""")
            else:
                # Create empty files for the others
                dest.touch()
    
    return True

# Call this before using einverted
if __name__ == "__main__":
    setup_einverted_environment()
    print("einverted environment setup complete")