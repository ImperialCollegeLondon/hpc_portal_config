from opi.core import Calculator
from opi.input.simple_keywords import BasisSet, Method, Scf, Task
from opi.input.structures import Structure
from orca.publish import publish_orca_files

def test_publish_orca_with_water(tmp_path):
    """Test publish_orca.py with water molecule calculation."""
    
    # Define water molecule geometry
    xyz_content = """3
    Water molecule
    O         -3.56626        1.77639        0.00000
    H         -2.59626        1.77639        0.00000
    H         -3.88959        1.36040       -0.81444"""
    
    # Create xyz file
    xyz_file = tmp_path / "water.xyz"
    xyz_file.write_text(xyz_content)
    
    # Set up ORCA calculation
    structure = Structure.from_xyz(str(xyz_file))
    working_dir = tmp_path / "RUN"
    working_dir.mkdir()
    
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
    output.parse()
    expected_energy = output.results_properties.geometries[-1].single_point_data.finalenergy
    
    # Test our publish function
    inp_file = working_dir / "water.inp"
    publish_orca_files(str(inp_file))
    
    # Check FILES_TO_PUBLISH was created correctly
    files_to_publish = working_dir / "FILES_TO_PUBLISH"
    assert files_to_publish.exists()
    content = files_to_publish.read_text()
    assert "water.inp\tORCA input file" in content
    assert "water.out\tORCA output file" in content
    assert "water.gbw\tORCA wavefunction file" in content
    
    # Check METADATA was created correctly
    metadata_file = working_dir / "METADATA"
    assert metadata_file.exists()
    metadata_content = metadata_file.read_text()
    assert f"Final_Energy\t{expected_energy:.8f}" in metadata_content
    assert "Number_of_Atoms\t3" in metadata_content