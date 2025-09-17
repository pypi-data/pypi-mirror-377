# python -m unittest pyxtal/test_all.py
import unittest
from pyxtal.lego.builder import builder
from pyxtal import pyxtal
import random
import numpy as np

xtal = pyxtal()
xtal.from_prototype('graphite')
cif_file = xtal.to_pymatgen()

bu1 = builder(['C'], [1], verbose=False)
bu1.set_descriptor_calculator(mykwargs={'rcut': 1.9})
bu1.set_reference_enviroments(cif_file)
bu1.set_criteria(CN={'C': [3]})

xtal.from_spg_wps_rep(92, ['4a', '8b'], [5.085, 7.099, 0.294, 0.094, 0.241, 0.826], ['Si', 'O'])
cif_file = xtal.to_pymatgen()
bu2 = builder(['Si', 'O'], [1, 2], verbose=False)
bu2.set_descriptor_calculator(mykwargs={'rcut': 2.4})
bu2.set_reference_enviroments(cif_file)
bu2.set_criteria(CN={'Si': [4], 'O': [2]}, exclude_ii=True)

class TestBuilder(unittest.TestCase):
    #def test_gen_xtal(self):
    #    print("test_gen_xtal")
    #    random.seed(0)
    #    np.random.seed(0)
    #    spg, wps = 191, [['6j', '6j', '6k']]
    #    xtal, sim = builder1.generate_xtal(spg, wps, 10,
    #                                       N_max = 1,
    #                                       add_db = False,
    #                                       random_state = 2)
    #    assert sim < 1e-2

    def test_opt_xtal(self):
        print("test_opt_xtal")
        spg, wps = 179, ['6a', '6a', '6a', '6a']
        for x in [
                    [11.111, 2.640, 0.290, 0.751, 0.421, 0.872],
                    [ 7.952, 2.606, 0.592, 0.926, 0.608, 0.307],
        ]:
            xtal = pyxtal()
            xtal.from_spg_wps_rep(spg, wps, x, ['C']*len(wps))
            xtal, sim, _ = bu1.optimize_xtal(xtal, add_db=False)
            #print(xtal.get_1d_rep_x())
            assert sim < 1e-2

    def test_opt_xtal2(self):
        print("test sio2")
        spg, wps = 92, ['4a', '8b']
        for x in [[5.0, 7.1, 0.3, 0.1, 0.2, 0.8]]:
            xtal = pyxtal()
            xtal.from_spg_wps_rep(spg, wps, x, ['Si', 'O'])
            xtal, sim, _ = bu2.optimize_xtal(xtal, add_db=False)
            assert sim < 1e-2

    def test_opt_xtals(self):
        print("test_opt_xtals")
        spg, wps = 179, ['6a', '6a', '6a', '6a']
        xtals = []
        for x in [
                    [11.111, 2.640, 0.290, 0.751, 0.421, 0.872],
                    [ 7.952, 2.606, 0.592, 0.926, 0.608, 0.307],
                 ]:
            xtal = pyxtal()
            xtal.from_spg_wps_rep(spg, wps, x, ['C']*len(wps))
            xtals.append(xtal)
        xtals = bu1.optimize_xtals(xtals, add_db=False)
        assert len(xtals) == 2
        #builder.optimize_xtals(xtals, opt_type='local', ncpu=2)

    def test_opt_diamond(self):
        xtal = pyxtal()
        xtal.from_prototype('diamond')
        sub_xtal = xtal.subgroup_once(H=166, eps=1e-4)
        xtal, sim, _ = bu1.optimize_xtal(sub_xtal, add_db=False)
        assert sim < 1e-2

    #def test_ortho(self):
    #    xtal = pyxtal()
    #    xtal.from_spg_wps_rep(53,
    #                          ['4h', '4h', '4h'],
    #                          [2.365503,  3.005858, 12.789526,  0.003843,
    #                           0.414543,  0.009659, 0.050974,  0.0076,  0.815])
    #    xtal, sim, _ = bu1.optimize_xtal(xtal, opt_type='global')
    #    assert sim < 1e-2


    def test_diamond(self):
        print("test_diamond")
        xtal = pyxtal()
        xtal.from_spg_wps_rep(227, ['8a'], [3.6], ['C'])
        xtals = xtal.subgroup(group_type='t+k')[7:]
        print("\nFirst split", xtal.group.number, len(xtals))
        for i, xtal1 in enumerate(xtals):
            xtal1s = xtal1.subgroup(group_type='t+k', max_cell=4)
            print("\n2nd split", i, xtal1.group.number, len(xtal1s))
            for _xtal1 in xtal1s[:3]:
                _xtal1.optimize_lattice(standard=True)
                final = _xtal1.subgroup_once(group_type='t+k')
                if final is not None:
                    #header = "{:3d} => ".format(xtal.group.number)
                    #header += "{:3d} => ".format(xtal1.group.number)
                    #header += "{:3d} => ".format(_xtal1.group.number)
                    #header += "{:3d} ".format(final.group.number)
                    #print(final.get_xtal_string(header=header))
                    bu1.optimize_xtal(final, add_db=False)

if __name__ == "__main__":
    unittest.main()
