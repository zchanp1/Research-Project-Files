import os

import numpy as np

from settings import MCF_SETTINGS_FILE, MCF_DEFAULT_SETTINGS, load_settings, RECORDING_SETTINGS_FILE, \
    RECORDING_DEFAULT_SETTINGS

mcf_settings = load_settings(MCF_SETTINGS_FILE, MCF_DEFAULT_SETTINGS)
recording_settings = load_settings(RECORDING_SETTINGS_FILE, RECORDING_DEFAULT_SETTINGS)

# Global variables
NB_CORES = 4
CENTRAL_CORE = mcf_settings['central_core'] - 1
CORES_INDEX_LIST = list(range(NB_CORES))
OUTER_CORES_INDEX_LIST = CORES_INDEX_LIST.copy()
OUTER_CORES_INDEX_LIST.pop(CENTRAL_CORE)

NB_GRATINGS_PER_CORE = mcf_settings['nb_gratings']
GRATING_IDX_MAX = NB_CORES * NB_GRATINGS_PER_CORE
CORE_TO_CENTER_DIST_UM = mcf_settings['core_to_center']  # (37μm)
GRATING_SPACING_M = mcf_settings['grating_spacing']  # (10mm)

NB_ITERATIONS = 10
RADII_MM = (30, 50, 70, 90, 110, np.inf)  # mm

radii_list = (None, 30, 50, 70, 90, 110)
phantoms = (None, 'Bare', 'Rigid', 'Eco30', 'Dragon30', 'Eco110', 'Dragon110')
phantom_materials = (None, 'Bare', 'Rigid', 'Eco', 'Dragon')
rail_materials = (None, 'Bare', 'DS10', 'DS20', 'DS30', 'SS940', 'SS950')

GRATING_SPACING_MM = int(GRATING_SPACING_M * 10 ** 3)
PHANTOM_SPACING_MM = 1  # (1mm)
SPACING_COEFF = int(GRATING_SPACING_MM / PHANTOM_SPACING_MM)


ARC_LENGTH_MM = 90  # mm = 190 positions 0 to 190mm
RAIL_LENGTH_MM = 85  # mm = 85 positions 0 to 85mm

NB_GRATINGS_IN_RAIL = 9
LOCALIZATION_GRATINGS_IN_RAIL = range(10, 19)

phantoms_dict = {
    'phantom_S_50': np.array([50, -70]),  # mm
    'phantom_S_70': np.array([70, -70]),  # mm
    'phantom_S_90': np.array([90, -70]),  # mm
    'phantom_S_110': np.array([110, -70]),
    'phantom_D_30': np.array([30, 110]), # mm
    'phantom_D_50': np.array([50, 70]),  # mm
    'phantom_D_90': np.array([90, 70]),  # mm
    'phantom_D_110': np.array([110, 70]),  # mm
    'dvrk_fins': None,
    'dvrk_side_pulling': None,
    'dvrk_side_sliding': None
}

# Plotting global variables
color_inclusive = ['#4477AA', '#66CCEE', '#228833', '#CCBB44', '#EE6677', '#AA3377']

# Saving parameters
SAVING_COLUMNS = ["date", "experiment_name", "start_time", "elapsed_time",
                  "wav0", "line_number", "wav_data", "curvatures", "labview_curvatures",
                  "index_first_grating", "index_last_grating", "phantom_type",
                  "compared_curvature", "rail_stiffness"]

# Core distribution
ANGLE_TO_NX = np.radians([0, 120, 240])
NB_RECORDED_DATA_MAX = 30

EXPERIMENT_ARGS = ['rail_material', 'phantom_material', 'compared_curvature', 'first_grating_idx', 'last_grating_idx']
EXPERIMENT_ARGS_TO_KEY = {'rail_material': '-RAIL-',
                          'phantom_material': '-PHANTOM-',
                          'compared_curvature': '-RADIUS-',
                          'first_grating_idx': '-MIN-',
                          'last_grating_idx': '-MAX-'}

LOCALIZATION_EXPERIMENT_ARGS_TO_KEY = {
    'phantom_name': '-PHANTOM-',
    'phantom_material': '-PHANTOM_MAT-',
    'rail_material': '-RAIL-',
    'first_grating_idx': '-MIN-',
    'last_grating_idx': '-MAX-',
    'experiment_id': '-ID-'}

LOCALIZATION_EXPERIMENT_ARGS_TO_KEY_REVERSED = {v: k for k, v in LOCALIZATION_EXPERIMENT_ARGS_TO_KEY.items()}

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
