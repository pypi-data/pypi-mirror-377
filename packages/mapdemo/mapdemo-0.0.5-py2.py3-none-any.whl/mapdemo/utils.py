"""This is the utils module that cintain utility functions from the mapdemo package
"""


def csv_to_df(csv_file):
    """Converts a csv file to a pandas DataFrame.

    Args:
        csv_file (str): The path of the csv file

    Returns:
        pandas.DataFrame: The pandas Dataframe
    """
    import pandas as pd
    return pd.read_csv(csv_file)