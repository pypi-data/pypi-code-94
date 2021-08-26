#################################################################################
# The Institute for the Design of Advanced Energy Systems Integrated Platform
# Framework (IDAES IP) was produced under the DOE Institute for the
# Design of Advanced Energy Systems (IDAES), and is copyright (c) 2018-2021
# by the software owners: The Regents of the University of California, through
# Lawrence Berkeley National Laboratory,  National Technology & Engineering
# Solutions of Sandia, LLC, Carnegie Mellon University, West Virginia University
# Research Corporation, et al.  All rights reserved.
#
# Please see the files COPYRIGHT.md and LICENSE.md for full copyright and
# license information.
#################################################################################
"""
Tests for feed block.
Authors: Andrew Lee
"""

import pytest
from pyomo.environ import ConcreteModel, value
from pyomo.util.check_units import assert_units_consistent

from idaes.core import FlowsheetBlock
from idaes.generic_models.unit_models.feed import Feed
from idaes.generic_models.properties.examples.saponification_thermo import (
                        SaponificationParameterBlock)
from idaes.generic_models.properties import iapws95
from idaes.core.util.model_statistics import (degrees_of_freedom,
                                              number_variables,
                                              number_total_constraints,
                                              number_unused_variables)
from idaes.core.util.testing import (PhysicalParameterTestBlock,
                                     initialization_tester)
from idaes.core.util import get_solver


# -----------------------------------------------------------------------------
# Get default solver for testing
solver = get_solver()


# -----------------------------------------------------------------------------
@pytest.mark.unit
def test_config():
    m = ConcreteModel()
    m.fs = FlowsheetBlock(default={"dynamic": False})

    m.fs.properties = PhysicalParameterTestBlock()

    m.fs.unit = Feed(default={"property_package": m.fs.properties})

    # Check unit config arguments
    assert len(m.fs.unit.config) == 4

    assert not m.fs.unit.config.dynamic
    assert not m.fs.unit.config.has_holdup
    assert m.fs.unit.config.property_package is m.fs.properties


# -----------------------------------------------------------------------------
class TestSaponification(object):
    @pytest.fixture(scope="class")
    def sapon(self):
        m = ConcreteModel()
        m.fs = FlowsheetBlock(default={"dynamic": False})

        m.fs.properties = SaponificationParameterBlock()

        m.fs.unit = Feed(default={"property_package": m.fs.properties})

        m.fs.unit.flow_vol.fix(1.0e-03)
        m.fs.unit.conc_mol_comp[0, "H2O"].fix(55388.0)
        m.fs.unit.conc_mol_comp[0, "NaOH"].fix(100.0)
        m.fs.unit.conc_mol_comp[0, "EthylAcetate"].fix(100.0)
        m.fs.unit.conc_mol_comp[0, "SodiumAcetate"].fix(0.0)
        m.fs.unit.conc_mol_comp[0, "Ethanol"].fix(0.0)

        m.fs.unit.temperature.fix(303.15)
        m.fs.unit.pressure.fix(101325.0)

        return m

    @pytest.mark.build
    @pytest.mark.unit
    def test_build(self, sapon):

        assert hasattr(sapon.fs.unit, "flow_vol")
        assert hasattr(sapon.fs.unit, "conc_mol_comp")
        assert hasattr(sapon.fs.unit, "temperature")
        assert hasattr(sapon.fs.unit, "pressure")

        assert hasattr(sapon.fs.unit, "outlet")
        assert len(sapon.fs.unit.outlet.vars) == 4
        assert hasattr(sapon.fs.unit.outlet, "flow_vol")
        assert hasattr(sapon.fs.unit.outlet, "conc_mol_comp")
        assert hasattr(sapon.fs.unit.outlet, "temperature")
        assert hasattr(sapon.fs.unit.outlet, "pressure")

        assert number_variables(sapon) == 8
        assert number_total_constraints(sapon) == 0
        assert number_unused_variables(sapon) == 8

    @pytest.mark.component
    def test_units(self, sapon):
        assert_units_consistent(sapon)

    @pytest.mark.unit
    def test_dof(self, sapon):
        assert degrees_of_freedom(sapon) == 0

    @pytest.mark.solver
    @pytest.mark.skipif(solver is None, reason="Solver not available")
    @pytest.mark.component
    def test_initialize(self, sapon):
        initialization_tester(sapon)

    # No solve, as nothing to solve for

    @pytest.mark.solver
    @pytest.mark.skipif(solver is None, reason="Solver not available")
    @pytest.mark.component
    def test_solution(self, sapon):
        assert (pytest.approx(101325.0, abs=1e-2) ==
                value(sapon.fs.unit.outlet.pressure[0]))
        assert (pytest.approx(303.15, abs=1e-2) ==
                value(sapon.fs.unit.outlet.temperature[0]))
        assert (pytest.approx(1e-3, abs=1e-5) ==
                value(sapon.fs.unit.outlet.flow_vol[0]))
        assert (pytest.approx(55388, abs=1e0) ==
                value(sapon.fs.unit.outlet.conc_mol_comp[0, "H2O"]))
        assert (pytest.approx(100.0, abs=1e-2) ==
                value(sapon.fs.unit.outlet.conc_mol_comp[0, "EthylAcetate"]))
        assert (pytest.approx(100.0, abs=1e-2) ==
                value(sapon.fs.unit.outlet.conc_mol_comp[0, "NaOH"]))
        assert (pytest.approx(0.00, abs=1e-2) ==
                value(sapon.fs.unit.outlet.conc_mol_comp[0, "Ethanol"]))
        assert (pytest.approx(0.00, abs=1e-2) ==
                value(sapon.fs.unit.outlet.conc_mol_comp[0, "SodiumAcetate"]))

    @pytest.mark.ui
    @pytest.mark.unit
    def test_report(self, sapon):
        sapon.fs.unit.report()


# -----------------------------------------------------------------------------
@pytest.mark.iapws
@pytest.mark.skipif(not iapws95.iapws95_available(),
                    reason="IAPWS not available")
class TestIAPWS(object):
    @pytest.fixture(scope="class")
    def iapws(self):
        m = ConcreteModel()
        m.fs = FlowsheetBlock(default={"dynamic": False})

        m.fs.properties = iapws95.Iapws95ParameterBlock(default={
                "phase_presentation": iapws95.PhaseType.LG})

        m.fs.unit = Feed(default={"property_package": m.fs.properties})

        m.fs.unit.flow_mol.fix(100)
        m.fs.unit.enth_mol.fix(24000)
        m.fs.unit.pressure.fix(101325)

        return m

    @pytest.mark.build
    @pytest.mark.unit
    def test_build(self, iapws):
        assert hasattr(iapws.fs.unit, "flow_mol")
        assert hasattr(iapws.fs.unit, "enth_mol")
        assert hasattr(iapws.fs.unit, "pressure")

        assert hasattr(iapws.fs.unit, "outlet")
        assert len(iapws.fs.unit.outlet.vars) == 3
        assert hasattr(iapws.fs.unit.outlet, "flow_mol")
        assert hasattr(iapws.fs.unit.outlet, "enth_mol")
        assert hasattr(iapws.fs.unit.outlet, "pressure")

        assert number_variables(iapws) == 3
        assert number_total_constraints(iapws) == 0
        assert number_unused_variables(iapws) == 3

    @pytest.mark.component
    def test_units(self, iapws):
        assert_units_consistent(iapws)

    @pytest.mark.unit
    def test_dof(self, iapws):
        assert degrees_of_freedom(iapws) == 0

    @pytest.mark.solver
    @pytest.mark.skipif(solver is None, reason="Solver not available")
    @pytest.mark.component
    def test_initialize(self, iapws):
        initialization_tester(iapws)

    # No solve test, as nothing to solve for

    @pytest.mark.solver
    @pytest.mark.skipif(solver is None, reason="Solver not available")
    @pytest.mark.component
    def test_solution(self, iapws):
        assert (pytest.approx(101325.0, abs=1e3) ==
                value(iapws.fs.unit.outlet.pressure[0]))
        assert (pytest.approx(24000, abs=1e3) ==
                value(iapws.fs.unit.outlet.enth_mol[0]))
        assert (pytest.approx(100.0, abs=1e-2) ==
                value(iapws.fs.unit.outlet.flow_mol[0]))

        assert (pytest.approx(373.12, abs=1e-2) == value(
            iapws.fs.unit.properties[0].temperature))
        assert (pytest.approx(0.5953, abs=1e-4) == value(
            iapws.fs.unit.properties[0].phase_frac["Liq"]))

    @pytest.mark.ui
    @pytest.mark.unit
    def test_report(self, iapws):
        iapws.fs.unit.report()
