import subprocess
import sys
from pathlib import Path
import os

notebook_path = Path(
    r"C:\Users\ptkaczyk\OneDrive - Crido\20260715_ self scrapowanie tge\scrap_test.ipynb"
)

if not notebook_path.exists():
    raise FileNotFoundError(f"Nie znaleziono notebooka: {notebook_path}")

s_date_input = input("Podaj datę startu w formacie rrrr.mm.dd: ")
e_date_input = input("Podaj datę końca w formacie rrrr.mm.dd: ")
source_type_input = input("local - 1 \n request - 2")


env = os.environ.copy()
env["S_DATE_INPUT"] = s_date_input
env["E_DATE_INPUT"] = e_date_input
env["SOURCE_TYPE_INPUT"] = source_type_input

try:

    subprocess.run(
        [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--inplace",
            str(notebook_path),
            "--ExecutePreprocessor.timeout=-1",
        ],
        check=True,
        env=env
    )

    print(f"Notebook wykonany i nadpisany: {notebook_path}")

except: 
    input("Błąd")

input("zakończono")