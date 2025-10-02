"""
ORCA output publishing script.
"""

import sys
from pathlib import Path
from opi.output.core import Output

def publish_orca_files(inp_file: str) -> None:
    """
    Generate FILES_TO_PUBLISH and METADATA files for an ORCA calculation.
    
    This function creates two output files:
    1. FILES_TO_PUBLISH - Lists calculation files with descriptions
    2. METADATA - Contains extracted calculation results and properties
    
    Args:
        inp_file: Path to the ORCA input file (.inp). The function expects
                 corresponding .out and .gbw files to exist in the same directory.
    
    Raises:
        SystemExit: If required files don't exist or cannot be processed.
    """
    inp_path = Path(inp_file)
    
    # Validate input file exists
    if not inp_path.exists():
        print(f"Input file {inp_file} does not exist.", file=sys.stderr)
        sys.exit(1)
    
    # Determine file paths based on input file location and basename
    base_name = inp_path.stem
    working_dir = inp_path.parent
    gbw_path = working_dir / f"{base_name}.gbw"
    out_path = working_dir / f"{base_name}.out"

    # Validate required output files exist
    if not out_path.exists():
        print(f"Output file {out_path} does not exist.", file=sys.stderr)
        sys.exit(1)

    if not gbw_path.exists():
        print(f"Wavefunction file {gbw_path} does not exist.", file=sys.stderr)
        sys.exit(1)

    # Generate FILES_TO_PUBLISH with file inventory
    files_to_publish = working_dir / "FILES_TO_PUBLISH"
    with open(files_to_publish, "w", encoding="utf-8") as f:
        f.write("name\tdescription\n")
        f.write(f"{inp_path.name}\tORCA input file\n")
        f.write(f"{out_path.name}\tORCA output file\n")
        f.write(f"{gbw_path.name}\tORCA wavefunction file\n")
    
    # Generate METADATA with calculation results
    metadata_file = working_dir / "METADATA"
    with open(metadata_file, "w", encoding="utf-8") as f:
        f.write("name\tvalue\n")

        # Parse ORCA output to extract calculation results
        output = Output(base_name, working_dir=working_dir, 
                       create_gbw_json=True, create_property_json=True)
        output.parse()
        
        # Extract and write calculated properties
        if output.terminated_normally():
            final_energy = output.results_properties.geometries[-1].single_point_data.finalenergy
            f.write(f"Final_Energy\t{final_energy:.8f}\n")
            
            coords = output.results_properties.geometries[-1].geometry.coordinates.cartesians
            f.write(f"Number_of_Atoms\t{len(coords)}\n")


def main():
    """Command line entry point."""
    if len(sys.argv) != 2:
        print("Usage: publish_orca.py <orca_input_file>", file=sys.stderr)
        sys.exit(1)
    
    publish_orca_files(sys.argv[1])


if __name__ == "__main__":
    main()