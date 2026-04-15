
import pandas as pd

def load_plates(
    folder_dict: dict,
    filename: str = "PlateResults.txt",
    delimiter: str = "\t",
    skiprows: int = 7,
    header: int = 1,
):
    """
    Load and concatenate PlateResults files from multiple measurement folders.

    Args:
        folder_dict (dict): Mapping each experiment (file/folder) to an ID.
        filename (str): Name of the target file inside each folder.
        delimiter (str): Field delimiter used in the file. Default: '\\t' 
            (tab-separated).
        skiprows (int): Number of rows to skip before the header. Default: 8.
        header (int): Row number to use as column names. Default: 1.

    Returns:
        pd.DataFrame: Concatenated dataframe with an added 'File ID' column.
    """
    
    all_dfs = []

    for file_id, folder_path in folder_dict.items():
        file_path = f"{folder_path}/{filename}"
        df_partial = pd.read_csv(
            file_path,
            sep=delimiter,
            skiprows=skiprows,
            header=header,
            keep_default_na=False,
            low_memory=False,
        )
        df_partial["File ID"] = file_id
        all_dfs.append(df_partial)

    return pd.concat(all_dfs, ignore_index=True)


import string

def map_num_to_letter(df, col='Row', inplace=True):
    """
    Maps integer row numbers (1–26) to uppercase alphabet letters.

    Args:
        df (pd.DataFrame): Input DataFrame.
        col (str): Column to remap. Defaults to 'Row'.
        inplace (bool): Modify df in place (True) or return a copy (False).

    Returns:
        pd.DataFrame 
    """
    row_map = {
        i: letter for i, 
               letter in enumerate(string.ascii_uppercase, start=1)
    }

    if inplace:
        df[col].replace(row_map, inplace=True)
        return None
    else:
        result = df.copy()
        result[col] = result[col].replace(row_map)
        return result