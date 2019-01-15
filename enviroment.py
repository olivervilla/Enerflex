"""
Enviroment: contiene constantes utiles para el proyecto
"""
import os


class Address:
    """
    Address: Contiene las rutas a las carpetas de proyecto
    """


    __path = os.path.realpath(__file__)
    MAIN_FOLDER = __path[:__path.find('enviroment.py')]
    BACKUP_DAILY_FOLDER = os.path.join(MAIN_FOLDER, 'backup\\daily\\')
    DATA_FOLDER = os.path.join(MAIN_FOLDER, 'data\\')
    INITS_FOLDER = os.path.join(MAIN_FOLDER, 'inits\\')
    LOGS_FOLDER = os.path.join(MAIN_FOLDER, 'logs\\')
    TEST_FOLDER = os.path.join(MAIN_FOLDER, 'test\\')
    UTIL_FOLDER = os.path.join(MAIN_FOLDER, 'util\\')
    DATABASE_FOLDER = os.path.join(MAIN_FOLDER, 'enerflex.db')
    BACKUP_MONTHLY_FOLDER = os.path.join(MAIN_FOLDER, 'backup\\monthly\\')

class Keys:
    """
    Keys: Contiene listas con las keywords de los pozos
    """


    DATABASE_KEYS = [
        'id', 'name', 'time', 'date', 
        'ptp', 'ptr', 'pld', 'ttp',
        'namecompresor_1', 'etm_1', 'pr_1', 'rpmp_1', 'fep_1', 'ttdp_1', 'prdp_1', 'ptsp_1', 'pttrp_1', 'pttpp_1', 'tagc_1', 'tad_1', 'fegc_1', 'fcgc_1', 
        'vgi_1', 'fcd_1', 'tgc_1', 'pegc_1', 'pdgc_1', 'td_1', 'ped_1', 'pdd_1', 'tpv_1', 'pld2_1', 'pts_1', 'tts_1', 'di_1', 'pc_1', 'df_1',
        'namecompresor_2', 'etm_2', 'pr_2', 'rpmp_2', 'fep_2', 'ttdp_2', 'prdp_2', 'ptsp_2', 'pttrp_2', 'pttpp_2', 'tagc_2', 'tad_2', 'fegc_2', 'fcgc_2',
        'vgi_2', 'fcd_2', 'tgc_2', 'pegc_2', 'pdgc_2', 'td_2', 'ped_2', 'pdd_2', 'tpv_2', 'pld2_2', 'pts_2', 'tts_2', 'di_2', 'pc_2', 'df_2'
    ]

    COMPRESSOR_KEYS = [
        'namecompresor', 'etm', 'pr', 'rpmp', 'fep', 'ttdp', 'prdp', 'ptsp', 'pttrp', 'pttpp', 'tagc', 'tad', 'fegc', 'fcgc',
        'vgi', 'fcd', 'tgc', 'pegc', 'pdgc', 'td', 'ped', 'pdd', 'tpv', 'pld2', 'pts', 'tts', 'di', 'pc', 'df'
    ]

    WELL_KEYS = [
        'name', 'time', 'date', 'ptp', 'ptr', 'pld', 'ttp'
    ]
