from pathlib import Path
from datetime import date
from importlib.metadata import version
import pandas as pd
from ir_pell_accepts.checks import validate_filename, validate_extension
from ir_pell_accepts.helper import adjust_term

def construct_results_filename(file: Path, append_today: bool = True, append_version: bool = True) -> Path:
    """
    Create the file name for the results file and append today's date and package version by default.

    Params
    ------
    file : Path object from pathlib
        The file name including extension, not a full path, just the name.
    append_today : bool
        Add today's date to the file name (e.g. 11-25-2025)
    append_version : bool
        Append the version of the python package used (e.g. v0.1.0)
    """
    file = validate_filename(file)
    todays_date = date.today().strftime("%Y-%m-%d") if append_today else None
    pkg_version = "v" + version("ir_pell_accepts") if append_version else None

    # Remove None's/blanks
    parts = [file.stem, todays_date, pkg_version]
    parts = [p for p in parts if p]

    return Path("_".join(parts) + file.suffix)


def output_results(df: pd.DataFrame, file_path: Path, append_today: bool = True, append_version: bool = True) -> None:
    """
    Output results to excel, csv, or tab/.txt
    """
    file = file_path.name
    if not file:
        raise ValueError(f"file_path must have a filename: {file_path}")
    
    file = construct_results_filename(file, append_today=append_today, append_version=append_version)
    
    outfile = file_path.parent / file
    ext = validate_extension(outfile.suffix)

    if ext == ".xlsx":
        with pd.ExcelWriter(
            outfile,
            engine="openpyxl",
            mode="a",
            if_sheet_exists="replace"
        ) as writer:
        
            df.to_excel(writer, sheet_name="Python Output", index=False)
    if ext == ".csv":
        df.to_csv(outfile, index=False)
    if ext == ".txt":
        df.to_csv(outfile, index=False, sep="\t")
