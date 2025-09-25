from opi.core import Calculator
from opi.input.simple_keywords import BasisSet, Method, Scf, Task
from opi.input.structures import Structure
from orca.publish import publish_orca_files
from pathlib import Path

def main():
    """ Create an illustrative example of the files created by publish.py """
    # Define water molecule geometry
    xyz_content = """3
    Water molecule
    O         -3.56626        1.77639        0.00000
    H         -2.59626        1.77639        0.00000
    H         -3.88959        1.36040       -0.81444"""

    current_dir = Path(__file__).parent.resolve()
    working_dir = current_dir / "EXAMPLE_PUBLISH"
    if not working_dir.exists():
        working_dir.mkdir()
    
    # Create xyz file
    xyz_file = working_dir / "water.xyz"
    xyz_file.write_text(xyz_content)
    
    # Set up ORCA calculation
    structure = Structure.from_xyz(str(xyz_file))
    calc = Calculator(basename="water", working_dir=working_dir)
    calc.structure = structure
    calc.input.add_simple_keywords(
        Scf.NOAUTOSTART,
        Method.HF,
        BasisSet.DEF2_SVP,
        Task.SP,
    )
    
    # Run calculation
    calc.write_input()
    calc.run()
    
    # Get expected results
    output = calc.get_output()
    assert output.terminated_normally()

    # Test our publish function
    inp_file = working_dir / "water.inp"
    publish_orca_files(str(inp_file))

    # delete all the orca files
    files_to_keep = {"FILES_TO_PUBLISH", "METADATA"}
    files_deleted = 0
    for file_path in working_dir.iterdir():
        if file_path.is_file() and file_path.name not in files_to_keep:
            file_path.unlink()
            files_deleted += 1

if __name__ == "__main__":
    main()