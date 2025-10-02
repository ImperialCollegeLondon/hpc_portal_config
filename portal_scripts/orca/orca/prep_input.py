#!/usr/bin/env python3
"""
ORCA input file preparation script.

Modifies ORCA input files to use cluster-specified resource allocations
by replacing memory and CPU directives with values from environment variables.
"""

import os
import re
import sys
from pathlib import Path

MEMORY_PROPORTION_FOR_CALC = 0.9  # Use 90% of available memory for calculation

def prep_orca_input(inp_file: str) -> None:
    """
    Modify ORCA input file to use environment-specified resources.
    
    Replaces any existing %pal nprocs and %maxcore directives with values
    from NCORES and MEMORY_GB environment variables.
    
    Args:
        inp_file: Path to the ORCA input file (.inp) to be modified.
    
    Raises:
        SystemExit: If input file doesn't exist or environment variables are not set.
    """
    inp_path = Path(inp_file)
    
    # Validate input file exists
    if not inp_path.exists():
        print(f"Input file {inp_file} does not exist.", file=sys.stderr)
        sys.exit(1)
    
    # Get resource allocation from environment
    try:
        ncores = int(os.environ["NCORES"])
        memory_gb = float(os.environ["MEMORY_GB"])
    except KeyError as e:
        print(f"Environment variable {e} is not set.", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        print("NCORES must be an integer and MEMORY_GB must be a number.", file=sys.stderr)
        sys.exit(1)
    
    # Calculate memory per core in MB
    memory_mb_per_core = int((memory_gb * 1024 * MEMORY_PROPORTION_FOR_CALC) / ncores)
    
    # Read input file
    content = inp_path.read_text()
    
    # Remove existing %maxcore directive
    content = re.sub(
        r'%maxcore\s+\d+\s*\n?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Remove existing %pal block
    content = re.sub(
        r'%pal\s*\n(?:\s+.*\n)*?end\s*\n?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Add new resource directives at the start of file
    new_directives = f"%maxcore {memory_mb_per_core}\n\n%pal\n   nprocs {ncores}\nend\n\n"
    content = new_directives + content
    
    # Write modified content back to file
    inp_path.write_text(content)


def main():
    """Command line entry point."""
    if len(sys.argv) != 2:
        print("Usage: prep_input.py <orca_input_file>", file=sys.stderr)
        sys.exit(1)
    
    prep_orca_input(sys.argv[1])


if __name__ == "__main__":
    main()