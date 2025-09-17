from pathlib import Path
from typing import ClassVar

from ryd_numerov.elements.base_element import BaseElement


class Sodium(BaseElement):
    species = "Na"
    Z = 11
    number_valence_electrons = 1
    ground_state_shell = (3, 0)
    _core_electron_configuration = "2p6"
    _nist_energy_levels_file = Path(__file__).parent / "nist_energy_levels" / "sodium.txt"

    # https://webbook.nist.gov/cgi/inchi?ID=C7440235&Mask=20
    _ionization_energy = (5.139_08, None, "eV")

    potential_type_default = "model_potential_marinescu_1993"

    # -- [1] Phys. Rev. A 45, 4720 (1992)
    # -- [2] Quantum Electron. 25 914 (1995)
    # -- [3] J. Phys. B: At. Mol. Opt. Phys. 30 2345 (1997)
    _quantum_defects: ClassVar = {
        (0, 0.5, 1 / 2): (1.34796938, 0.0609892, 0.0196743, -0.001045, 0),  # [1,2]
        (1, 0.5, 1 / 2): (0.85544502, 0.112067, 0.0479, 0.0457, 0),  # [2]
        (1, 1.5, 1 / 2): (0.85462615, 0.112344, 0.0497, 0.0406, 0),  # [2]
        (2, 1.5, 1 / 2): (0.014909286, -0.042506, 0.00840, 0, 0),  # [2,3]
        (2, 2.5, 1 / 2): (0.01492422, -0.042585, 0.00840, 0, 0),  # [2,3]
        (3, 2.5, 1 / 2): (0.001632977, -0.0069906, 0.00423, 0, 0),  # [3]
        (3, 3.5, 1 / 2): (0.001630875, -0.0069824, 0.00352, 0, 0),  # [3]
        (4, 3.5, 1 / 2): (0.00043825, -0.00283, 0, 0, 0),  # [3]
        (4, 4.5, 1 / 2): (0.00043740, -0.00297, 0, 0, 0),  # [3]
        (5, 4.5, 1 / 2): (0.00016114, -0.00185, 0, 0, 0),  # [3]
        (5, 5.5, 1 / 2): (0.00015796, -0.00148, 0, 0, 0),  # [3]
    }

    _corrected_rydberg_constant = (109734.69, None, "1/cm")

    # Phys. Rev. A 49, 982 (1994)
    alpha_c_marinescu_1993 = 0.9448
    r_c_dict_marinescu_1993: ClassVar = {0: 0.45489422, 1: 0.45798739, 2: 0.71875312, 3: 28.6735059}
    model_potential_parameter_marinescu_1993: ClassVar = {
        0: (4.82223117, 2.45449865, -1.12255048, -1.42631393),
        1: (5.08382502, 2.18226881, -1.19534623, -1.03142861),
        2: (3.53324124, 2.48697936, -0.75688448, -1.27852357),
        3: (1.11056646, 1.05458759, 1.73203428, -0.09265696),
    }

    # https://iopscience.iop.org/article/10.1088/1674-1056/18/10/025
    model_potential_parameter_fei_2009 = (0.9729, 2.5434, 1.0406, 0.4685)
