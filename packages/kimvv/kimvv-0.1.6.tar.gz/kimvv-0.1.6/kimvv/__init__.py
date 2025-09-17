from .core import KIMVVTestDriver, override_call_method
from .EquilibriumCrystalStructure.test_driver.test_driver import TestDriver as __EquilibriumCrystalStructure
from .ElasticConstantsCrystal.test_driver.test_driver import TestDriver as __ElasticConstantsCrystal
from .CrystalStructureAndEnergyVsPressure.test_driver.test_driver import TestDriver as __CrystalStructureAndEnergyVsPressure


@override_call_method
class EquilibriumCrystalStructure(__EquilibriumCrystalStructure, KIMVVTestDriver):
    pass


@override_call_method
class ElasticConstantsCrystal(__ElasticConstantsCrystal, KIMVVTestDriver):
    pass


@override_call_method
class CrystalStructureAndEnergyVsPressure(__CrystalStructureAndEnergyVsPressure, KIMVVTestDriver):
    pass


__all__ = [
    "EquilibriumCrystalStructure",
    "ElasticConstantsCrystal",
    "CrystalStructureAndEnergyVsPressure",
]
