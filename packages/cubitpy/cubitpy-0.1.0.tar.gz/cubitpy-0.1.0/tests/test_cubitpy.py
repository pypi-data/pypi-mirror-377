# The MIT License (MIT)
#
# Copyright (c) 2018-2025 CubitPy Authors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""This script is used to test the functionality of the cubitpy module."""

import os
import shutil
import subprocess

import numpy as np
import pytest
from deepdiff import DeepDiff
from fourcipp.fourc_input import FourCInput

# Define the testing paths.
testing_path = os.path.abspath(os.path.dirname(__file__))
testing_input = os.path.join(testing_path, "input-files-ref")
testing_temp = os.path.join(testing_path, "testing-tmp")
testing_external_geometry = os.path.join(testing_path, "external-geometry")

# CubitPy imports.
from cubitpy.conf import cupy
from cubitpy.cubit_utility import get_surface_center, import_fluent_geometry
from cubitpy.cubitpy import CubitPy
from cubitpy.geometry_creation_functions import (
    create_brick_by_corner_points,
    create_parametric_surface,
    create_spline_interpolation_curve,
)
from cubitpy.mesh_creation_functions import create_brick, extrude_mesh_normal_to_surface

# Global variable if this test is run by GitLab.
if "TESTING_GITHUB" in os.environ.keys() and os.environ["TESTING_GITHUB"] == "1":
    TESTING_GITHUB = True
else:
    TESTING_GITHUB = False

CUBIT_VERSION_TESTING_IDENTIFIER = {True: "coreform", False: "cubit15"}[
    cupy.is_coreform()
]


def check_tmp_dir():
    """Check if the temp directory exists, if not create it."""
    os.makedirs(testing_temp, exist_ok=True)


def compare_yaml(
    cubit,
    *,
    base_name=None,
    additional_identifier=None,
    rtol=1.0e-12,
    atol=1.0e-12,
    mesh_in_exo=False,
):
    """Write and compare the YAML file from a Cubit object with the reference
    YAML file.

    Args
    ----
    cubit: Cubit object
        Should implement `create_yaml(path)` to generate the test output.
    base_name: str, optional
        Base name of the test, per default this is the current test name.
    additional_identifier: str, optional
        Additional identifier added to the base name of the test to result
        in the reference file.
    rtol: float
        Relative tolerance for numerical differences.
    atol: float
        Absolute tolerance for numerical differences.
    mesh_in_exo: bool
        If true, the mesh is dumped in exodus format instead of YAML, meaning
        that two files are created, so we perform an additional check to make
        sure the exodus file is also created. Default is False.
    """
    # Determine test name
    if base_name is None:
        compare_name = (
            os.environ.get("PYTEST_CURRENT_TEST")
            .split(":")[-1]
            .split(" ")[0]
            .split("[")[0]
        )
    else:
        compare_name = base_name
    if additional_identifier is not None:
        compare_name += "_" + additional_identifier

    check_tmp_dir()

    # File paths
    ref_file = os.path.join(testing_input, compare_name + ".4C.yaml")
    out_file = os.path.join(testing_temp, compare_name + ".4C.yaml")

    if mesh_in_exo:
        # dump the input script with the mesh in exodus format
        cubit.dump(out_file, mesh_in_exo=True)
        # make sure the directory also contains the exo mesh
        out_file_stem = out_file.removesuffix(".4C.yaml")
        assert os.path.exists(f"{out_file_stem}.exo")
    else:
        cubit.dump(out_file)

    ref_input_file = FourCInput.from_4C_yaml(ref_file)
    out_input_file = FourCInput.from_4C_yaml(out_file)

    try:
        files_are_equal = ref_input_file.compare(
            out_input_file,
            allow_int_as_float=True,
            raise_exception=True,
            rtol=rtol,
            atol=atol,
        )
    except AssertionError as exception:
        print(f"[compare] Files differ: {exception}")

        ref_sections = ref_input_file.sections
        out_sections = out_input_file.sections

        for section in ref_sections:
            ref_section_data = ref_sections.get(section)
            out_section_data = out_sections.get(section)

            # Perform yaml comparison
            diff = DeepDiff(
                ref_section_data,
                out_section_data,
                ignore_order=True,
            )
            if diff:
                print(diff.pretty())

        if TESTING_GITHUB:
            subprocess.run(["diff", ref_file, out_file])
        elif shutil.which("meld"):
            subprocess.Popen(["meld", ref_file, out_file])
        elif shutil.which("code"):
            subprocess.Popen(
                ["code", "--diff", ref_file, out_file], stderr=subprocess.PIPE
            ).communicate()
        else:
            print("No viewer avail. - Inspect manually.")
            print(f"Reference: {ref_file}")
            print(f"Generated: {out_file}")
        raise exception
    else:
        assert files_are_equal


def create_block(cubit, np_arrays=False):
    """Create a block with cubit.

    Args
    ----
    cubit: Cubit object.
    np_arrays: bool
        If the cubit interaction is with numpy or python arrays.
    """

    # Dimensions and mesh size of the block.
    block_size = [0.1, 1, 10]
    n_elements = [2, 4, 8]
    if np_arrays:
        lx, ly, lz = np.array(block_size)
        nx, ny, nz = np.array(n_elements)
    else:
        lx, ly, lz = block_size
        nx, ny, nz = n_elements

    # Create the block.
    block = cubit.brick(lx, ly, lz)

    # Move the block.
    move_array = [0, 0, block.bounding_box()[2]]
    if np_arrays:
        move_array = np.array(move_array)
    cubit.move(block, move_array)

    # Set the meshing parameters for the curves.
    for line in block.curves():
        point_on_line = line.position_from_fraction(0.5)
        tangent = np.array(line.tangent(point_on_line))
        if np.abs(np.dot(tangent, [1, 0, 0])) > 1e-5:
            cubit.set_line_interval(line, nx)
        elif np.abs(np.dot(tangent, [0, 1, 0])) > 1e-5:
            cubit.set_line_interval(line, ny)
        elif np.abs(np.dot(tangent, [0, 0, 1])) > 1e-5:
            cubit.set_line_interval(line, nz)
        else:
            raise ArithmeticError("Error")

    # Mesh the block and use a user defined element description
    block.mesh()
    cubit.add_element_type(
        block.volumes()[0],
        cupy.element_type.hex8,
        name="block",
        material={"MAT": 1},
        bc_description={"KINEM": "linear"},
    )

    # Create node sets.
    for i, surf in enumerate(block.surfaces()):
        normal = np.array(surf.normal_at(get_surface_center(surf)))
        if np.dot(normal, [0, 0, -1]) == 1:
            cubit.add_node_set(
                surf,
                name="fix",
                bc_section="DESIGN SURF DIRICH CONDITIONS",
                bc_description={
                    "NUMDOF": 6,
                    "ONOFF": [1, 1, 1, 0, 0, 0],
                    "VAL": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    "FUNCT": [0, 0, 0, 0, 0, 0],
                },
            )
        elif np.dot(normal, [0, 0, 1]) == 1:
            cubit.add_node_set(
                surf,
                name="load",
                bc_section="DESIGN SURF DIRICH CONDITIONS",
                bc_description={
                    "NUMDOF": 6,
                    "ONOFF": [1, 1, 1, 0, 0, 0],
                    "VAL": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    "FUNCT": [0, 0, 0, 0, 0, 0],
                },
            )
        else:
            cubit.add_node_set(
                surf,
                name="load{}".format(i),
                bc_section="DESIGN SURF NEUMANN CONDITIONS",
                bc_description={
                    "NUMDOF": 6,
                    "ONOFF": [1, 1, 1, 0, 0, 0],
                    "VAL": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    "FUNCT": [0, 0, 0, 0, 0, 0],
                },
            )

    # Compare the input file created for 4C.
    compare_yaml(cubit, base_name="test_create_block")


def test_create_block():
    """Test the creation of a cubit block."""

    # Initialize cubit.
    cubit = CubitPy()
    create_block(cubit)


def test_create_block_numpy_arrays():
    """Test the creation of a cubit block."""

    # Initialize cubit.
    cubit = CubitPy()
    create_block(cubit, np_arrays=True)


def test_create_block_multiple():
    """Test the creation of a cubit block multiple time to check that cubit can
    be reset."""

    # Initialize cubit.
    cubit = CubitPy()
    create_block(cubit)

    # Delete the old cubit object and run the function twice on the new.
    cubit = CubitPy()
    for _i in range(2):
        create_block(cubit)
        cubit.reset()

    # Create two object and keep them in parallel.
    cubit = CubitPy()
    cubit_2 = CubitPy()
    create_block(cubit)
    create_block(cubit_2)


def test_create_wedge6():
    """Create a mesh with wedge elements."""
    # Initialize cubit.
    cubit = CubitPy()

    # Create nodes to define two tri elements
    for x in [-0.5, 0.5]:
        for y in [-0.5, 0.5]:
            cubit.cmd("create node location {} {} 0.5".format(x, y))

    # Create tri elements
    cubit.cmd("create tri node 1 2 3")
    cubit.cmd("create tri node 3 2 4")

    # By offsetting the tri elements, create wedge elements
    cubit.cmd("create element offset tri 1 2 distance 0.6 layers 1")

    # Define a group formed by wedge elements
    wedge_group = cubit.group(add_value="add wedge all")

    # Check that we can get the element IDs in the group
    assert [1, 2] == wedge_group.get_item_ids_from_type(
        cupy.finite_element_object.wedge
    )

    # Define the element type of the group
    cubit.add_element_type(
        wedge_group,
        cupy.element_type.wedge6,
        name="wedges",
        material={"MAT": 1},
        bc_description=None,
    )

    # Compare the input file created for 4C
    compare_yaml(cubit)


def test_element_types_tet():
    """Create a curved solid with different tet element types."""

    # Initialize cubit.
    cubit = CubitPy()

    element_type_list = [
        cupy.element_type.tet4,
        cupy.element_type.tet10,
    ]

    for i, element_type in enumerate(element_type_list):
        cubit.cmd("create pyramid height 1 sides 3 radius 1.2 top 0")
        cubit.cmd("move Volume {} x {}".format(i + 1, i))
        volume = cubit.volume(1 + i)
        cubit.add_element_type(
            volume,
            element_type,
            name="block_" + str(i),
            material={"MAT": 1},
            bc_description=None,
        )
        cubit.cmd("Volume {} size 2".format(volume.id()))
        volume.mesh()

        cubit.add_node_set(
            volume.surfaces()[1],
            name="fix_" + str(i),
            bc_section="DESIGN SURF DIRICH CONDITIONS",
            bc_description={
                "NUMDOF": 3,
                "ONOFF": [1, 1, 1],
                "VAL": [0, 0, 0],
                "FUNCT": [0, 0, 0],
            },
        )

    cubit.fourc_input["FUNCT1"] = [{"SYMBOLIC_FUNCTION_OF_TIME": "t"}]

    cubit.fourc_input["MATERIALS"] = [
        {
            "MAT": 1,
            "MAT_Struct_StVenantKirchhoff": {
                "YOUNG": 1.0e9,
                "NUE": 0.3,
                "DENS": 0.0,
            },
        }
    ]

    cubit.fourc_input["IO/RUNTIME VTK OUTPUT/STRUCTURE"] = {
        "OUTPUT_STRUCTURE": True,
        "DISPLACEMENT": True,
    }

    # Compare the input file created for 4C.
    compare_yaml(cubit, additional_identifier=CUBIT_VERSION_TESTING_IDENTIFIER)


def test_element_types_hex():
    """Create a curved solid with different hex element types."""

    # Initialize cubit.
    cubit = CubitPy()

    element_type_list = [
        cupy.element_type.hex8,
        cupy.element_type.hex20,
        cupy.element_type.hex27,
        cupy.element_type.hex8sh,
    ]

    def add_arc(radius, angle):
        """Add a arc segment."""
        cubit.cmd(
            "create curve arc radius {} center location 0 0 0 normal 0 0 1 start angle 0 stop angle {}".format(
                radius, angle
            )
        )

    for i, element_type in enumerate(element_type_list):
        # Offset for the next volume.
        offset_point = i * 12
        offset_curve = i * 12
        offset_surface = i * 6
        offset_volume = i

        # Add two arcs.
        add_arc(1.1, 30)
        add_arc(0.9, 30)

        # Add the closing lines.
        cubit.cmd(
            "create curve vertex {} {}".format(2 + offset_point, 4 + offset_point)
        )
        cubit.cmd(
            "create curve vertex {} {}".format(1 + offset_point, 3 + offset_point)
        )

        # Create the surface.
        cubit.cmd(
            "create surface curve {} {} {} {}".format(
                1 + offset_curve,
                2 + offset_curve,
                3 + offset_curve,
                4 + offset_curve,
            )
        )

        # Create the volume.
        cubit.cmd(
            "sweep surface {} perpendicular distance 0.2".format(1 + offset_surface)
        )

        # Move the volume.
        cubit.cmd("move Volume {} x 0 y 0 z {}".format(1 + offset_volume, i * 0.4))

        # Set the element type.
        cubit.add_element_type(
            cubit.volume(1 + offset_volume),
            element_type,
            name="block_" + str(i),
            material={"MAT": 1},
            bc_description=None,
        )

        # Set mesh properties.
        cubit.cmd("volume {} size 0.2".format(1 + offset_volume))
        cubit.cmd("mesh volume {}".format(1 + offset_volume))

        # Add the node sets.
        cubit.add_node_set(
            cubit.surface(5 + offset_surface),
            name="fix_" + str(i),
            bc_section="DESIGN SURF DIRICH CONDITIONS",
            bc_description={
                "NUMDOF": 3,
                "ONOFF": [1, 1, 1],
                "VAL": [0, 0, 0],
                "FUNCT": [0, 0, 0],
            },
        )

    cubit.fourc_input["FUNCT1"] = [{"SYMBOLIC_FUNCTION_OF_TIME": "t"}]

    cubit.fourc_input["MATERIALS"] = [
        {
            "MAT": 1,
            "MAT_Struct_StVenantKirchhoff": {
                "YOUNG": 1e9,
                "NUE": 0.3,
                "DENS": 0,
            },
        }
    ]

    cubit.fourc_input["IO/RUNTIME VTK OUTPUT/STRUCTURE"] = {
        "OUTPUT_STRUCTURE": True,
        "DISPLACEMENT": True,
    }
    # Compare the input file created for 4C.
    compare_yaml(cubit)


@pytest.mark.parametrize("plane", ["zplane", "yplane"])
def test_element_types_quad(plane):
    """Create a quad mesh on the given plane.

    We check two planes there because for 2D output depending on the
    plane that the nodes are on, cubit might drop the third coordinate
    entry if the automatic option from cubit while exporting the exo
    file is chosen.
    """
    cubit = CubitPy()
    cubit.cmd(f"create surface rectangle width 1 height 2 {plane}")
    cubit.cmd("curve 1 3 interval 3")
    cubit.cmd("curve 2 4 interval 2")
    cubit.cmd("mesh surface 1")
    cubit.add_element_type(
        cubit.surface(1),
        cupy.element_type.quad4,
        material={"MAT": 1},
        bc_description={
            "KINEM": "nonlinear",
            "EAS": "none",
            "THICK": 1.0,
            "STRESS_STRAIN": "plane_stress",
            "GP": [3, 3],
        },
    )
    compare_yaml(cubit, additional_identifier=plane)


def test_block_function():
    """Create a solid block with different element types."""

    # Initialize cubit.
    cubit = CubitPy()

    element_type_list = [
        cupy.element_type.hex8,
        cupy.element_type.hex20,
        cupy.element_type.hex27,
        cupy.element_type.hex8sh,
    ]

    count = 0
    for interval in [True, False]:
        for element_type in element_type_list:
            if interval:
                kwargs_brick = {"mesh_interval": [3, 2, 1]}
            else:
                kwargs_brick = {"mesh_factor": 10}
            cube = create_brick(
                cubit,
                0.5,
                0.6,
                0.7,
                element_type=element_type,
                name=f"{element_type} {count}",
                mesh=False,
                **kwargs_brick,
            )
            cubit.move(cube, [count, 0, 0])
            cube.volumes()[0].mesh()
            count += 1

    # Compare the input file created for 4C.
    out_file = os.path.join(testing_temp, "tmp" + ".4C.yaml")
    cubit.dump(out_file)
    compare_yaml(cubit)


def test_extrude_mesh_function():
    """Test the extrude mesh function."""

    # Initialize cubit.
    cubit = CubitPy()

    # Create dummy geometry to check, that the extrude functions work with
    # already existing geometry.
    cubit.cmd("create surface circle radius 1 zplane")
    cubit.cmd("mesh surface 1")
    cubit.cmd("create brick x 1")
    cubit.cmd("mesh volume 2")

    # Create and cut torus.
    cubit.cmd("create torus major radius 1.0 minor radius 0.5")
    torus_vol_id = cubit.get_entities(cupy.geometry.volume)[-1]
    cut_text = "webcut volume {} with plane {}plane offset {} imprint merge"
    cubit.cmd(cut_text.format(torus_vol_id, "x", 1.0))
    cubit.cmd(cut_text.format(torus_vol_id, "y", 0.0))
    surface_ids = cubit.get_entities(cupy.geometry.surface)
    cut_surface_ids = [surface_ids[-4], surface_ids[-1]]
    cut_surface_ids_string = " ".join(map(str, cut_surface_ids))
    cubit.cmd("surface {} size auto factor 9".format(cut_surface_ids_string))
    cubit.cmd("mesh surface {}".format(cut_surface_ids_string))
    # Extrude the surface.
    volume = extrude_mesh_normal_to_surface(
        cubit,
        [cubit.surface(i) for i in cut_surface_ids],
        0.3,
        n_layer=3,
        extrude_dir="symmetric",
        offset=[1, 2, 3],
    )

    # Check the created volume.
    if cupy.is_coreform():
        ref_volume = 0.6934429579015018
    else:
        ref_volume = 0.6917559630511103
    assert ref_volume == pytest.approx(
        cubit.get_meshed_volume_or_area("volume", [volume.id()]), 1e-10
    )

    # Set the mesh for output.
    cubit.add_element_type(volume, cupy.element_type.hex8)

    # Compare the input file created for 4C.
    compare_yaml(cubit)


def test_extrude_mesh_function_average_normals_block():
    """Test the average extrude mesh function for two blocks."""

    # Initialize cubit.
    cubit = CubitPy()

    # Create L-shaped geometry.
    cubit.cmd("create brick x 1")
    cubit.cmd("create brick x 2 y 1 z 1")
    cubit.cmd("move volume 1 x -0.5 y 1")
    cubit.cmd("unite volume 1,2")

    # Extract surfaces normal to eacht other.
    surface_ids = cubit.get_entities(cupy.geometry.surface)
    extrude_surface_ids = [surface_ids[-4], surface_ids[-1]]
    extrude_surface_ids_string = " ".join(map(str, extrude_surface_ids))

    # Create the mesh.
    cubit.cmd("surface {} size auto factor 9".format(extrude_surface_ids_string))
    cubit.cmd("mesh surface {}".format(extrude_surface_ids_string))

    # Extrude the surfaces.
    volume = extrude_mesh_normal_to_surface(
        cubit,
        [cubit.surface(i) for i in extrude_surface_ids],
        0.1,
        n_layer=3,
        extrude_dir="inside",
        average_normals=True,
    )

    # Check the created volume.
    assert 0.1924264068711928 == pytest.approx(
        cubit.get_meshed_volume_or_area("volume", [volume.id()]), 1e-10
    )

    # Set the mesh for output.
    cubit.add_element_type(volume, cupy.element_type.hex8)

    # Compare the input file created for 4C.
    compare_yaml(cubit)


def test_extrude_mesh_function_average_normals_for_cylinder_and_sphere():
    """Test the average extrude mesh function for curved surfaces (Toy Aneurysm
    Case)."""

    # Initialize cubit.
    cubit = CubitPy()

    # Offset between center of cylinder and sphere.
    offset = 0.8

    # create cylinder and sphere for a toy aneurysm.
    cubit.cmd("create Cylinder height 1 radius 0.5")
    cubit.cmd("create sphere radius 0.4")
    cubit.cmd(f"move volume 2 x 0 y {offset}")

    # Cut volumes into quarter parts.
    cubit.cmd("webcut volume all with general plane xy noimprint nomerge")
    cubit.cmd("webcut volume all with general plane yz noimprint nomerge")
    cubit.cmd("webcut volume all with general plane xz noimprint nomerge")
    cubit.cmd(
        f"webcut volume all with general plane xz offset -{offset}  noimprint nomerge "
    )

    # Unit one quarter of the cylinder and sphere.
    cubit.cmd("unite volume 12 8")

    # Create surface mesh.
    extrude_surface_ids = [115, 113]
    extrude_surface_ids_string = " ".join(map(str, extrude_surface_ids))
    cubit.cmd("surface {} size auto factor 7".format(extrude_surface_ids_string))
    cubit.cmd("mesh surface {}".format(extrude_surface_ids_string))

    # Extrude the surfaces.
    volume = extrude_mesh_normal_to_surface(
        cubit,
        [cubit.surface(i) for i in extrude_surface_ids],
        0.05,
        n_layer=1,
        extrude_dir="outside",
        average_normals=True,
    )

    # Check the size of the created volume.
    if cupy.is_coreform():
        ref_volume = 0.026753602587277842
    else:
        ref_volume = 0.02668549643643842
    assert ref_volume == pytest.approx(
        cubit.get_meshed_volume_or_area("volume", [volume.id()]), 1e-10
    )

    # Set the mesh for output.
    cubit.add_element_type(volume, cupy.element_type.hex8)

    # Compare the input file created for 4C.
    # Since this meshes slightly different on different Cubit versions, we need
    # a "loose" tolerance here.
    compare_yaml(cubit, rtol=1e-8, atol=1e-8)


def test_node_set_geometry_type():
    """Create the boundary conditions via the bc_type enum."""

    # First create the solid mesh.
    cubit = CubitPy()
    solid = create_brick(cubit, 1, 1, 1, mesh_interval=[1, 1, 1])

    # Add all possible boundary conditions.

    # Dirichlet and Neumann.
    cubit.add_node_set(
        solid.vertices()[0],
        name="vertex",
        bc_type=cupy.bc_type.dirichlet,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [1, 1, 1],
            "VAL": [0, 0, 0],
            "FUNCT": [0, 0, 1],
        },
    )
    cubit.add_node_set(
        solid.curves()[0],
        name="curve",
        bc_type=cupy.bc_type.neumann,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [1, 1, 1],
            "VAL": [0, 0, 0],
            "FUNCT": [0, 0, 2],
        },
    )
    cubit.add_node_set(
        solid.surfaces()[0],
        name="surface",
        bc_type=cupy.bc_type.dirichlet,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [1, 1, 1],
            "VAL": [0, 0, 0],
            "FUNCT": [0, 0, 3],
        },
    )
    cubit.add_node_set(
        solid.volumes()[0],
        name="volume",
        bc_type=cupy.bc_type.neumann,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [1, 1, 1],
            "VAL": [0, 0, 0],
            "FUNCT": [0, 0, 4],
        },
    )

    # Define boundary conditions on explicit nodes.
    cubit.add_node_set(
        cubit.group(add_value="add node 2"),
        name="point2",
        geometry_type=cupy.geometry.vertex,
        bc_type=cupy.bc_type.neumann,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [1, 1, 1],
            "VAL": [0, 0, 0],
            "FUNCT": [0, 0, 4],
        },
    )
    cubit.add_node_set(
        cubit.group(
            add_value="add node {}".format(
                " ".join([str(i + 1) for i in range(cubit.get_node_count())])
            )
        ),
        name="point3",
        geometry_type=cupy.geometry.vertex,
        bc_type=cupy.bc_type.neumann,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [1, 1, 1],
            "VAL": [0, 0, 0],
            "FUNCT": [0, 0, 4],
        },
    )

    # Coupling.
    cubit.add_node_set(
        solid.volumes()[0],
        name="coupling_btsv",
        bc_type=cupy.bc_type.beam_to_solid_volume_meshtying,
        bc_description={"COUPLING_ID": 1},
    )
    cubit.add_node_set(
        solid.surfaces()[0],
        name="coupling_btss",
        bc_type=cupy.bc_type.beam_to_solid_surface_meshtying,
        bc_description={"COUPLING_ID": 1},
    )

    cubit.fourc_input["MATERIALS"] = [
        {
            "MAT": 1,
            "MAT_Struct_StVenantKirchhoff": {
                "YOUNG": 10,
                "NUE": 0.0,
                "DENS": 0.0,
            },
        }
    ]

    # Compare the input file created for 4C.
    compare_yaml(cubit)


def test_contact_condition_beam_to_surface():
    """Test the beam-to-surface contact condition BC."""
    cubit = CubitPy()

    # Create the mesh.
    solid = create_brick(cubit, 1, 1, 1, mesh_interval=[1, 1, 1])
    solid2 = create_brick(cubit, 1, 1, 1, mesh_interval=[1, 1, 1])
    cubit.move(solid2, [-1, 0, 0])

    # Test contact conditions
    cubit.add_node_set(
        solid.surfaces()[0],
        name="block1_contact_side",
        bc_type=cupy.bc_type.beam_to_solid_surface_contact,
        bc_description={"COUPLING_ID": 1},
    )

    # Compare the input file created for 4C.
    compare_yaml(cubit)


def test_contact_condition_curve_to_curve():
    """Test the curve-to-curve contact condition BC."""
    cubit = CubitPy()

    # Create and mesh two rectangles
    cubit.cmd("create surface rectangle width 1 height 1 zplane")
    solid1 = cubit.surface(cubit.get_last_id(cupy.geometry.surface))
    cubit.cmd(f"surface {solid1.id()} size 1")
    cubit.cmd("create surface rectangle width 2 height 1 zplane")
    solid2 = cubit.surface(cubit.get_last_id(cupy.geometry.surface))
    cubit.cmd(f"move surface {solid2.id()} x 0 y -1 z 0 include_merged")
    cubit.cmd(f"surface {solid2.id()} size 1")
    cubit.cmd("mesh surface all")

    # Add elements
    bc_desc = {
        "KINEM": "nonlinear",
        "EAS": None,
        "THICK": 1,
        "STRESS_STRAIN": "plain_strain",
        "GP": [2, 2],
    }
    cubit.add_element_type(
        solid1.surfaces()[0],
        el_type=cupy.element_type.quad4,
        bc_description=bc_desc,
    )
    cubit.add_element_type(
        solid2.surfaces()[0],
        el_type=cupy.element_type.quad4,
        bc_description=bc_desc,
    )

    # Test contact conditions
    cubit.add_node_set(
        solid1.curves()[2],
        name="block1_contact_side",
        bc_type=cupy.bc_type.solid_to_solid_contact,
        bc_description={"InterfaceID": 0, "Side": "Master"},
    )
    cubit.add_node_set(
        solid2.curves()[0],
        name="block2_contact_side",
        bc_type=cupy.bc_type.solid_to_solid_contact,
        bc_description={"InterfaceID": 0, "Side": "Slave"},
    )

    # Compare the input file created for 4C.
    compare_yaml(cubit)


def test_contact_condition_surface_to_surface():
    """Test the surface-to-surface contact condition BC."""
    cubit = CubitPy()

    # Create the mesh.
    solid = create_brick(cubit, 1, 1, 1, mesh_interval=[1, 1, 1])
    solid2 = create_brick(cubit, 1, 1, 1, mesh_interval=[1, 1, 1])
    cubit.move(solid2, [-1, 0, 0])

    # Test contact conditions
    cubit.add_node_set(
        solid.surfaces()[0],
        name="block1_contact_side",
        bc_type=cupy.bc_type.solid_to_solid_surface_contact,
        bc_description={"InterfaceID": 0, "Side": "Master"},
    )
    cubit.add_node_set(
        solid2.surfaces()[3],
        name="block2_contact_side",
        bc_type=cupy.bc_type.solid_to_solid_contact,
        bc_description={"InterfaceID": 0, "Side": "Slave"},
    )

    # Compare the input file created for 4C.
    compare_yaml(cubit)


@pytest.mark.xfail(
    reason="This test fails due to mismatching results on macOS and Linux"
)
def test_fluid_functionality():
    """Test fluid conditions and fluid mesh creation."""

    cubit = CubitPy()
    fluid = create_brick(
        cubit,
        1,
        1,
        1,
        mesh_interval=[1, 1, 1],
        element_type=cupy.element_type.tet4_fluid,
    )

    # add inflowrate
    cubit.add_node_set(
        fluid.surfaces()[0],
        name="inflowrate",
        bc_type=cupy.bc_type.flow_rate,
        bc_description={"ConditionID": 1},
    )

    cubit.add_node_set(
        fluid.surfaces()[1],
        name="inflow_stabilization",
        bc_type=cupy.bc_type.fluid_neumann_inflow_stab,
        bc_description={},
    )

    # Compare the input file created for 4C.
    compare_yaml(cubit, additional_identifier=CUBIT_VERSION_TESTING_IDENTIFIER)


def test_thermo_functionality():
    """Test thermo mesh creation."""

    cubit = CubitPy()
    create_brick(
        cubit,
        1,
        1,
        1,
        mesh_interval=[1, 1, 1],
        element_type=cupy.element_type.hex8_thermo,
    )

    # Compare the input file created for 4C.
    compare_yaml(cubit)


def test_scatra_functionality():
    """Test scatra mesh creation."""

    cubit = CubitPy()
    thermo = create_brick(
        cubit,
        1,
        1,
        1,
        mesh_interval=[1, 1, 1],
        element_type=cupy.element_type.hex8_scatra,
    )

    # Compare the input file created for 4C.
    compare_yaml(cubit)


def test_fsi_functionality():
    """Test fsi and ale conditions and fluid mesh creation."""

    cubit = CubitPy()

    # Create solif and fluid meshes
    solid = create_brick(cubit, 1, 1, 1, mesh_interval=[1, 1, 1])
    fluid = create_brick(
        cubit,
        1,
        1,
        1,
        mesh_interval=[1, 1, 1],
        element_type=cupy.element_type.hex8_fluid,
    )
    cubit.move(fluid, [1, 0, 0])

    # Test FSI and ALE conditions
    cubit.add_node_set(
        fluid.surfaces()[0],
        name="fsi_fluid_side",
        bc_type=cupy.bc_type.fsi_coupling,
        bc_description={"coupling_id": 1},
    )
    cubit.add_node_set(
        solid.surfaces()[3],
        name="fsi_solid_side",
        bc_type=cupy.bc_type.fsi_coupling,
        bc_description={"coupling_id": 1},
    )
    cubit.add_node_set(
        fluid.surfaces()[3],
        name="ale_dirichlet_side",
        bc_type=cupy.bc_type.ale_dirichlet,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [1, 1, 1],
            "VAL": [0, 0, 0],
            "FUNCT": [0, 0, 0],
        },
    )

    # Compare the input file created for 4C.
    compare_yaml(cubit)


def test_point_coupling():
    """Create node-node and vertex-vertex coupling."""

    # First create two blocks.
    cubit = CubitPy()
    solid_1 = create_brick(cubit, 1, 1, 1, mesh_interval=[2, 2, 2], mesh=False)
    cubit.move(solid_1, [0.0, -0.5, 0.0])
    solid_2 = create_brick(cubit, 1, 2, 1, mesh_interval=[2, 4, 2], mesh=False)
    cubit.move(solid_2, [0.0, 1.0, 0.0])

    # Mesh the blocks.
    solid_1.mesh()
    solid_2.mesh()

    # Couple all nodes on the two surfaces. Therefore we first have to get
    # the surfaces of the two blocks that are at the interface.
    surfaces = cubit.group(name="interface_surfaces")
    surfaces.add("add surface with -0.1 < y_coord and y_coord < 0.1")

    # Check each node with each other node. If they are at the same
    # position, add a coupling.
    surf = surfaces.get_geometry_objects(cupy.geometry.surface)

    # Sort the node IDs, by doing so the results are independent of the ordering
    # of the node IDs returned by cubit (which can change between versions).
    node_ids_1 = surf[0].get_node_ids()
    node_ids_1.sort()
    node_ids_2 = surf[1].get_node_ids()
    node_ids_2.sort()

    for node_id_1 in node_ids_1:
        coordinates_1 = np.array(cubit.get_nodal_coordinates(node_id_1))
        for node_id_2 in surf[1].get_node_ids():
            coordinates_2 = cubit.get_nodal_coordinates(node_id_2)
            if np.linalg.norm(coordinates_2 - coordinates_1) < cupy.eps_pos:
                cubit.add_node_set(
                    cubit.group(
                        add_value="add node {} {}".format(node_id_1, node_id_2)
                    ),
                    geometry_type=cupy.geometry.vertex,
                    bc_type=cupy.bc_type.point_coupling,
                    bc_description={
                        "NUMDOF": 3,
                        "ONOFF": [1, 1, 1],
                    },
                )

    # Also add coupling explicitly to the on corners.
    for point_1 in solid_1.vertices():
        coordinates_1 = np.array(point_1.coordinates())
        for point_2 in solid_2.vertices():
            coordinates_2 = np.array(point_2.coordinates())
            if np.linalg.norm(coordinates_2 - coordinates_1) < cupy.eps_pos:
                # Here a group has to be created.
                group = cubit.group()
                group.add([point_1, point_2])
                cubit.add_node_set(
                    group,
                    bc_type=cupy.bc_type.point_coupling,
                    bc_description={
                        "NUMDOF": 3,
                        "ONOFF": [1, 2, 3],
                    },
                )

    # Compare the input file created for 4C.
    compare_yaml(cubit)


def test_group_of_surfaces():
    """Test the proper creation of a group of surfaces and assign them an
    element type."""
    cubit = CubitPy()

    # create a rectangle and imprint it
    cubit.cmd("create surface rectangle width 1 height 2 zplane")
    cubit.cmd("create curve location -0.5 0 0  location 0.5 0 0")
    cubit.cmd("imprint tolerant surface 1 with curve 5 merge")

    # define mesh size
    cubit.cmd("surface all size 0.3")

    # create mesh
    cubit.cmd("mesh surface all")

    # create group and assign element type
    surfaces = cubit.group(add_value="add surface 2 3")

    cubit.add_element_type(
        surfaces,
        cupy.element_type.quad4,
        name="mesh",
        material={"MAT": 1},
        bc_description={
            "KINEM": "linear",
            "EAS": "none",
            "THICK": 1.0,
            "STRESS_STRAIN": "plane_strain",
            "GP": [3, 3],
        },
    )

    # Compare the input file created for 4C.
    compare_yaml(cubit)


@pytest.mark.parametrize("group_with", ["volume", "hex"])
def test_groups(group_with):
    """Test that groups are handled correctly when creating node sets and
    element blocks.

    Args
    ----
    group_with: str
        If the element block should be added via a group containing the
        geometry volume or via a group containing the hex elements.
    """

    if not group_with == "volume" and not group_with == "hex":
        raise ValueError(f"Got unexpected argument group_with {group_with}")

    # Create a solid brick.
    cubit = CubitPy()
    cubit.brick(4, 2, 1)

    # Add to group by string.
    volume = cubit.group(name="all_vol")
    volume.add("add volume all")

    # Add to group via string.
    surface_fix = cubit.group(
        name="fix_surf",
        add_value="add surface in volume in all_vol with x_coord < 0",
    )
    surface_load = cubit.group(
        name="load_surf",
        add_value="add surface in volume in all_vol with x_coord > -1.99",
    )

    # Add to group by CubitPy object.
    surface_load_alt = cubit.group(name="load_surf_alt")
    surface_load_alt.add(cubit.surface(1))
    surface_load_alt.add([cubit.surface(i) for i in [2, 3, 5, 6]])

    # Create a group without a name.
    group_no_name = cubit.group()
    group_no_name.add("add surface in volume in all_vol with x_coord < 0")

    # Create a group without a name.
    group_explicit_type = cubit.group()
    group_explicit_type.add("add surface 2")
    group_explicit_type.add("add curve 1")
    group_explicit_type.add("add vertex 3")

    if group_with == "volume":
        # Set the element block and use a user defined element description
        cubit.add_element_type(
            volume,
            cupy.element_type.hex8,
            material={"MAT": 1},
            bc_description={"KINEM": "linear"},
        )

    # Add BCs.
    cubit.add_node_set(
        surface_fix,
        bc_type=cupy.bc_type.dirichlet,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [1, 1, 1],
            "VAL": [0, 0, 0],
            "FUNCT": [0, 0, 0],
        },
    )

    cubit.add_node_set(
        surface_load,
        bc_type=cupy.bc_type.neumann,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [0, 0, 1],
            "VAL": [0, 0, 1],
            "FUNCT": [0, 0, 0],
        },
    )
    cubit.add_node_set(
        surface_load_alt,
        bc_type=cupy.bc_type.neumann,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [0, 0, 1],
            "VAL": [0, 0, 1],
            "FUNCT": [0, 0, 0],
        },
    )
    cubit.add_node_set(
        group_no_name,
        name="fix_surf_no_name_group",
        bc_type=cupy.bc_type.dirichlet,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [1, 1, 1],
            "VAL": [0, 0, 0],
            "FUNCT": [0, 0, 0],
        },
    )
    cubit.add_node_set(
        group_explicit_type,
        name="fix_group_explicit_type",
        geometry_type=cupy.geometry.vertex,
        bc_type=cupy.bc_type.dirichlet,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [1, 1, 1],
            "VAL": [0, 0, 0],
            "FUNCT": [0, 0, 0],
        },
    )

    # Mesh the model.
    cubit.cmd("volume {} size auto factor 8".format(volume.id()))
    cubit.cmd("mesh {}".format(volume))

    if group_with == "hex":
        # Set the element block and use a user defined element description
        all_hex = cubit.group(add_value="add hex all")
        cubit.add_element_type(
            all_hex,
            cupy.element_type.hex8,
            material={"MAT": 1},
            bc_description={"KINEM": "linear"},
        )

    # Add a group containing elements and nodes.
    mesh_group = cubit.group(name="mesh_group")
    mesh_group.add("add node 1 4 18 58 63")
    mesh_group.add("add face 69")
    mesh_group.add("add hex 17")
    cubit.add_node_set(
        mesh_group,
        geometry_type=cupy.geometry.vertex,
        bc_type=cupy.bc_type.dirichlet,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [1, 1, 1],
            "VAL": [0, 0, 0],
            "FUNCT": [0, 0, 0],
        },
    )

    cubit.fourc_input["MATERIALS"] = [
        {
            "MAT": 1,
            "MAT_Struct_StVenantKirchhoff": {
                "YOUNG": 10,
                "NUE": 0.0,
                "DENS": 0.0,
            },
        }
    ]

    # Compare the input file created for 4C.
    compare_yaml(cubit)


@pytest.mark.parametrize("group_get_by", [None, "name", "id"])
def test_groups_multiple_sets(group_get_by):
    """Test that multiple sets can be created from a single group object.

    Also test that a group can be obtained by name and id.
    """

    # Create a solid brick.
    cubit = CubitPy()
    cubit.brick(4, 2, 1)

    # Add to group by string.
    volume = cubit.group(name="all_vol")
    volume.add("add volume all")

    # Get group.
    if group_get_by is not None:
        volume_old = volume
        if group_get_by == "name":
            volume = cubit.group(group_from_name=volume_old.name)
        elif group_get_by == "id":
            volume = cubit.group(group_from_id=volume_old._id)
        else:
            raise ValueError(f"Got unexpected value for group_get_by {group_get_by}")
        assert volume._id == volume_old._id
        assert volume.name == volume_old.name

    # Add BCs.
    cubit.add_node_set(
        volume,
        bc_type=cupy.bc_type.dirichlet,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [1, 1, 1],
            "VAL": [0, 0, 0],
            "FUNCT": [0, 0, 0],
        },
    )
    cubit.add_node_set(
        volume,
        bc_type=cupy.bc_type.neumann,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [0, 0, 1],
            "VAL": [0, 0, 1],
            "FUNCT": [0, 0, 0],
        },
    )

    # Add blocks.
    cubit.add_element_type(volume, cupy.element_type.hex8)

    # Mesh the model.
    cubit.cmd("volume {} size auto factor 8".format(volume.id()))
    cubit.cmd("mesh {}".format(volume))

    cubit.fourc_input["MATERIALS"] = [
        {
            "MAT": 1,
            "MAT_Struct_StVenantKirchhoff": {
                "YOUNG": 10.0,
                "NUE": 0.0,
                "DENS": 0.0,
            },
        }
    ]
    # Compare the input file created for 4C.
    compare_yaml(cubit)


def test_reset_block():
    """Test that the block counter can be reset in cubit."""

    # Create a solid brick.
    cubit = CubitPy()
    block_1 = cubit.brick(1, 1, 1)
    block_2 = cubit.brick(2, 0.5, 0.5)
    cubit.cmd("volume 1 size auto factor 10")
    cubit.cmd("volume 2 size auto factor 10")
    cubit.cmd("mesh volume 1")
    cubit.cmd("mesh volume 2")

    cubit.add_element_type(block_1.volumes()[0], cupy.element_type.hex8)
    compare_yaml(cubit, additional_identifier="1")

    cubit.reset_blocks()
    cubit.add_element_type(block_2.volumes()[0], cupy.element_type.hex8)
    compare_yaml(cubit, additional_identifier="2")


def test_get_id_functions():
    """Test if the get_ids and get_items methods work as expected."""

    cubit = CubitPy()

    cubit.cmd("create vertex 0 0 0")
    cubit.cmd("create curve location 0 0 0 location 1 1 1")
    cubit.cmd("create surface circle radius 1 zplane")
    cubit.cmd("brick x 1")

    assert [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] == cubit.get_ids(
        cupy.geometry.vertex
    )
    assert [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] == cubit.get_ids(
        cupy.geometry.curve
    )
    assert [1, 2, 3, 4, 5, 6, 7] == cubit.get_ids(cupy.geometry.surface)
    if cupy.is_coreform():
        ref_ids = [1, 2]
        assert [1, 2] == cubit.get_ids(cupy.geometry.volume)
    else:
        ref_ids = [2]
    assert ref_ids == cubit.get_ids(cupy.geometry.volume)


def test_get_node_id_function():
    """Test if the get_node_ids methods in the cubit objects work as
    expected."""

    # Create brick.
    cubit = CubitPy()
    brick = create_brick(cubit, 1, 1, 1, mesh_interval=[2, 2, 2])

    # Compare volume, surface, curve and vertex nodes.
    node_ids = brick.volumes()[0].get_node_ids()
    node_ids.sort()
    assert node_ids == list(range(1, 28))

    node_ids = brick.surfaces()[3].get_node_ids()
    node_ids.sort()
    assert node_ids == [4, 6, 7, 13, 15, 16, 19, 22, 23]

    node_ids = brick.curves()[4].get_node_ids()
    node_ids.sort()
    assert node_ids == [10, 11, 12]

    node_ids = brick.vertices()[7].get_node_ids()
    node_ids.sort()
    assert node_ids == [15]


def test_serialize_nested_lists():
    """Test that nested lists can be send to cubit correctly."""

    cubit = CubitPy()
    block_1 = cubit.brick(1, 1, 0.25)
    block_2 = cubit.brick(0.5, 0.5, 0.5)
    subtracted_block = cubit.subtract([block_2], [block_1])
    cubit.cmd(
        "volume {} size auto factor 9".format(subtracted_block[0].volumes()[0].id())
    )
    subtracted_block[0].volumes()[0].mesh()
    cubit.add_element_type(subtracted_block[0].volumes()[0], cupy.element_type.hex8)
    compare_yaml(cubit)


def test_serialize_geometry_types():
    """Test that geometry types can be send to cubit correctly."""

    cubit = CubitPy()

    cubit.cmd("create vertex -1 -1 -1")
    cubit.cmd("create vertex 1 2 3")
    geo_id = cubit.get_last_id(cupy.geometry.vertex)
    bounding_box = cubit.get_bounding_box(cupy.geometry.vertex, geo_id)
    bounding_box_ref = np.array([1.0, 1.0, 0.0, 2.0, 2.0, 0.0, 3.0, 3.0, 0.0, 0.0])
    assert 0.0 == pytest.approx(np.linalg.norm(bounding_box - bounding_box_ref), 1e-10)

    cubit.cmd("create curve vertex 1 2")
    geo_id = cubit.get_last_id(cupy.geometry.curve)
    bounding_box = cubit.get_bounding_box(cupy.geometry.curve, geo_id)
    bounding_box_ref = np.array(
        [-1.0, 1.0, 2.0, -1.0, 2.0, 3.0, -1.0, 3.0, 4.0, 5.385164807134504]
    )
    assert 0.0 == pytest.approx(np.linalg.norm(bounding_box - bounding_box_ref), 1e-10)


def test_mesh_import():
    """Test that the cubit class MeshImport works properly.

    Code mainly taken from:
    https://cubit.sandia.gov/public/13.2/help_manual/WebHelp/appendix/python/class_mesh_import.htm
    """

    cubit = CubitPy()
    mi = cubit.MeshImport()
    mi.add_nodes(
        3,
        8,
        [0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0],
    )
    mi.add_elements(cubit.HEX, 1, [1, 2, 3, 4, 5, 6, 7, 8])

    element_group = cubit.group(add_value="add HEX 1")
    cubit.add_element_type(element_group, cupy.element_type.hex8)

    compare_yaml(cubit)


def test_display_in_cubit():
    """Call the display_in_cubit function without actually opening the graphic
    version of cubit.

    Compare that the created journal file is correct.
    """

    # Create brick.
    cubit = CubitPy()
    create_brick(cubit, 1, 1, 1, mesh_interval=[2, 2, 2])

    # Check the journal file which is created in the display_in_cubit
    # function.
    journal_path = cubit.display_in_cubit(
        labels=[
            cupy.geometry.vertex,
            cupy.geometry.curve,
            cupy.geometry.surface,
            cupy.geometry.volume,
            cupy.finite_element_object.node,
            cupy.finite_element_object.edge,
            cupy.finite_element_object.face,
            cupy.finite_element_object.triangle,
            cupy.finite_element_object.hex,
            cupy.finite_element_object.tet,
        ],
        testing=True,
    )
    with open(journal_path, "r") as journal:
        journal_text = journal.read()
    if cupy.is_coreform():
        state_name = "state.cub5"
    else:
        state_name = "state.cub"
    ref_text = (
        f'open "{cupy.temp_dir}/{state_name}"\n'
        "label volume On\n"
        "label surface On\n"
        "label curve On\n"
        "label vertex On\n"
        "label hex On\n"
        "label tet On\n"
        "label face On\n"
        "label tri On\n"
        "label edge On\n"
        "label node On\n"
        "display"
    )
    assert journal_text.strip() == ref_text.strip()


def test_create_parametric_surface():
    """Test the create_parametric_surface function."""

    cubit = CubitPy()

    def f(u, v, arg, kwarg=-1.0):
        """Parametric function to create the curve."""
        return [u, v, arg * np.sin(u) + kwarg * np.cos(v)]

    surface = create_parametric_surface(
        cubit,
        f,
        [[-1, 1], [-1, 1]],
        n_segments=[3, 2],
        function_args=[2.1],
        function_kwargs={"kwarg": 1.2},
    )

    cubit.cmd("surface {} size auto factor 9".format(surface.id()))
    surface.mesh()

    coordinates = [
        cubit.get_nodal_coordinates(i + 1) for i in range(cubit.get_node_count())
    ]
    connectivity = [
        cubit.get_connectivity("quad", i + 1) for i in range(cubit.get_quad_count())
    ]

    # fmt: off
    coordinates_ref = np.array([
        [-1.0, -1.0, -1.118726301054815],
        [-1.0, 1.0, -1.118726301054815],
        [-1.0, 0.0, -0.5670890680965828],
        [1.0, 1.0, 2.4154518351383505],
        [-0.29336121659426423, 1.0, 0.037372888869339725],
        [0.2933612165942643, 1.0, 1.2593526452141954],
        [1.0, -1.0, 2.4154518351383505],
        [1.0, 0.0, 2.9670890680965822],
        [-0.29336121659426406, -1.0, 0.03737288886933997],
        [0.2933612165942643, -1.0, 1.2593526452141954],
        [-0.29336121659426406, -8.872129520034311e-17, 0.5890101218275721],
        [0.2933612165942643, 8.060694322846754e-19, 1.810989878172428]
        ])

    connectivity_ref = np.array([[ 1,  3, 11,  9],
            [ 3,  2,  5, 11],
            [ 9, 11, 12, 10],
            [11,  5,  6, 12],
            [10, 12,  8,  7],
            [12,  6,  4,  8]])
    # fmt: on

    assert 0.0 == pytest.approx(np.linalg.norm(coordinates - coordinates_ref), 1e-12)
    assert np.linalg.norm(connectivity - connectivity_ref) == 0


def test_spline_interpolation_curve():
    """Test the create_spline_interpolation_curve function."""

    cubit = CubitPy()

    x = np.linspace(0, 2 * np.pi, 7)
    y = np.cos(x)
    z = np.sin(x)
    vertices = np.array([x, y, z]).transpose()

    curve = create_spline_interpolation_curve(cubit, vertices)
    curve.mesh()

    coordinates = [
        cubit.get_nodal_coordinates(i + 1) for i in range(cubit.get_node_count())
    ]
    connectivity = [
        cubit.get_connectivity("edge", i + 1) for i in range(cubit.get_edge_count())
    ]

    # fmt: off
    coordinates_ref = np.array([
        [0.0, 1.0, 0.0],
        [6.283185307179586, 1.0, -2.4492935982947064e-16],
        [0.6219064247387815, 0.7622034923056742, 0.5808964193893371],
        [1.2706376409420117, 0.30926608007524203, 0.9532391827102926],
        [1.8922964421051867, -0.3108980458371118, 0.946952808381383],
        [2.5151234800888007, -0.8099976142632724, 0.5846200862869367],
        [3.1415926535897927, -0.9999999999999998, 1.6653345369377348e-16],
        [3.7680618270907873, -0.8099976142632712, -0.5846200862869384],
        [4.3908888650744, -0.31089804583711017, -0.9469528083813835],
        [5.012547666237575, 0.30926608007524364, -0.9532391827102922],
        [5.661278882440805, 0.7622034923056742, -0.5808964193893369]
    ])

    connectivity_ref = np.array([[1, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8], [8, 9], [9, 10],
        [10, 11], [11, 2]])
    # fmt: on

    assert 0.0 == pytest.approx(np.linalg.norm(coordinates - coordinates_ref), 1e-12)
    assert np.linalg.norm(connectivity - connectivity_ref) == 0


def test_create_brick_by_corner_points():
    """Test the create_brick_by_corner_points and create_surface_by_vertices
    functions."""

    # Set up Cubit.
    cubit = CubitPy()

    # Create the brick
    corner_points = np.array(
        [
            [0, 0, 0],
            [0, 0, 1],
            [0, 2, 1],
            [0, 1, 0],
            [1, 0, 0],
            [1, 0, 1],
            [1, 1, 1],
            [1, 1, 0],
        ],
        dtype=float,
    )
    # Rotation matrix for the rotation angle 0.1 * np.pi around the axis [1, 2, 3]
    rotation_matrix = [
        [0.9545524794169283, -0.24077287082252985, 0.17566442074271046],
        [0.25475672330962884, 0.9650403687822526, -0.06161248695804464],
        [-0.15468864201206198, 0.10356404441934158, 0.9825201843911263],
    ]
    corner_points = np.array(
        [np.dot(rotation_matrix, point) for point in corner_points]
    )
    brick = create_brick_by_corner_points(cubit, corner_points)
    cubit.cmd(f"volume {brick.id()} size auto factor 9")
    brick.mesh()
    cubit.add_element_type(brick, cupy.element_type.hex8)
    compare_yaml(cubit)


def setup_and_check_import_fluent_geometry(
    fluent_geometry, feature_angle, reference_entities_number
):
    """
    Test if cubit can import a geometry and:
        1) proceed without error
        2) has created the same number of the reference entities [volumes, surfaces, blocks]
    """

    # Setup
    cubit = CubitPy()
    import_fluent_geometry(cubit, fluent_geometry, feature_angle)

    # check if importation was successful
    assert not cubit.was_last_cmd_undoable()

    # check number of entities
    assert cubit.get_volume_count() == reference_entities_number[0]
    assert len(cubit.get_entities("surface")) == reference_entities_number[1]
    assert cubit.get_block_count() == reference_entities_number[2]


def test_import_fluent_geometry():
    """Test if an aneurysm geometry can be imported from a fluent mesh."""

    fluent_geometry = os.path.join(testing_external_geometry, "fluent_aneurysm.msh")

    # for a feature angle of 135, the imported geometry should consist of 1 volume, 7 surfaces and 1 block
    setup_and_check_import_fluent_geometry(fluent_geometry, 135, [1, 7, 1])

    # for a feature angle of 100, the imported geometry should consist of 1 volume, 4 surfaces and 1 block
    setup_and_check_import_fluent_geometry(fluent_geometry, 100, [1, 4, 1])


@pytest.mark.xfail(
    reason="This test fails due to mismatching results on macOS and Linux"
)
def test_extrude_artery_of_aneurysm():
    """Extrude an arterial surface based on an aneurysm test case."""

    # Set up Cubit.
    cubit = CubitPy()

    # Set path for geometry.
    fluent_geometry = os.path.join(testing_external_geometry, "fluent_aneurysm.msh")

    # Import aneruysm geometry to cubit.
    import_fluent_geometry(cubit, fluent_geometry, 100)

    # Select wall surface for this case.
    wall_id = [3]

    # Remesh the artery surface with hex elements.
    cubit.cmd("delete mesh")
    cubit.cmd("mesh surface {}".format(wall_id[0]))

    # Extrude the surface.
    volume = extrude_mesh_normal_to_surface(
        cubit,
        [cubit.surface(wall_id[0])],
        0.1,
        n_layer=2,
        extrude_dir="outside",
    )

    # Check the created volume.
    if cupy.is_coreform():
        ref_volume = 13.614146346307278
    else:
        ref_volume = 13.570135865871498
    assert ref_volume == pytest.approx(
        cubit.get_meshed_volume_or_area("volume", [volume.id()]), 1e-5
    )


def test_yaml_with_exo_export():
    """Test if exporting a yaml file with an exodus mesh works."""
    # Set up Cubit.
    cubit = CubitPy()

    # Initialize geometry
    cubit.cmd("brick x 1 y 1 z 1")
    cubit.cmd("brick x 5e-1 y 5e-1 z 5e-1")
    cubit.cmd("move Volume 2 x 75e-2 y 0 z 0")
    cubit.cmd("volume 1 size {1e-1}")
    cubit.cmd("volume 2 size {1e-1}")

    # mesh the two geometries
    cubit.cmd("mesh volume 1")
    cubit.cmd("mesh volume 2")

    # Assign nodesets, required for boundary conditions
    cubit.add_node_set(
        cubit.group(add_value="add surface 6"),
        name="slave",
        bc_type=cupy.bc_type.solid_to_solid_contact,
        bc_description={
            "InterfaceID": 1,
            "Side": "Slave",
        },
    )
    cubit.add_node_set(
        cubit.group(add_value="add surface 10"),
        name="master",
        bc_type=cupy.bc_type.solid_to_solid_contact,
        bc_description={
            "InterfaceID": 1,
            "Side": "Master",
        },
    )
    cubit.add_node_set(
        cubit.group(add_value="add surface 4"),
        name="wall",
        bc_type=cupy.bc_type.dirichlet,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [1, 1, 1],
            "VAL": [0, 0, 0],
            "FUNCT": [None, None, None],
        },
        node_set_id=17,
    )
    cubit.add_node_set(
        cubit.group(add_value="add surface 12"),
        name="pushing",
        bc_type=cupy.bc_type.dirichlet,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [1, 0, 0],
            "VAL": [-1.0, 0.0, 0.0],
            "FUNCT": [1, None, None],
        },
    )

    cubit.add_node_set(
        cubit.group(add_value="add curve 1"),
        name="curve_1",
        bc_type=cupy.bc_type.neumann,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [1, 0, 0],
            "VAL": [1.0, 0.0, 0.0],
            "FUNCT": [None, None, None],
        },
    )
    cubit.add_node_set(
        cubit.group(add_value="add curve 2"),
        name="curve_2",
        bc_type=cupy.bc_type.neumann,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [1, 0, 0],
            "VAL": [1.0, 0.0, 0.0],
            "FUNCT": [None, None, None],
        },
    )
    cubit.add_node_set(
        cubit.group(add_value="add curve 3"),
        name="curve_3",
        bc_type=cupy.bc_type.neumann,
        bc_description={
            "NUMDOF": 3,
            "ONOFF": [1, 1, 0],
            "VAL": [1.0, 0.0, 0.0],
            "FUNCT": [None, None, None],
        },
        node_set_id=15,
    )

    # Add the element types
    cubit.add_element_type(
        cubit.group(add_value="add volume 1"),
        el_type=cupy.element_type.hex8,
        material={
            "MAT": 1,
        },
        bc_description={
            "KINEM": "nonlinear",
        },
    )
    cubit.add_element_type(
        cubit.group(add_value="add volume 2"),
        el_type=cupy.element_type.hex8,
        material={
            "MAT": 2,
        },
        bc_description={
            "KINEM": "nonlinear",
        },
        block_id=27,
    )

    cubit.fourc_input.combine_sections(
        {
            "PROBLEM SIZE": {"DIM": 3},
            "PROBLEM TYPE": {"PROBLEMTYPE": "Structure"},
        }
    )

    # Compare the input file created for 4C.
    compare_yaml(cubit, mesh_in_exo=True)


def test_yaml_with_exo_export_fsi():
    """Test if exporting a yaml file with an exodus mesh works, even in fsi
    cases, where GEOMETRY sections for fluid and solid domains need to be
    exported."""
    ##############
    # PARAMETERS #
    ##############

    Depth = 0.05
    Width = 1.0
    BottomHeight = 0.002
    CavityHeight = 1.0
    InflowHeight = 0.1
    MeshDepth = 1
    MeshWidth = 32
    MeshBottomHeight = 1
    MeshCavityHeight = 32
    MeshInflowHeight = 7

    cubit = CubitPy()

    ############
    # GEOMETRY #
    ############

    # Create Bottom
    cubit.cmd(f"brick x {Width} y {BottomHeight} z {Depth}")
    cubit.cmd(f"volume 1 move x {Width / 2} y {-BottomHeight / 2} z {-Depth / 2}")

    # Create Fluid Part
    cubit.cmd(f"brick x {Width} y {CavityHeight + InflowHeight} z {Depth}")
    cubit.cmd("align volume 2 surface 9 with surface 5")
    # $ divide cavity and inflow region
    cubit.cmd(f"webcut volume 2 with plane yplane offset {CavityHeight} imprint merge")

    ###########
    # MESHING #
    ###########

    # Mesh Bottom
    cubit.cmd(f"curve 3 interval {MeshBottomHeight}")
    cubit.cmd("curve 3 scheme equal")
    cubit.cmd("mesh curve 3")
    cubit.cmd(f"curve 2 interval {MeshWidth}")
    cubit.cmd("curve 2 scheme equal")
    cubit.cmd("mesh curve 2")
    cubit.cmd(f"curve 11 interval {MeshDepth}")
    cubit.cmd("curve 11 scheme equal")
    cubit.cmd("mesh curve 11")
    cubit.cmd("mesh volume 1")
    # Mesh Cavity
    cubit.cmd(f"curve 29 interval {MeshCavityHeight}")
    cubit.cmd("curve 29 scheme equal")
    cubit.cmd("mesh curve 29")
    cubit.cmd(f"curve 16 interval {MeshWidth}")
    cubit.cmd("curve 16 scheme equal")
    cubit.cmd("mesh curve 16")
    cubit.cmd(f"curve 21 interval {MeshDepth}")
    cubit.cmd("curve 21 scheme equal")
    cubit.cmd("mesh curve 21")
    cubit.cmd("mesh volume 2")
    # Mesh Inflow
    cubit.cmd(f"curve 40 interval {MeshInflowHeight}")
    cubit.cmd("curve 40 scheme equal")
    cubit.cmd("mesh curve 40")
    cubit.cmd("mesh volume 3")

    ##########
    # GROUPS #
    ##########

    # Structure
    cubit.add_element_type(
        cubit.group(add_value="add volume 1"),
        name="flexible bottom",
        el_type=cupy.element_type.hex8,
        material={
            "MAT": 1,
        },
        bc_description={
            "KINEM": "nonlinear",
            "TECH": "eas_full",
        },
    )

    # Fluid
    cubit.add_element_type(
        cubit.group(add_value="add volume 2 3"),
        name="fluid",
        el_type=cupy.element_type.hex8_fluid,
        material={
            "MAT": 2,
        },
        bc_description={
            "NA": "ALE",
        },
    )

    cubit.fourc_input.combine_sections(
        {
            "PROBLEM TYPE": {"PROBLEMTYPE": "Fluid_Structure_Interaction"},
            "PROBLEM SIZE": {"DIM": 3},
            "STRUCTURAL DYNAMIC": {
                "INT_STRATEGY": "Standard",
                "LINEAR_SOLVER": 3,
            },
        }
    )

    # Compare the input file created for 4C.
    compare_yaml(cubit, mesh_in_exo=True)


def test_cmd_return():
    """Test the cmd_return function of CubitPy."""

    cubit = CubitPy()

    center = cubit.cmd_return("create vertex 0 0 0", cupy.geometry.vertex)
    assert center.get_geometry_type() == cupy.geometry.vertex
    assert center.id() == 1

    arc_1 = cubit.cmd_return(
        f"create curve arc center vertex {center.id()} radius 1 full",
        cupy.geometry.curve,
    )
    assert arc_1.get_geometry_type() == cupy.geometry.curve
    assert arc_1.id() == 1

    center = cubit.cmd_return("create vertex 0.1 0 0", cupy.geometry.vertex)
    assert center.get_geometry_type() == cupy.geometry.vertex
    assert center.id() == 3

    arc_2 = cubit.cmd_return(
        f"create curve arc center vertex {center.id()} radius 2 full",
        cupy.geometry.curve,
    )
    assert arc_2.get_geometry_type() == cupy.geometry.curve
    assert arc_2.id() == 2

    # We check the volume here as well, as in CoreForm a sheet body is created here that Cubit
    # internally handles as a volume. But, we don't want this volume returned here.
    create_surface_geometry = cubit.cmd_return_dict(
        f"create surface curve {arc_1.id()} {arc_2.id()}",
        [cupy.geometry.surface, cupy.geometry.volume],
    )
    for surface in create_surface_geometry[cupy.geometry.surface]:
        assert surface.get_geometry_type() == cupy.geometry.surface
    assert [item.id() for item in create_surface_geometry[cupy.geometry.surface]] == [1]
    assert len(create_surface_geometry[cupy.geometry.volume]) == 0

    sweep_geometry = cubit.cmd_return_dict(
        f"sweep surface {surface.id()} perpendicular distance 2",
        [
            cupy.geometry.vertex,
            cupy.geometry.curve,
            cupy.geometry.surface,
            cupy.geometry.volume,
        ],
    )
    assert len(sweep_geometry) == 4
    assert [item.id() for item in sweep_geometry[cupy.geometry.vertex]] == [5, 6]
    assert [item.id() for item in sweep_geometry[cupy.geometry.curve]] == [3, 4, 5, 6]
    assert [item.id() for item in sweep_geometry[cupy.geometry.surface]] == [2, 3, 4]
    assert [item.id() for item in sweep_geometry[cupy.geometry.volume]] == [1]
