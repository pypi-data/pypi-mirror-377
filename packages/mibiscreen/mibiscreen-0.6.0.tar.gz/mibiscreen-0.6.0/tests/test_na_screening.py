#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testing analysis module on NA screening of mibiscreen.

@author: Alraune Zech
"""

import numpy as np
import pandas as pd
import pytest
from mibiscreen.analysis.sample.screening_NA import electron_balance
from mibiscreen.analysis.sample.screening_NA import oxidators
from mibiscreen.analysis.sample.screening_NA import reductors
from mibiscreen.analysis.sample.screening_NA import sample_NA_screening
from mibiscreen.analysis.sample.screening_NA import sample_NA_traffic
from mibiscreen.data.example_data.example_data import example_data


class TestReductors:
    """Class for testing reductors analysis module on NA screening of mibipret."""

    data = example_data(with_units = False)
    data_empty = pd.Series(
                        data = np.arange(4),
                        name = 'empyt_data',
                        dtype = float
                        )

    columns = ['sample_nr', 'sulfate', 'benzene']
    units = [' ','mg/L', 'ug/L']
    s01 = ['2000-001', 748, 263]
    s02 = ['2000-002', 548, ]
    data_nonstandard = pd.DataFrame([units,s01,s02],columns = columns)

    def test_reductors_01(self):
        """Testing routine reductors().

        Correct calculation of total amount of reductors.
        """
        tot_reduct_test = 27.956808208823354
        tot_reduct = np.sum(reductors(self.data))

        assert (tot_reduct - tot_reduct_test)<1e-5
        # assert np.sum(tot_reduct.values - tot_reduct_example_data.values)<1e-5

    def test_reductors_02(self):
        """Testing routine reductors().

        Correct handling when no EA data is provided.
        """
        with pytest.raises(ValueError):
            reductors(self.data_empty)

    def test_reductors_03(self):
        """Testing routine reductors().

        Correct handling when unknown group of EA are provided.
        """
        with pytest.raises(ValueError):
            reductors(self.data,ea_group = 'test')

    def test_reductors_04(self):
        """Testing routine reductors().

        Testing Error message that data is not in standard format.
        """
        with pytest.raises(ValueError):
            reductors(self.data_nonstandard)

    def test_reductors_05(self):
        """Testing routine reductors().

        Testing include option adding calculated values as column to data.
        """
        data_test = self.data.copy()
        reductors(data_test,include = True)
        assert data_test.shape[1] == self.data.shape[1]+1 and "total_reductors" in data_test.columns


    def test_reductors_06(self,capsys):
        """Testing routine reductors().

        Testing verbose flag.
        """
        reductors(self.data,verbose=True)
        out,err=capsys.readouterr()

        assert len(out)>0


class TestOxidators:
    """Class for testing oxidators analysis module on NA screening of mibipret."""

    data = example_data(with_units = False)
    data_empty = pd.Series(
                        data = np.arange(4),
                        name = 'empyt_data',
                        dtype=float)

    columns = ['sample_nr', 'sulfate', 'benzene']
    units = [' ','mg/L', 'ug/L']
    s01 = ['2000-001', 748, 263]
    s02 = ['2000-002', 548, ]
    data_nonstandard = pd.DataFrame([units,s01,s02],columns = columns)

    def test_oxidators_01(self):
        """Testing routine oxidators().

        Correct calculation of total amount of oxidators for standard contaminant
        group BTEXIIN.
        """
        tot_oxi_test = 10.369793079245106
        tot_oxi = np.sum(oxidators(self.data))

        assert (tot_oxi - tot_oxi_test)<1e-5

    def test_oxidators_02(self):
        """Testing routine oxidators().

        Correct calculation of total amount of oxidators for BTEX.
        """
        tot_oxi_test = 3.5295281756799395
        tot_oxi = np.sum(oxidators(self.data,contaminant_group='BTEX'))

        assert (tot_oxi - tot_oxi_test)<1e-5


    def test_oxidators_03s(self):
        """Testing routine oxidators().

        Correct handling when no contaminant data is provided.
        """
        with pytest.raises(ValueError):
            oxidators(self.data_empty)


    def test_oxidators_04(self):
        """Testing routine oxidators().

        Correct handling when unknown group of contaminants are provided.
        """
        with pytest.raises(ValueError):
            oxidators(self.data,contaminant_group = 'test')

    def test_oxidators_05(self):
        """Testing Error message that given data type not defined."""
        with pytest.raises(ValueError):  #, match = "Data not in standardized format. Run 'standardize()' first."):
            oxidators(self.data_nonstandard)


    def test_oxidators_06(self):
        """Testing routine oxidators().

        Testing inplace option adding calculated values as column to data.
        """
        data_test = self.data.copy()
        oxidators(data_test,include = True)
        # assert names.name_total_oxidators in data_test.columns
        assert data_test.shape[1] == self.data.shape[1]+1 and "total_oxidators_BTEXIIN" in data_test.columns


    def test_oxidators_07(self,capsys):
        """Testing routine oxidators().

        Testing verbose flag.
        """
        oxidators(self.data,verbose=True)
        out,err=capsys.readouterr()

        assert len(out)>0


class TestElectronBalance:
    """Class for testing electron_balance analysis module on NA screening of mibipret."""

    data = example_data(with_units = False)

    data_na = pd.concat([pd.Series(data = [11.819184,0.525160, 0.347116, 15.265349], name = 'total_reductors'),
                         pd.Series(data = [1.5663,3.70051, 3.00658, 2.09641], name = 'total_oxidators')],
                        axis =1)


    def test_electron_balance_01(self):
        """Testing routine electron_balance().

        Correct calculation of electron balance from data not containing
        amounts of reductors and oxidators (have to be calculated first).
        """
        e_bal_test = 15.087302683658793
        e_bal = np.sum(electron_balance(self.data))

        assert (e_bal - e_bal_test)<1e-5

    def test_electron_balance_02(self):
        """Testing routine electron_balance().

        Correct calculation of total amount of electron balance from
        dataframe containing amounts of reductors and oxidators.
        """
        e_bal_test = 15.087302683658793
        e_bal = np.sum(electron_balance(self.data_na))

        assert (e_bal - e_bal_test)<1e-5

    def test_electron_balance_03(self,capsys):
        """Testing routine electron_balance().

        Testing 'include' option adding calculated values as column to data.
        """
        data_test = self.data_na.copy()
        electron_balance(data_test,include = True)
        assert data_test.shape[1] == self.data_na.shape[1]+1 and 'e_balance' in data_test.columns

    def test_electron_balance_04(self,capsys):
        """Testing routine electron_balance().

        Testing verbose flag.
        """
        electron_balance(self.data,verbose=True)
        out,err=capsys.readouterr()

        assert len(out)>0


class TestNATraffic:
    """Class for testing NA_traffic analysis module on NA screening of mibipret."""

    data = example_data(with_units = False)

    data_na = pd.concat([pd.Series(data = [11.819184,0.525160, 0.347116, 15.265349], name = 'total_reductors'),
                         pd.Series(data = [1.5663,3.70051, 3.00658, 2.09641], name = 'total_oxidators')],
                        axis=1)


    def test_sample_NA_traffic_01(self):
        """Testing routine sample_NA_traffic().

        Correct calculation of NA traffic light based on electron balance.
        When data does not contain electron balance (has to be calculated
        from reductors and oxidators).
        """
        na_traffic_test = ['green','red','red','green']
        na_traffic = sample_NA_traffic(self.data)

        assert np.all(na_traffic.values == na_traffic_test)

    def test_sample_NA_traffic_02(self):
        """Testing routine sample_NA_traffic().

        Correct calculation of NA traffic light based on electron balance when
        dataframe contains values of electron_balance.
        """
        na_traffic_test = ['green','red','red','green']
        na_traffic = sample_NA_traffic(self.data_na)

        assert np.all(na_traffic.values == na_traffic_test)

    def test_sample_NA_traffic_03(self,capsys):
        """Testing routine sample_NA_traffic().

        Testing 'include' option adding calculated values as column to data.
        """
        data_test = self.data_na.copy()
        sample_NA_traffic(data_test,include = True)
        assert data_test.shape[1] == self.data_na.shape[1]+1 and "na_traffic_light" in data_test.columns

    def test_sample_NA_traffic_04(self,capsys):
        """Testing routine sample_NA_traffic().

        Testing verbose flag.
        """
        sample_NA_traffic(self.data,verbose=True)
        out,err=capsys.readouterr()

        assert len(out)>0

class TestScreeningNA:
    """Class for testing sample_NA_screening analysis module on NA screening of mibipret."""

    data = example_data(with_units = False)

    def test_sample_NA_screening_01(self):
        """Testing routine sample_NA_screening().

        Correct calculation of total amount of reductors.
        """
        na_data = sample_NA_screening(self.data)

        assert na_data.shape == (4,7)

    def test_sample_NA_screening_02(self,capsys):
        """Testing routine sample_NA_screening().

        Testing verbose flag.
        """
        sample_NA_screening(self.data,verbose=True)
        out,err=capsys.readouterr()

        assert len(out)>0

