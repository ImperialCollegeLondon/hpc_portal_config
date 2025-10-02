"""
Tests for ORCA input file preparation script.
"""

import os

from opi.core import Calculator
from opi.input.simple_keywords import BasisSet, Method, Scf, Task
from opi.input.structures import Structure

from prep_input import prep_orca_input, MEMORY_PROPORTION_FOR_CALC


def test_prep_orca_input_modifies_resources(tmp_path):
    """Test that prep_orca_input correctly modifies resource directives."""
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
    
    # Write input file with default settings
    calc.write_input()
    
    inp_file = working_dir / "water.inp"
    
    # Set test resource allocation
    test_ncores = 16
    test_memory_gb = 48
    expected_memory_mb_per_core = int((test_memory_gb * 1024 * MEMORY_PROPORTION_FOR_CALC) / test_ncores)
    
    # Set environment variables
    os.environ["NCORES"] = str(test_ncores)
    os.environ["MEMORY_GB"] = str(test_memory_gb)
    
    # Run preparation function
    prep_orca_input(str(inp_file))
    
    # Read modified input file
    modified_content = inp_file.read_text()
    
    # Verify resource directives were added correctly
    assert f"%maxcore {expected_memory_mb_per_core}" in modified_content
    assert "%pal" in modified_content
    assert f"nprocs {test_ncores}" in modified_content
    assert "end" in modified_content
    
    # Verify formatting matches expected style
    lines = modified_content.split('\n')
    
    # Find the %pal block and verify formatting
    pal_index = next(i for i, line in enumerate(lines) if '%pal' in line.lower())
    assert 'nprocs' in lines[pal_index + 1]
    assert lines[pal_index + 1].startswith('   ')  # Should be indented
    assert lines[pal_index + 2].strip() == 'end'


def test_prep_orca_input_removes_existing_directives(tmp_path):
    """Test that existing resource directives are replaced, not duplicated."""
    # Create input file with existing resource directives in the expected format
    inp_content = """%maxcore 2000

%pal
   nprocs 4
end

! HF DEF2-SVP
* xyz 0 1
O  0.0  0.0  0.0
H  1.0  0.0  0.0
H  0.0  1.0  0.0
*
"""
    
    inp_file = tmp_path / "test.inp"
    inp_file.write_text(inp_content)
    
    # Set environment variables
    os.environ["NCORES"] = "8"
    os.environ["MEMORY_GB"] = "32"
    expected_memory_mb_per_core = int((32 * 1024 * MEMORY_PROPORTION_FOR_CALC) / 8)
    
    # Run preparation function
    prep_orca_input(str(inp_file))
    
    # Read modified content
    modified_content = inp_file.read_text()
    
    # Count occurrences of resource directives (should appear exactly once)
    assert modified_content.count("%pal") == 1
    assert modified_content.count("%maxcore") == 1
    assert modified_content.count("nprocs 8") == 1
    assert modified_content.count(f"{expected_memory_mb_per_core}") == 1
    
    # Verify old values are not present
    assert "nprocs 4" not in modified_content
    assert "2000" not in modified_content