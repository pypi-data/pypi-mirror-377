# to run reduced tests execute `TINT_FULL_TEST=0 python3 -m coverage run --source . -m unittest discover tests``
# to run    full tests execute `TINT_FULL_TEST=1 python3 -m coverage run --source . -m unittest discover tests``

import unittest
import numpy.testing as test
import pickle
import os
import Tintegrals as Tintegrals
from deglist import *

full_test = os.getenv('TINT_FULL_TEST')
print(full_test)
if full_test == '1':
    print("Running tests with full degList")
else:
    degList3 = degList3[:1]
    degList4 = degList4[:1]
    degList5 = degList5[:1]
    degList6 = degList6[:1]
    degList7 = degList7[:1]
    print("Running tests with reduced degList")

class numericTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(numericTest, self).__init__(*args, **kwargs)
        self.Tints3 = pickle.load(open('tests/Tints3.pkl', 'rb'))
        self.Tints4 = pickle.load(open('tests/Tints4.pkl', 'rb'))
        self.Tints5 = pickle.load(open('tests/Tints5.pkl', 'rb'))
        self.Tints6 = pickle.load(open('tests/Tints6.pkl', 'rb'))
        self.Tints7 = pickle.load(open('tests/Tints7.pkl', 'rb'))
    # mudim
    def test_getMudim(self):
        print(float(Tintegrals.getMudim()))
        test.assert_allclose(float(Tintegrals.getMudim()), 1)
    def test_getInclB0del(self):
        test.assert_equal(Tintegrals.getInclB0del(), True)
    # B0fin
    def test_b0fin0(self):
        test.assert_allclose(float(Tintegrals.B0fin(0, 0, 0)), 0.)
    def test_b0fin1(self):
        test.assert_allclose(float(Tintegrals.B0fin(0, 0, 10)), -1.302585093)
    def test_b0fin2(self):
        test.assert_allclose(float(Tintegrals.B0fin(0, 10, 0)), -1.302585093)
    def test_b0fin3(self):
        test.assert_allclose(float(Tintegrals.B0fin(0, 10, 10)), -2.302585093)
    def test_b0fin4(self):
        test.assert_allclose(float(Tintegrals.B0fin(0, 10, 15)), -2.518980417)
    def test_b0fin5(self):
        Tintegrals.setMudim(10)
        test.assert_allclose(float(Tintegrals.B0fin(0, 10, 10)), 0.)
        Tintegrals.setMudim(1)
    def test_b0fin6(self):
        Tintegrals.setMudim(10)
        test.assert_allclose(float(Tintegrals.B0fin(0, 10, 15)), -0.2163953243)
        Tintegrals.setMudim(1)
    def test_b0fin8(self):
        test.assert_raises(Exception, Tintegrals.B0fin, 1, 2, 3)
    # B0del
    def test_b0del0(self):
        test.assert_allclose(float(Tintegrals.B0del(0, 0, 0)), 0.)
    def test_b0del1(self):
        test.assert_allclose(float(Tintegrals.B0del(0, 0, 10)), 2.170830996)
    def test_b0del2(self):
        test.assert_allclose(float(Tintegrals.B0del(0, 10, 0)), 2.170830996)
    def test_b0del3(self):
        test.assert_allclose(float(Tintegrals.B0del(0, 10, 10)), 3.473416088)
    def test_b0del4(self):
        test.assert_allclose(float(Tintegrals.B0del(0, 10, 15)), 4.001892343)
    def test_b0del5(self):
        Tintegrals.setMudim(10)
        test.assert_allclose(float(Tintegrals.B0del(0, 10, 10)), 0.822467033)
        Tintegrals.config.mudim = 1
    def test_b0del6(self):
        Tintegrals.setMudim(10)
        test.assert_allclose(float(Tintegrals.B0del(0, 10, 15)), 0.8526746399)
        Tintegrals.setMudim(1)
    def test_b0del7(self):
        Tintegrals.setInclB0del(False)
        test.assert_allclose(float(Tintegrals.B0del(0, 1, 2)), 0)
        Tintegrals.setInclB0del(True)
    def test_b0del8(self):
        test.assert_raises(Exception, Tintegrals.B0del, 1, 2, 3)
    # T134
    def test_T134_0(self):
        test.assert_allclose(float(Tintegrals.T134fin(0, 0, 0)), 0.)
    def test_T134_1a(self):
        test.assert_allclose(float(Tintegrals.T134fin(1, 0, 0)), 5.9674011)
    def test_T134_1b(self):
        test.assert_allclose(float(Tintegrals.T134fin(0, 1, 0)), 5.9674011)
    def test_T134_1c(self):
        test.assert_allclose(float(Tintegrals.T134fin(0, 0, 1)), 5.9674011)
    def test_T134_2a(self):
        test.assert_allclose(float(Tintegrals.T134fin(0, 1, 1)), 8.644934067)
    def test_T134_2b(self):
        test.assert_allclose(float(Tintegrals.T134fin(1, 0, 1)), 8.644934067)
    def test_T134_2c(self):
        test.assert_allclose(float(Tintegrals.T134fin(1, 1, 0)), 8.644934067)
    def test_T134_3a(self):
        test.assert_allclose(float(Tintegrals.T134fin(0, 1, 2)), 14.63855321)
    def test_T134_3b(self):
        test.assert_allclose(float(Tintegrals.T134fin(1, 0, 2)), 14.63855321)
    def test_T134_3c(self):
        test.assert_allclose(float(Tintegrals.T134fin(1, 2, 0)), 14.63855321)
    def test_T134_4(self):
        test.assert_allclose(float(Tintegrals.T134fin(1, 1, 1)), 9.451540242)
    def test_T134_5a(self):
        test.assert_allclose(float(Tintegrals.T134fin(2, 1, 1)), 13.14289398)
    def test_T134_5b(self):
        test.assert_allclose(float(Tintegrals.T134fin(1, 2, 1)), 13.14289398)
    def test_T134_5c(self):
        test.assert_allclose(float(Tintegrals.T134fin(1, 1, 2)), 13.14289398)
    def test_T134_6(self):
        test.assert_allclose(float(Tintegrals.T134fin(1, 2, 3)), 28.3986482)
    def test_T134_uv2(self):
        test.assert_allclose(float(Tintegrals.T134uv2(1, 2, 3)), 7)
    def test_T134_uv1(self):
        test.assert_allclose(float(Tintegrals.T134uv1(1, 2, 3)), -4.320198641)
    def test_T134sub_1(self):
        test.assert_allclose(float(Tintegrals.T134fin(1, 2, 3)), 28.3986482)
    def test_T134sub_2(self):
        Tintegrals.setInclB0del(False)
        test.assert_allclose(float(Tintegrals.T134fin(1, 2, 3)), 2.635602969)
        Tintegrals.setInclB0del(True)
    def test_T111(self):
        print("\ntesting T111")
        for massconfig in degList3:
            test.assert_allclose(float(Tintegrals.T111(*massconfig)), float(self.Tints3['T111'][degList3.index(massconfig)]))
    def test_T113(self):
        print("\ntesting T113")
        for massconfig in degList3:
            test.assert_allclose(float(Tintegrals.T113(*massconfig)), float(self.Tints3['T113'][degList3.index(massconfig)]))
    def test_T1113(self):
        print("\ntesting T1113")
        for massconfig in degList4:
            test.assert_allclose(float(Tintegrals.T1113(*massconfig)), float(self.Tints4['T1113'][degList4.index(massconfig)]))
    def test_T1133(self):
        print("\ntesting T1133")
        for massconfig in degList4:
            test.assert_allclose(float(Tintegrals.T1133(*massconfig)), float(self.Tints4['T1133'][degList4.index(massconfig)]))
    def test_T1134(self):
        print("\ntesting T1134")
        for massconfig in degList4:
            test.assert_allclose(float(Tintegrals.T1134(*massconfig)), float(self.Tints4['T1134'][degList4.index(massconfig)]))
    def test_T11113(self):
        print("\ntesting T11113")
        for massconfig in degList5:
            test.assert_allclose(float(Tintegrals.T11113(*massconfig)), float(self.Tints5['T11113'][degList5.index(massconfig)]))
    def test_T11133(self):
        print("\ntesting T11133")
        for massconfig in degList5:
            test.assert_allclose(float(Tintegrals.T11133(*massconfig)), float(self.Tints5['T11133'][degList5.index(massconfig)]))
    def test_T11134(self):
        print("\ntesting T11134")
        for massconfig in degList5:
            test.assert_allclose(float(Tintegrals.T11134(*massconfig)), float(self.Tints5['T11134'][degList5.index(massconfig)]))
    def test_T11334(self):
        print("\ntesting T11334")
        for massconfig in degList5:
            test.assert_allclose(float(Tintegrals.T11334(*massconfig)), float(self.Tints5['T11334'][degList5.index(massconfig)]))
    def test_T111113(self):
        print("\ntesting T111113")
        for massconfig in degList6:
            test.assert_allclose(float(Tintegrals.T111113(*massconfig)), float(self.Tints6['T111113'][degList6.index(massconfig)]))
    def test_T111133(self):
        print("\ntesting T111133")
        for massconfig in degList6:
            test.assert_allclose(float(Tintegrals.T111133(*massconfig)), float(self.Tints6['T111133'][degList6.index(massconfig)]))
    def test_T111134(self):
        print("\ntesting T111134")
        for massconfig in degList6:
            test.assert_allclose(float(Tintegrals.T111134(*massconfig)), float(self.Tints6['T111134'][degList6.index(massconfig)]))
    def test_T111333(self):
        print("\ntesting T111333")
        for massconfig in degList6:
            test.assert_allclose(float(Tintegrals.T111333(*massconfig)), float(self.Tints6['T111333'][degList6.index(massconfig)]))
    def test_T111334(self):
        print("\ntesting T111334")
        for massconfig in degList6:
            test.assert_allclose(float(Tintegrals.T111334(*massconfig)), float(self.Tints6['T111334'][degList6.index(massconfig)]))
    def test_T113344(self):
        print("\ntesting T113344")
        for massconfig in degList6:
            test.assert_allclose(float(Tintegrals.T113344(*massconfig)), float(self.Tints6['T113344'][degList6.index(massconfig)]))
    def test_T1111134(self):
        print("\ntesting T1111134")
        for massconfig in degList7:
            test.assert_allclose(float(Tintegrals.T1111134(*massconfig)), float(self.Tints7['T1111134'][degList7.index(massconfig)]))
    def test_T1111334(self):
        print("\ntesting T1111334")
        for massconfig in degList7:
            test.assert_allclose(float(Tintegrals.T1111334(*massconfig)), float(self.Tints7['T1111334'][degList7.index(massconfig)]))
    def test_T1113334(self):
        print("\ntesting T1113334")
        for massconfig in degList7:
            test.assert_allclose(float(Tintegrals.T1113334(*massconfig)), float(self.Tints7['T1113334'][degList7.index(massconfig)]))
    def test_T1113344(self):
        print("\ntesting T1113344")
        for massconfig in degList7:
            test.assert_allclose(float(Tintegrals.T1113344(*massconfig)), float(self.Tints7['T1113344'][degList7.index(massconfig)]))
