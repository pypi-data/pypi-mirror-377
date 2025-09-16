import os
import pytest

from src.vtk_openCARP_methods_ibt.openCARP.exporting import write_mesh_from_vtk_obj
from src.vtk_openCARP_methods_ibt.vtk_methods.exporting import vtk_polydata_writer
from src.vtk_openCARP_methods_ibt.openCARP.importing import convert_openCARP_to_vtk, convert_openCARP_to_vtk_single_name
from tests.openCARP.test_writing import _setup_basic_geom, _setup_fibers, _setup_sheet, _setup_elm_tag

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = SCRIPT_PATH + "/../../data"


def test_working_conversion():
    test_file = f"{DATA_DIR}/cube"
    resulting_mesh = convert_openCARP_to_vtk(test_file + ".pts", test_file + ".elem", test_file + ".lon")
    vtk_polydata_writer(test_file + ".vtk", resulting_mesh)


def test_wrong_filename():
    test_file = f"{DATA_DIR}/cube_wrong"
    with pytest.raises(FileNotFoundError):
        convert_openCARP_to_vtk(test_file + ".pts", test_file + ".elem", test_file + ".lon")


def test_direct_openCARP_importing():
    grid = _setup_geom()
    read_grid = convert_openCARP_to_vtk_single_name(f"{DATA_DIR}/test_opencarp")
    _assert_vtk_objects_equal(grid, read_grid)


def test_direct_openCARP_importing_no_sheet():
    grid = _setup_geom(f"{DATA_DIR}/test_opencarp_nosheet")
    read_grid = convert_openCARP_to_vtk_single_name(f"{DATA_DIR}/test_opencarp_nosheet")
    _assert_vtk_objects_equal(grid, read_grid)


def _setup_geom(file_name: str = f"{DATA_DIR}/test_opencarp"):
    grid = _setup_basic_geom()
    _setup_fibers(grid)
    _setup_sheet(grid)
    _setup_elm_tag(grid)

    # Export to openCARP format
    write_mesh_from_vtk_obj(file_name, grid)
    return grid


def _assert_vtk_objects_equal(obj1, obj2):
    """Compare two VTK objects for equality by checking points and cells."""
    assert obj1.GetNumberOfPoints() == obj2.GetNumberOfPoints(), "Different number of points"
    assert obj1.GetNumberOfCells() == obj2.GetNumberOfCells(), "Different number of cells"

    # Compare points
    for i in range(obj1.GetNumberOfPoints()):
        assert obj1.GetPoint(i) == obj2.GetPoint(i), f"Point {i} differs"

    # Compare cells
    for i in range(obj1.GetNumberOfCells()):
        cell1 = obj1.GetCell(i)
        cell2 = obj2.GetCell(i)
        assert cell1.GetNumberOfPoints() == cell2.GetNumberOfPoints(), f"Cell {i} has different number of points"
        for j in range(cell1.GetNumberOfPoints()):
            assert cell1.GetPointId(j) == cell2.GetPointId(j), f"Cell {i} point {j} differs"
