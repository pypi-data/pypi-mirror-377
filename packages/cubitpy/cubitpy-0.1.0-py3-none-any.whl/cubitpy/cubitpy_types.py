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
"""This module contains ENums for types used in cubitpy as well as functions to
convert them to strings for cubit or 4C commands or the wrapper."""

import warnings
from enum import Enum, auto


class GeometryType(Enum):
    """Enum for geometry types."""

    vertex = auto()
    curve = auto()
    surface = auto()
    volume = auto()

    def get_cubit_string(self):
        """Return the string that represents this item in cubit."""

        if self == self.vertex:
            return "vertex"
        elif self == self.curve:
            return "curve"
        elif self == self.surface:
            return "surface"
        elif self == self.volume:
            return "volume"
        else:
            raise ValueError("Got unexpected type {}!".format(self))

    def get_dat_bc_section_string(self):
        """Return the string that represents this item in a dat file
        section."""

        if self == self.vertex:
            return "POINT"
        elif self == self.curve:
            return "LINE"
        elif self == self.surface:
            return "SURF"
        elif self == self.volume:
            return "VOL"
        else:
            raise ValueError("Got unexpected type {}!".format(self))


class FiniteElementObject(Enum):
    """Enum for finite element objects."""

    hex = auto()
    tet = auto()
    wedge = auto()
    face = auto()
    triangle = auto()
    edge = auto()
    node = auto()

    def get_cubit_string(self):
        """Return the string that represents this item in cubit."""

        if self == self.hex:
            return "hex"
        elif self == self.tet:
            return "tet"
        elif self == self.wedge:
            return "wedge"
        elif self == self.face:
            return "face"
        elif self == self.triangle:
            return "tri"
        elif self == self.edge:
            return "edge"
        elif self == self.node:
            return "node"

    def get_dat_bc_section_string(self):
        """Return the string that represents this item in a dat file section.

        Currently this only makes sense for the node type, when
        explicitly defining boundary conditions on nodes.
        """
        if self == self.node:
            return "POINT"
        else:
            raise ValueError("Got unexpected type {}!".format(self))


class CubitItems(Enum):
    """Enum for cubit internal items such as groups."""

    group = auto()


class ElementType(Enum):
    """Enum for finite element shape types."""

    hex8 = auto()
    hex20 = auto()
    hex27 = auto()
    tet4 = auto()
    tet10 = auto()
    hex8sh = auto()
    hex8_fluid = auto()
    tet4_fluid = auto()
    hex8_thermo = auto()
    tet4_thermo = auto()
    hex8_scatra = auto()
    tet4_scatra = auto()
    quad4 = auto()
    wedge6 = auto()

    def get_cubit_names(self):
        """Get the strings that are needed to mesh and describe this element in
        cubit."""

        # Get the element type parameters.
        if (
            self == self.hex8
            or self == self.hex8sh
            or self == self.hex8_fluid
            or self == self.hex8_thermo
            or self == self.hex8_scatra
        ):
            cubit_scheme = "Auto"
            cubit_element_type = "HEX8"
        elif self == self.hex20:
            cubit_scheme = "Auto"
            cubit_element_type = "HEX20"
        elif self == self.hex27:
            cubit_scheme = "Auto"
            cubit_element_type = "HEX27"
        elif (
            self == self.tet4
            or self == self.tet4_fluid
            or self == self.tet4_thermo
            or self == self.tet4_scatra
        ):
            cubit_scheme = "Tetmesh"
            cubit_element_type = "TETRA4"
        elif self == self.tet10:
            cubit_scheme = "Tetmesh"
            cubit_element_type = "TETRA10"
        elif self == self.quad4:
            cubit_scheme = "Auto"
            cubit_element_type = "QUAD4"
        elif self == self.wedge6:
            cubit_scheme = None
            cubit_element_type = "WEDGE6"
        else:
            raise ValueError("Got wrong element type {}!".format(self))

        return cubit_scheme, cubit_element_type

    def get_four_c_name(self):
        """Get the name of this element in 4C."""

        # Get the element type parameters.
        if (
            self == self.hex8sh
            or self == self.hex8
            or self == self.hex20
            or self == self.hex27
            or self == self.tet10
            or self == self.tet4
            or self == self.wedge6
        ):
            return "SOLID"
        elif self == self.hex8_fluid or self == self.tet4_fluid:
            return "FLUID"
        elif self == self.hex8_thermo or self == self.tet4_thermo:
            return "THERMO"
        elif self == self.hex8_scatra or self == self.tet4_scatra:
            return "TRANSP"
        if self == self.quad4:
            return "WALL"
        else:
            raise ValueError("Got wrong element type {}!".format(self))

    def get_four_c_section(self):
        """Get the correct section name of this element in 4C."""

        if self == self.hex8_fluid or self == self.tet4_fluid:
            return "FLUID"
        elif (
            self == self.hex20
            or self == self.hex8
            or self == self.hex20
            or self == self.hex27
            or self == self.tet4
            or self == self.hex8sh
            or self == self.tet10
            or self == self.quad4
            or self == self.wedge6
        ):
            return "STRUCTURE"
        elif self == self.hex8_thermo or self == self.tet4_thermo:
            return "THERMO"
        elif self == self.hex8_scatra or self == self.tet4_scatra:
            return "TRANSPORT"
        else:
            raise ValueError("Got wrong element type {}!".format(self))

    def get_four_c_type(self):
        """Get the correct element shape name of this element in 4C."""

        if (
            self == self.hex8
            or self == self.hex8sh
            or self == self.hex8_fluid
            or self == self.hex8_thermo
            or self == self.hex8_scatra
        ):
            return "HEX8"
        elif self == self.hex20:
            return "HEX20"
        elif self == self.hex27:
            return "HEX27"
        elif (
            self == self.tet4
            or self == self.tet4_fluid
            or self == self.tet4_thermo
            or self == self.tet4_scatra
        ):
            return "TET4"
        elif self == self.tet10:
            return "TET10"
        elif self == self.quad4:
            return "QUAD4"
        elif self == self.wedge6:
            return "WEDGE6"
        else:
            raise ValueError("Got wrong element type {}!".format(self))

    def get_default_four_c_description(self):
        """Get the default text for the description in 4C after the material
        string."""

        # Get the element type parameters.
        if (
            self == self.hex8
            or self == self.hex20
            or self == self.hex27
            or self == self.tet4
            or self == self.tet10
            or self == self.wedge6
        ):
            return {"KINEM": "nonlinear"}
        elif self == self.hex8sh:
            return {"KINEM": "nonlinear", "TECH": "shell_eas_ans"}

        elif self == self.hex8_fluid or self == self.tet4_fluid:
            return {"NA": "ALE"}
        elif self == self.hex8_thermo or self == self.tet4_thermo:
            return {}
        elif self == self.hex8_scatra or self == self.tet4_scatra:
            return {}
        else:
            raise ValueError("Got wrong element type {}!".format(self))


class BoundaryConditionType(Enum):
    """Enum for boundary conditions types."""

    dirichlet = auto()
    neumann = auto()
    point_coupling = auto()
    beam_to_solid_volume_meshtying = auto()
    beam_to_solid_surface_meshtying = auto()
    beam_to_solid_surface_contact = auto()
    # The following value "solid_to_solid_surface_contact" is deprecated and
    # only kept for legacy reasons.
    # Please use "solid_to_solid_contact" instead.
    solid_to_solid_surface_contact = auto()
    solid_to_solid_contact = auto()

    # fluid
    flow_rate = auto()
    fluid_neumann_inflow_stab = auto()
    fsi_coupling = auto()
    ale_dirichlet = auto()

    def get_dat_bc_section_header(self, geometry_type):
        """Get the header string for the boundary condition input section in
        the dat file."""

        if self == self.dirichlet or self == self.neumann:
            if self == self.dirichlet:
                self_string = "DIRICH"
            else:
                self_string = "NEUMANN"

            return "DESIGN {} {} CONDITIONS".format(
                geometry_type.get_dat_bc_section_string(), self_string
            )
        elif (
            self == self.beam_to_solid_volume_meshtying
            and geometry_type == GeometryType.volume
        ):
            return "BEAM INTERACTION/BEAM TO SOLID VOLUME MESHTYING VOLUME"
        elif (
            self == self.beam_to_solid_surface_meshtying
            and geometry_type == GeometryType.surface
        ):
            return "BEAM INTERACTION/BEAM TO SOLID SURFACE MESHTYING SURFACE"
        elif (
            self == self.beam_to_solid_surface_contact
            and geometry_type == GeometryType.surface
        ):
            return "BEAM INTERACTION/BEAM TO SOLID SURFACE CONTACT SURFACE"
        elif self == self.point_coupling and (geometry_type == GeometryType.vertex):
            return "DESIGN POINT COUPLING CONDITIONS"
        elif self == self.solid_to_solid_surface_contact and (
            geometry_type == GeometryType.surface
        ):
            warnings.warn(
                "The 'solid_to_solid_surface_contact' boundary condition enum is deprecated "
                "and will be removed in a future version. "
                "Use 'solid_to_solid_contact' instead.",
                category=DeprecationWarning,
                stacklevel=2,
            )
            return "DESIGN SURF MORTAR CONTACT CONDITIONS 3D"
        elif self == self.solid_to_solid_contact and (
            geometry_type == GeometryType.surface
        ):
            return "DESIGN SURF MORTAR CONTACT CONDITIONS 3D"
        elif self == self.solid_to_solid_contact and (
            geometry_type == GeometryType.curve
        ):
            return "DESIGN LINE MORTAR CONTACT CONDITIONS 2D"
        elif self == self.fsi_coupling and (geometry_type == GeometryType.surface):
            return "DESIGN FSI COUPLING SURF CONDITIONS"
        elif self == self.ale_dirichlet and (geometry_type == GeometryType.surface):
            return "DESIGN SURF ALE DIRICH CONDITIONS"
        elif self == self.flow_rate and (geometry_type == GeometryType.surface):
            return "DESIGN FLOW RATE SURF CONDITIONS"
        elif self == self.fluid_neumann_inflow_stab and (
            geometry_type == GeometryType.surface
        ):
            return "FLUID NEUMANN INFLOW SURF CONDITIONS"
        elif self == self.fluid_neumann_inflow_stab and (
            geometry_type == GeometryType.curve
        ):
            return "FLUID NEUMANN INFLOW LINE CONDITIONS"
        else:
            raise ValueError(
                "No implemented case for {} and {}!".format(self, geometry_type)
            )
