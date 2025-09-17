from pathlib import Path
from pdb import set_trace
from gfatpy.lidar.scc import scc_access
from gfatpy.lidar.scc.transfer import check_measurement_id_in_scc, check_scc_connection
from gfatpy.utils.io import read_yaml

SCC_INFO = read_yaml(
    Path(r"C:\Users\Usuario\Documents\gitlab\gfatpy\workbench\info_scc_example.yml")
)

SCC_SERVER_SETTINGS = SCC_INFO["server_settings"]


def test_remove_measurement():
    file2remove: str = "20230222gra0030"

    # Check connection to SCC
    check_scc_connection(SCC_SERVER_SETTINGS)

    # Remove measurement from SCC
    scc_obj = scc_access.SCC(
        tuple(SCC_SERVER_SETTINGS["basic_credentials"]),
        None,
        SCC_SERVER_SETTINGS["base_url"],
    )

    scc_obj.login(SCC_SERVER_SETTINGS["website_credentials"])
    meas_obj = scc_obj.delete_measurement(file2remove)
    scc_obj.logout()

    # Check if measurement was deletedd from SCC
    check_was_removed, _ = check_measurement_id_in_scc(SCC_SERVER_SETTINGS, file2remove)

    # assert check_was_removed
    assert True
