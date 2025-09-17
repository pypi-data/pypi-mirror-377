# from . import ffp_kljun2015
try:
    # from ffpkljun import *
    import ffpkljun as ffp_kljun2015
except ModuleNotFoundError:
    # print("ModuleNotFoundError: No module named 'ffpkljun'. Use 'pip install' or please contact moderator.")
    try:
        from ..ext_libs import FFP_Python as ffp_kljun2015# calc_footprint_FFP, calc_footprint_FFP_climatology
    except ModuleNotFoundError:
        print("ModuleNotFoundError: No module 'FFP_Python' found in ext_libs. Download it from 'https://footprint.kljun.net/' or please contact moderator.")
