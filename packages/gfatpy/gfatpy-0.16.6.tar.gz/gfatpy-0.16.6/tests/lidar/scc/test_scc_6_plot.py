from pathlib import Path

from matplotlib import pyplot as plt

from gfatpy.lidar.scc.plot.product import SCC_elpp
from gfatpy.lidar.scc.plot.scc_zip import SCC_zipfile, SCC_raw

scc_id = 781
SCC_DIR = Path(f"./tests/datos/PRODUCTS/alhambra/scc/scc{scc_id}/2023/08/30/products")
OUTPUT_DIR = Path(f"./tests/datos/PRODUCTS/alhambra/scc/scc{scc_id}/2023/08/30/plots")

# def test_file_plot_raw():
#     scc_zipfile = SCC_DIR / "raw_20230830gra0315.zip"
#     scc_zip = SCC_zipfile(scc_zipfile)
    
#     scc_file = scc_zip.products[0]
#     range_limits = (0, 10)
#     assert isinstance(scc_file, SCC_raw)
#     figs, plotfiles = scc_file.plot(range_limits=range_limits, output_dir=OUTPUT_DIR, savefig=True, dpi=150)
#     assert isinstance(plotfiles, list)
#     assert isinstance(plotfiles[0], Path)
#     assert plotfiles[0].exists()      
#     scc_zip.remove_unzipped_dir()    
#     for fig_ in figs:
#         plt.close(fig_)


# def test_file_plot_elpp():
#     scc_zipfile = SCC_DIR / "preprocessed_20230830gra0315.zip"
#     scc_zip = SCC_zipfile(scc_zipfile)
#     scc_file = scc_zip.products[0]
#     range_limits = (0, 25)
#     normalization_range = (6, 7)    
#     assert isinstance(scc_file, SCC_elpp)
#     fig_, plotfile = scc_file.rayleight_fit(scc_id=scc_id, normalization_range=normalization_range ,range_limits=range_limits, output_dir=OUTPUT_DIR, savefig=True, dpi=150)
#     plt.close(fig_)
#     assert isinstance(plotfile, Path)
#     assert plotfile.exists()
#     scc_zip.remove_unzipped_dir()

def test_zip_plot_elda():
    scc_zipfile = SCC_DIR / "optical_20230830gra0315.zip"
    scc_zip = SCC_zipfile(scc_zipfile)
    plot = scc_zip.plot(output_dir=OUTPUT_DIR, dpi=150, range_limits=(0, 10))
    assert plot is not None 
    assert isinstance(plot, Path)
    assert plot.exists()
    # scc_zip.remove_unzipped_dir()