from __future__ import (nested_scopes, generators, division, absolute_import,
                        print_function, unicode_literals)
import os
import unittest
import pyNastran
from pyNastran.bdf.cards.baseCard import collapse_thru_by
from pyNastran.bdf.caseControlDeck import CaseControlDeck

testPath = pyNastran.__path__[0]
#print("testPath = %s" % testPath)
from pyNastran.bdf.test.test_bdf import run_bdf, run_all_files_in_folder


class Tester(unittest.TestCase):

    def run_bdf(self, folder, bdfFilename, xref=False, cid=None,
                meshForm='combined', debug=False):
        cid = 0
        #xref = False
        return run_bdf(folder, bdfFilename, xref=xref, cid=cid, isFolder=True,
                       meshForm=meshForm, debug=debug)

    def run_all_files_in_folder(self, folder, xref=False, cid=None, debug=False):
        run_all_files_in_folder(folder, xref=xref, cid=cid, debug=debug)


class TestBDF(Tester):
    def test_bdf_01(self):
        bdfFilename = os.path.join('solid_bending', 'solid_bending.bdf')
        folder = os.path.abspath(os.path.join(testPath, '..', 'models'))
        self.run_bdf(folder, bdfFilename)
        (fem1, fem2, diffCards2) = self.run_bdf(folder, bdfFilename, xref=True)

        for fem in [fem1, fem2]:
            assert len(fem.params) == 2, 'len(params) = %i' % len(fem.params)
            assert len(fem.coords) == 1, 'len(coords) = %i' % len(fem.coords)
            assert len(fem.nodes) == 72, 'len(nodes) = %i' % len(fem.nodes)
            assert len(fem.materials) == 1, 'len(materials) = %i' % len(fem.materials)
            assert len(fem.elements) == 186, 'len(elements) = %i' % len(fem.elements)
            assert len(fem.methods) == 0, 'len(methods) = %i' % len(fem.methods)
            assert len(fem.properties) == 1, 'len(properties) = %i' % len(fem.properties)

    def test_bdf_02(self):
        bdfFilename = os.path.join('plate_py', 'plate_py.dat')
        folder = os.path.abspath(os.path.join(testPath, '..', 'models'))
        self.run_bdf(folder, bdfFilename)
        (fem1, fem2, diffCards2) = self.run_bdf(folder, bdfFilename, xref=True)

        for fem in [fem1, fem2]:
            assert len(fem.coords) == 3, 'len(coords) = %i' % len(fem.coords)
            assert len(fem.params) == 6, 'len(params) = %i' % len(fem.params)
            assert len(fem.nodes) == 231, 'len(nodes) = %i' % len(fem.nodes)
            assert len(fem.materials) == 1, 'len(materials) = %i' % len(fem.materials)
            assert len(fem.elements) == 200, 'len(elements) = %i' % len(fem.elements)
            assert len(fem.methods) == 1, 'len(methods) = %i' % len(fem.methods)
            assert len(fem.properties) == 1, 'len(properties) = %i' % len(fem.properties)

    def test_bdf_03(self):
        bdfFilename = os.path.join('beam_modes', 'beam_modes.dat')
        folder = os.path.abspath(os.path.join(testPath, '..', 'models'))
        (fem1, fem2, diffCards2) = self.run_bdf(folder, bdfFilename)

        for fem in [fem1, fem2]:
            assert len(fem.params) == 6, 'len(params) = %i' % len(fem.params)
            assert len(fem.coords) == 1, 'len(coords) = %i' % len(fem.coords)
            assert len(fem.nodes) == 12, 'len(nodes) = %i' % len(fem.nodes)
            assert len(fem.materials) == 1, 'len(materials) = %i' % len(fem.materials)
            assert len(fem.elements) == 11, 'len(elements) = %i' % len(fem.elements)
            assert len(fem.methods) == 1, 'len(methods) = %i' % len(fem.methods)
            assert len(fem.properties) == 3, 'len(properties) = %i' % len(fem.properties)  ## PBEAML issue
        #self.run_bdf(folder, bdfFilename, xref=True) ## PBEAML is not supported

    def test_bdf_04(self):
        bdfFilename = 'testA.bdf'
        folder = os.path.abspath(os.path.join(testPath, 'bdf', 'test', 'unit'))
        self.run_bdf(folder, bdfFilename)
        #self.run_bdf(folder, bdfFilename, xref=True) ## PBEAML is not supported

class BaseCard_Test(Tester):
    def test_base_card_01_collapse_thru(self):
        """
        tests collapse_thru method used by SETx cards
        """
        data = [1, 2, 3, 4, 5, 10]
        expected = [1, u'THRU', 5, 10]
        self.assertEquals(collapse_thru_by(data),expected,
                          collapse_thru_by(data))

        data = [1, 3, 4, 5, 6, 17]
        expected = [1, 3, 4, 5, 6, 17]
        self.assertEquals(collapse_thru_by(data),expected,
                          collapse_thru_by(data))

        data = [1, 3, 4, 5, 6, 7, 17]
        expected = [1, 3, 4, 'THRU', 7, 17]
        self.assertEquals(collapse_thru_by(data),expected,
                          collapse_thru_by(data))

        data = [1, 3, 4, 6, 8, 10, 12, 14, 17]
        expected = [1, 3, 4, 'THRU', 14, 'BY', 2, 17]
        self.assertEquals(collapse_thru_by(data),expected,
                          collapse_thru_by(data))

        data = [1, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 101]
        expected = [1, 3, 4, 5, 6, 8, 'THRU', 22, 'BY', 2, 101]
        self.assertEquals(collapse_thru_by(data),expected,
                          collapse_thru_by(data))

        data = [1, 2, 3, 4, 5]
        expected = [1, 'THRU', 5]
        self.assertEquals(collapse_thru_by(data),expected,
                          collapse_thru_by(data))

        data = [5]
        expected = [5]
        self.assertEquals(collapse_thru_by(data),expected,
                          collapse_thru_by(data))

        data = [1,2,3,4,5, 7,9,11, 12,14,16]
        expected = [1, 'THRU', 5,
                    7, 9, 11,
                    12, 14, 16]
        self.assertEquals(collapse_thru_by(data),expected,
                          collapse_thru_by(data))

        data = [1,2]
        expected = [1, 2]
        self.assertEquals(collapse_thru_by(data),expected,
                          collapse_thru_by(data))

        data = [1,3,5,7,9,11]
        expected = [1, 'THRU', 11, 'BY', 2]
        self.assertEquals(collapse_thru_by(data),expected,
                          collapse_thru_by(data))

        data = [1,2,3,4]
        expected = [1, 'THRU', 4]
        self.assertEquals(collapse_thru_by(data),expected,
                          collapse_thru_by(data))

        data = [1,2,3]
        expected = [1, 2, 3]
        self.assertEquals(collapse_thru_by(data),expected,
                          collapse_thru_by(data))

        data = [1, 2, 3, 4, 5, 6, 7, 8]
        expected = [1, 'THRU', 8]
        self.assertEquals(collapse_thru_by(data),expected,
                          collapse_thru_by(data))

class CaseControlTest(unittest.TestCase):
    def test_case_control_01(self):
        lines = ['SPC=2',
                 'MPC =3',
                 'STRESS= ALL',
                 'DISPLACEMENT(PLOT,PUNCH) = 8', ]

        deck = CaseControlDeck(lines)
        self.assertTrue(deck.has_parameter(0, 'SPC'))
        self.assertTrue(deck.has_parameter(0, 'sPC'))
        self.assertFalse(deck.has_parameter(0, 'JUNK'))
        #print("get_subcase_parameter(MPC) 3 = ", deck.get_subcase_parameter(
        #    0, 'MPC'))

        deck.add_parameter_to_global_subcase('GPFORCE = 7')

        deck.create_new_subcase(1)
        deck.create_new_subcase(2)

        deck.add_parameter_to_local_subcase(1, 'STRAIN = 7')

        out = deck.get_subcase_parameter(0, 'GPFORCE')

        deck.add_parameter_to_local_subcase(1, 'ANALYSIS = SAERO')
        deck.add_parameter_to_local_subcase(2, 'ANALYSIS = STATIC')
        out = deck.get_subcase_parameter(2, 'ANALYSIS')

        deck.add_parameter_to_local_subcase(1, 'SET 1 = 100')
        deck.add_parameter_to_local_subcase(1, 'SET 2 = 200')

        lines = ['DISPLACEMENT(PLOT,PUNCH) = 8',
                 'GPFORCE = 7',
                 'MPC = 3',
                 'SPC = 2',
                 'STRESS = ALL',
                 'SUBCASE 1',
                 '    SET 1 = 100',
                 '    SET 2 = 200',
                 '    ANALYSIS = SAERO',
                 '    STRAIN = 7',
                 'SUBCASE 2',
                 '    ANALYSIS = STATIC',]
        deck_string = '%s' % deck
        deck_lines = deck_string.strip().splitlines()
        self.assertEqual(lines, deck_lines)


if __name__ == '__main__':
    unittest.main()
