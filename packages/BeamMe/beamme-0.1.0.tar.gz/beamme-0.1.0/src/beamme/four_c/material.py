# The MIT License (MIT)
#
# Copyright (c) 2018-2025 BeamMe Authors
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
"""This file implements materials for 4C beams and solids."""

from beamme.core.material import MaterialBeamBase as _MaterialBeamBase
from beamme.core.material import MaterialSolidBase as _MaterialSolidBase


class MaterialReissner(_MaterialBeamBase):
    """Holds material definition for Reissner beams."""

    def __init__(self, shear_correction=1, **kwargs):
        super().__init__(material_string="MAT_BeamReissnerElastHyper", **kwargs)

        # Shear factor for Reissner beam.
        self.shear_correction = shear_correction

    def dump_to_list(self):
        """Return a list with the (single) item representing this material."""
        if (
            self.area is None
            and self.mom2 is None
            and self.mom3 is None
            and self.polar is None
        ):
            area, mom2, mom3, polar = self.calc_area_stiffness()
        elif (
            self.area is not None
            and self.mom2 is not None
            and self.mom3 is not None
            and self.polar is not None
        ):
            area = self.area
            mom2 = self.mom2
            mom3 = self.mom3
            polar = self.polar
        else:
            raise ValueError(
                "Either all relevant material parameters are set "
                "by the user, or a circular cross-section will be assumed. "
                "A combination is not possible"
            )

        data = {
            "YOUNG": self.youngs_modulus,
            "POISSONRATIO": self.nu,
            "DENS": self.density,
            "CROSSAREA": area,
            "SHEARCORR": self.shear_correction,
            "MOMINPOL": polar,
            "MOMIN2": mom2,
            "MOMIN3": mom3,
        }
        if self.interaction_radius is not None:
            data["INTERACTIONRADIUS"] = self.interaction_radius
        return {"MAT": self.i_global + 1, self.material_string: data}


class MaterialReissnerElastoplastic(MaterialReissner):
    """Holds elasto-plastic material definition for Reissner beams."""

    def __init__(
        self,
        *,
        yield_moment=None,
        isohardening_modulus_moment=None,
        torsion_plasticity=False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.material_string = "MAT_BeamReissnerElastPlastic"

        if yield_moment is None or isohardening_modulus_moment is None:
            raise ValueError(
                "The yield moment and the isohardening modulus for moments must be specified "
                "for plasticity."
            )

        self.yield_moment = yield_moment
        self.isohardening_modulus_moment = isohardening_modulus_moment
        self.torsion_plasticity = torsion_plasticity

    def dump_to_list(self):
        """Return a list with the (single) item representing this material."""
        super_list = super().dump_to_list()
        mat_dict = super_list[self.material_string]
        mat_dict["YIELDM"] = self.yield_moment
        mat_dict["ISOHARDM"] = self.isohardening_modulus_moment
        mat_dict["TORSIONPLAST"] = self.torsion_plasticity
        return super_list


class MaterialKirchhoff(_MaterialBeamBase):
    """Holds material definition for Kirchhoff beams."""

    def __init__(self, is_fad=False, **kwargs):
        super().__init__(material_string="MAT_BeamKirchhoffElastHyper", **kwargs)
        self.is_fad = is_fad

    def dump_to_list(self):
        """Return a list with the (single) item representing this material."""
        if (
            self.area is None
            and self.mom2 is None
            and self.mom3 is None
            and self.polar is None
        ):
            area, mom2, mom3, polar = self.calc_area_stiffness()
        elif (
            self.area is not None
            and self.mom2 is not None
            and self.mom3 is not None
            and self.polar is not None
        ):
            area = self.area
            mom2 = self.mom2
            mom3 = self.mom3
            polar = self.polar
        else:
            raise ValueError(
                "Either all relevant material parameters are set "
                "by the user, or a circular cross-section will be assumed. "
                "A combination is not possible"
            )
        data = {
            "YOUNG": self.youngs_modulus,
            "SHEARMOD": self.youngs_modulus / (2.0 * (1.0 + self.nu)),
            "DENS": self.density,
            "CROSSAREA": area,
            "MOMINPOL": polar,
            "MOMIN2": mom2,
            "MOMIN3": mom3,
            "FAD": self.is_fad,
        }
        if self.interaction_radius is not None:
            data["INTERACTIONRADIUS"] = self.interaction_radius
        return {"MAT": self.i_global + 1, self.material_string: data}


class MaterialEulerBernoulli(_MaterialBeamBase):
    """Holds material definition for Euler Bernoulli beams."""

    def __init__(self, **kwargs):
        super().__init__(
            material_string="MAT_BeamKirchhoffTorsionFreeElastHyper", **kwargs
        )

    def dump_to_list(self):
        """Return a list with the (single) item representing this material."""
        area, mom2, _mom3, _polar = self.calc_area_stiffness()
        if self.area is None and self.mom2 is None:
            area, mom2, _mom3, _polar = self.calc_area_stiffness()
        elif self.area is not None and self.mom2 is not None:
            area = self.area
            mom2 = self.mom2
        else:
            raise ValueError(
                "Either all relevant material parameters are set "
                "by the user, or a circular cross-section will be assumed. "
                "A combination is not possible"
            )
        data = {
            "YOUNG": self.youngs_modulus,
            "DENS": self.density,
            "CROSSAREA": area,
            "MOMIN": mom2,
        }
        return {"MAT": self.i_global + 1, self.material_string: data}


class MaterialSolid(_MaterialSolidBase):
    """Base class for a material for solids."""

    def __init__(self, material_string=None, **kwargs):
        """Set the material values for a solid."""
        self.material_string = material_string
        super().__init__(**kwargs)

    def dump_to_list(self):
        """Return a list with the (single) item representing this material."""

        return {"MAT": self.i_global + 1, self.material_string: self.data}


class MaterialStVenantKirchhoff(MaterialSolid):
    """Holds material definition for StVenant Kirchhoff solids."""

    def __init__(self, youngs_modulus=-1.0, nu=0.0, density=0.0):
        super().__init__(
            material_string="MAT_Struct_StVenantKirchhoff",
            data={"YOUNG": youngs_modulus, "NUE": nu, "DENS": density},
        )
