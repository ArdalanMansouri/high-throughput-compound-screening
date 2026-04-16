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
    import pandas as pd

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

    mapped = df[col].map(row_map) # Map the column values using the row_map

    if inplace:
        df[col] = mapped
        return None
    else:
        result = df.copy()
        result[col] = mapped
        return result
    
def plate_normalizer (
        df_untreated, df_treated, plate_identifier, 
        column_for_normalization, func="mean"):  
    """ A function for normalizing plate to plate variation in both treated 
    (control) and untreated(sample) groups and return the outcome as separate 
    dataframes.
    By using two variable at the same time, both outcomes can be retrieved. 
    Example: df_control, df_sample = plate_normalizer(...)
    
    Args:
        df_untreated: The df containing the untreated samples 
            (i.e., df_Control)
        df_treated: The df containig the samples that have been treated with 
            compounds (i.e., df_Sample)
        plate_identifer: The plate identifier is the column with the ID of 
            each separate plate (i.e., File ID)
        func: the aggregation function that want to use for normalization. 
            For example: "mean" or "median" 

    Returns:
        final_untreated_df: The normalized df for the untreated samples        
    """

    import pandas as pd 
    # Distinguishing treated and untreated samples after merging the data at 
    # the end. 
    df_untreated = df_untreated.copy()
    df_untreated["Group"] = "Untreated"
    df_treated = df_treated.copy()
    df_treated["Group"] = "Treated"
 
    # Determine the total mean/median for the column we want to normalize.
    total_mean_control= df_untreated[column_for_normalization].agg(func)
   
    # Make normalization factor for the controls of each plate.
    all_plates_NormalizerFactors = [] # container for the outcome of the loop.

    # list of ids for each plate (1 to 5).
    all_plates_identifiers = df_untreated[plate_identifier].unique() 
    for identifier in all_plates_identifiers:
        # calculate the average value for the selected column in each plate.
        plate_mean_control=df_untreated[
            column_for_normalization
        ].loc[df_untreated[plate_identifier]== identifier].agg(func)

        # Make a normalization factor by dividing the average value of all 
        # plates by the average value of each plate/
        plate_mean_NormalizationFactor= total_mean_control/plate_mean_control
        
        # Add the nomalization factor to a list.
        all_plates_NormalizerFactors.append(plate_mean_NormalizationFactor)

    # Normalize the values of the control group (untreated) and treated group:
    # Dictonary containers for storing the number of the df (key) and the df 
    # (value).
    splitted_untreated = {} 
    splitted_treated = {}
    # Make keys for quality control of each modified data based on the 
    # number of the df, used for debugging.
    i = 1 # i as the key for the untreated dataframes.
    j = 1 # j as the key for the treated dataframes.
    for plate_id, normalizaton_factor in zip(
            all_plates_identifiers, all_plates_NormalizerFactors):
        # Applying (Multiplying) normalized mean of each plate to every 
        # value of that plate
        splitted_df_untreated = df_untreated.loc[
            df_untreated[plate_identifier] == plate_id
        ]
        splitted_df_untreated = splitted_df_untreated.copy()
        # make a new empty column to add the normalized numbers to
        new_col = column_for_normalization + "_Normalized_" + "by_" + func
        splitted_df_untreated[new_col] = "" 
        # add the normalized values to the newly made column.
        splitted_df_untreated[new_col] = (
            splitted_df_untreated[column_for_normalization].apply(
                lambda x: x * normalizaton_factor
            )
        )
        
        # Append the modified dataframe to the container dictionary 
        # for later concat of all modified slices. 
        splitted_untreated[i] = splitted_df_untreated 
        i += 1
    #  Normalize the values of the sample group based on the control 
    # normalizers. 
        splitted_df_treated = df_treated.loc[
            df_treated[plate_identifier] == plate_id
        ]
        splitted_df_treated = splitted_df_treated.copy()
        # make a new empty column to add the normalized numbers to
        splitted_df_treated[new_col] = "" 
        # add the normalized values to the newly made column.
        splitted_df_treated[new_col] = (
            splitted_df_treated[column_for_normalization].apply(
                lambda x: x * normalizaton_factor
            )
        )
        
        # Append the modified dataframe to the container dictionary 
        # for later concat of all modified slices. 
        splitted_treated[j] = splitted_df_treated 
        j += 1

    # Combine all the sliced dfs from each unreated and treated samples. 
    final_untreated_df = pd.concat(
        splitted_untreated.values(), ignore_index=True
    )
    final_treated_df = pd.concat(
        splitted_treated.values(), ignore_index=True
    )

    # Use two variable to get the newly modifed untread and treated dfs. 
    return final_untreated_df, final_treated_df
