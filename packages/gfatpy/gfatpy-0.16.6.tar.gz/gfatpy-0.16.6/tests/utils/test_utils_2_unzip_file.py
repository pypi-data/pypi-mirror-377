from pathlib import Path
from tkinter import N
from gfatpy.utils.io import unzip_file

ZIP_FILE = Path(r"tests\datos\RAW\alhambra\2023\02\22\DC_20230222_0030.zip")

def test_unzip_all():
    tmp_path = unzip_file(ZIP_FILE)
    assert tmp_path is not None
    unzipped_path = Path(tmp_path.name)
    assert unzipped_path.exists()
    assert len(list(unzipped_path.rglob("*"))) == 12
    tmp_path.cleanup()

def test_unzip_pattern():
    tmp_path = unzip_file(ZIP_FILE, pattern_or_list=r'\.\d+$')
    assert tmp_path is not None
    unzipped_path = Path(tmp_path.name)    
    assert unzipped_path.exists()
    assert len(list(unzipped_path.glob("*"))) == 1
    assert len(list(unzipped_path.rglob("*"))) == 11
    tmp_path.cleanup()

def test_unzip_pattern2():
    tmp_path = unzip_file(ZIP_FILE, pattern_or_list=['temp.dat'])
    assert tmp_path is not None
    unzipped_path = Path(tmp_path.name)    
    assert unzipped_path.exists()
    assert len(list(unzipped_path.glob("*"))) == 1
    assert len(list(unzipped_path.rglob("*"))) == 2
    tmp_path.cleanup()
