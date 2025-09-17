from pathlib import Path
from typing import ClassVar

from ryd_numerov.elements.base_element import BaseElement


class _RubidiumAbstract(BaseElement):
    Z = 37
    number_valence_electrons = 1
    ground_state_shell = (5, 0)
    _additional_allowed_shells: ClassVar = [(4, 2), (4, 3)]

    _core_electron_configuration = "4p6"
    _nist_energy_levels_file = Path(__file__).parent / "nist_energy_levels" / "rubidium.txt"

    # https://journals.aps.org/pra/pdf/10.1103/PhysRevA.83.052515
    _ionization_energy = (1_010_029.164_6, 0.000_3, "GHz")

    potential_type_default = "model_potential_marinescu_1993"

    # older value
    # https://webbook.nist.gov/cgi/inchi?ID=C7440177&Mask=20
    # _ionization_energy = (4.177_13, 0.000_002, "eV")  # noqa: ERA001
    # corresponds to (1_010_025.54, 0.48, "GHz")

    # -- [1] Phys. Rev. A 83, 052515 (2011) - Rb87
    # -- [2] Phys. Rev. A 67, 052502 (2003) - Rb85
    # -- [3] Phys. Rev. A 74, 054502 (2006) - Rb85
    # -- [4] Phys. Rev. A 74, 062712 (2006) - Rb85
    _quantum_defects: ClassVar = {
        (0, 0.5, 1 / 2): (3.1311807, 0.1787, 0, 0, 0),  # [1]
        (1, 0.5, 1 / 2): (2.6548849, 0.29, 0, 0, 0),  # [2]
        (1, 1.5, 1 / 2): (2.6416737, 0.295, 0, 0, 0),  # [2]
        (2, 1.5, 1 / 2): (1.3480948, -0.6054, 0, 0, 0),  # [1]
        (2, 2.5, 1 / 2): (1.3464622, -0.594, 0, 0, 0),  # [1]
        (3, 2.5, 1 / 2): (0.0165192, -0.085, 0, 0, 0),  # [3]
        (3, 3.5, 1 / 2): (0.0165437, -0.086, 0, 0, 0),  # [3]
        (4, 3.5, 1 / 2): (0.004, 0, 0, 0, 0),  # [4]
        (4, 4.5, 1 / 2): (0.004, 0, 0, 0, 0),  # [4]
    }

    # Phys. Rev. A 49, 982 (1994)
    alpha_c_marinescu_1993 = 9.076
    r_c_dict_marinescu_1993: ClassVar = {0: 1.66242117, 1: 1.50195124, 2: 4.86851938, 3: 4.79831327}
    model_potential_parameter_marinescu_1993: ClassVar = {
        0: (3.69628474, 1.64915255, -9.86069196, 0.19579987),
        1: (4.44088978, 1.92828831, -16.79597770, -0.81633314),
        2: (3.78717363, 1.57027864, -11.6558897, 0.52942835),
        3: (2.39848933, 1.76810544, -12.0710678, 0.77256589),
    }

    # https://iopscience.iop.org/article/10.1088/1674-1056/18/10/025
    model_potential_parameter_fei_2009 = (0.9708, 13.9706, 0.2909, 0.2215)


class Rubidium87(_RubidiumAbstract):
    species = "Rb87"

    _corrected_rydberg_constant = (109736.62301604665, None, "1/cm")


class Rubidium(Rubidium87):
    # for backwards compatibility
    species = "Rb"


class Rubidium85(_RubidiumAbstract):
    species = "Rb85"

    _corrected_rydberg_constant = (109736.605, None, "1/cm")
