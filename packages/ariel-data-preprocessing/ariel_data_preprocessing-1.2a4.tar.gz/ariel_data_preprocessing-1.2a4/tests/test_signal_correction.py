'''Unittests for signal correction class'''

import unittest

import numpy as np
import pandas as pd
import h5py

from ariel_data_preprocessing.signal_correction import SignalCorrection
from ariel_data_preprocessing.calibration_data import CalibrationData
from ariel_data_preprocessing.utils import get_planet_list

class TestSignalCorrection(unittest.TestCase):

    def setUp(self):

        self.input_data_path = 'tests/test_data/raw'
        self.output_data_path = 'tests/test_data/corrected'
        self.planet = '342072318'
        self.planet_path = f'{self.input_data_path}/train/{self.planet}'

        self.airs_frames = 50
        self.fgs_frames = 50
        self.cut_inf = 39
        self.cut_sup = 321

        # Load and prep signal data
        self.fgs_signal = pd.read_parquet(
            f'{self.planet_path}/FGS1_signal_0.parquet'
        ).to_numpy().reshape(self.fgs_frames, 32, 32)

        self.fgs_signal = self.fgs_signal.astype(np.float64)

        self.airs_signal = pd.read_parquet(
            f'{self.planet_path}/AIRS-CH0_signal_0.parquet'
        ).to_numpy().reshape(self.airs_frames, 32, 356)[:, :, self.cut_inf:self.cut_sup]

        self.airs_signal = self.airs_signal.astype(np.float64)

        self.signal_correction = SignalCorrection(
            input_data_path=self.input_data_path,
            output_data_path=self.output_data_path,
            airs_frames=self.airs_frames,
            fgs_frames=self.fgs_frames,
        )

        self.calibration_data = CalibrationData(
            input_data_path=self.input_data_path,
            planet_path=self.planet_path,
            airs_frames=self.airs_frames,
            fgs_frames=self.fgs_frames,
            cut_inf=self.cut_inf,
            cut_sup=self.cut_sup
        )

    def test_signal_correction(self):
        '''Test full signal correction pipeline'''

        self.signal_correction.run()

        with h5py.File(f'{self.output_data_path}/train.h5', 'r') as hdf:

            self.assertEqual(len(hdf[self.planet]), 4)
            self.assertTrue('AIRS-CH0_signal' in hdf[self.planet])
            self.assertTrue('FGS1_signal' in hdf[self.planet])
            self.assertTrue(hdf[self.planet]['AIRS-CH0_signal'].shape[0] == self.airs_signal.shape[0]//2)
            self.assertTrue(hdf[self.planet]['AIRS-CH0_signal'].shape[1] == self.airs_signal.shape[1])
            self.assertTrue(hdf[self.planet]['AIRS-CH0_signal'].shape[2] == self.airs_signal.shape[2])
            self.assertTrue(hdf[self.planet]['FGS1_signal'].shape[0] == self.fgs_signal.shape[0]//2)
            self.assertTrue(hdf[self.planet]['FGS1_signal'].shape[1] == self.fgs_signal.shape[1])
            self.assertTrue(hdf[self.planet]['FGS1_signal'].shape[2] == self.fgs_signal.shape[2])


    def test_planet_list(self):
        '''Test planet list extraction'''

        planet_list = get_planet_list(self.input_data_path)

        self.assertTrue(isinstance(planet_list, list))
        self.assertTrue(len(planet_list) > 0)
        self.assertTrue(all(isinstance(p, str) for p in planet_list))
        self.assertEqual(planet_list[0], '342072318')


    def test_adc_conversion(self):
        '''Test ADC conversion'''

        corrected_airs = self.signal_correction._ADC_convert(
            self.airs_signal
        )

        corrected_fgs = self.signal_correction._ADC_convert(
            self.fgs_signal
        )

        self.assertTrue(corrected_airs.shape == self.airs_signal.shape)
        self.assertTrue(corrected_fgs.shape == self.fgs_signal.shape)


    def test_mask_hot_dead(self):
        '''Test hot/dead pixel masking'''

        masked_airs = self.signal_correction._mask_hot_dead(
            self.airs_signal,
            self.calibration_data.dead_airs,
            self.calibration_data.dark_airs
        )

        masked_fgs = self.signal_correction._mask_hot_dead(
            self.fgs_signal,
            self.calibration_data.dead_fgs,
            self.calibration_data.dark_fgs
        )

        self.assertTrue(masked_airs.shape == self.airs_signal.shape)
        self.assertTrue(masked_fgs.shape == self.fgs_signal.shape)
        self.assertTrue(isinstance(masked_airs, np.ma.MaskedArray))
        self.assertTrue(isinstance(masked_fgs, np.ma.MaskedArray))


    def test_linear_correction(self):
        '''Test linearity correction'''

        corrected_airs = self.signal_correction._apply_linear_corr(
            self.calibration_data.linear_corr_airs,
            self.airs_signal
        )

        corrected_fgs = self.signal_correction._apply_linear_corr(
            self.calibration_data.linear_corr_fgs,
            self.fgs_signal
        )

        self.assertTrue(corrected_airs.shape == self.airs_signal.shape)
        self.assertTrue(corrected_fgs.shape == self.fgs_signal.shape)
    

    def test_dark_subtraction(self):
        '''Test dark frame subtraction'''

        dark_subtracted_airs = self.signal_correction._clean_dark(
            self.airs_signal.astype(np.float64),
            self.calibration_data.dead_airs,
            self.calibration_data.dark_airs,
            self.calibration_data.dt_airs
        )

        dark_subtracted_fgs = self.signal_correction._clean_dark(
            self.fgs_signal.astype(np.float64),
            self.calibration_data.dead_fgs,
            self.calibration_data.dark_fgs,
            self.calibration_data.dt_fgs
        )

        self.assertTrue(dark_subtracted_airs.shape == self.airs_signal.shape)
        self.assertTrue(dark_subtracted_fgs.shape == self.fgs_signal.shape)


    def test_cds_subtraction(self):
        '''Test CDS subtraction'''

        cds_airs = self.signal_correction._get_cds(
            self.airs_signal
        )

        cds_fgs = self.signal_correction._get_cds(
            self.fgs_signal
        )

        self.assertTrue(cds_airs.shape[0] == self.airs_signal.shape[0]//2)
        self.assertTrue(cds_fgs.shape[0] == self.fgs_signal.shape[0]//2)


    def test_flat_field_correction(self):
        '''Test flat field correction'''

        flat_corrected_airs = self.signal_correction._correct_flat_field(
            self.airs_signal,
            self.calibration_data.flat_airs,
            self.calibration_data.dead_airs
        )

        flat_corrected_fgs = self.signal_correction._correct_flat_field(
            self.fgs_signal,
            self.calibration_data.flat_fgs,
            self.calibration_data.dead_fgs
        )

        self.assertTrue(flat_corrected_airs.shape == self.airs_signal.shape)
        self.assertTrue(flat_corrected_fgs.shape == self.fgs_signal.shape)