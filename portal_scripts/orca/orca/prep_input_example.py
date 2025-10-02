"""
Example script demonstrating ORCA input file preparation.

Creates a simple water molecule calculation, writes the input file,
then modifies it using prep_input.py with hardcoded resource allocations.
"""

import os
import subprocess
from pathlib import Path

from opi.core import Calculator
from opi.input.simple_keywords import BasisSet, Method, Scf, Task
from opi.input.structures import Structure


def main():
    """Create example demonstrating input file preparation."""
    # Define water molecule geometry
    xyz_content = """3
Water molecule
O         -3.56626        1.77639        0.00000
H         -2.59626        1.77639        0.00000
H         -3.88959        1.36040       -0.81444"""
    
    # Set up working directory
    current_dir = Path(__file__).parent.resolve()
    working_dir = current_dir / "EXAMPLE_PREP"
    if not working_dir.exists():
        working_dir.mkdir()
    
    # Create xyz file
    xyz_file = working_dir / "water.xyz"
    xyz_file.write_text(xyz_content)
    
    # Set up ORCA calculation with initial resource settings
    structure = Structure.from_xyz(str(xyz_file))
    calc = Calculator(basename="water", working_dir=working_dir)
    calc.structure = structure
    calc.input.memory = 4000
    calc.input.ncores = 2
    calc.input.add_simple_keywords(
        Scf.NOAUTOSTART,
        Method.HF,
        BasisSet.DEF2_SVP,
        Task.SP,
    )
    
    # Write original input file
    calc.write_input()
    
    original_inp = working_dir / "water.inp"
    original_content = original_inp.read_text()
    
    # Save original input file for comparison
    original_saved = working_dir / "water_original.inp"
    original_saved.write_text(original_content)
    
    # Set environment variables for resource allocation
    env = os.environ.copy()
    env["NCORES"] = "8"
    env["MEMORY_GB"] = "32"
    
    # Run prep_input.py to modify the input file
    prep_script = current_dir / "prep_input.py"
    subprocess.run(
        ["python3", str(prep_script), str(original_inp)],
        env=env,
        check=True
    )

if __name__ == "__main__":
    main()