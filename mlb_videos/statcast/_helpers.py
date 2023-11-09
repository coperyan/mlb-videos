import pandas as pd


from mlb_videos.statcast._constants import DATE_FORMATS


def parse_df(df: pd.DataFrame) -> pd.DataFrame:
    """Parse Statcast Dataframe

    Parameters
    ----------
        df : pd.DataFrame
            Dataframe -- result of statcast API request

    Returns
    -------
        pd.DataFrame
            Cleaned, parsed, normalized dataframe
    """
    str_cols = [dt[0] for dt in df.dtypes.items() if str(dt[1]) in ["object", "string"]]

    for strcol in str_cols:
        fvi = df[strcol].first_valid_index()
        if fvi is None:
            continue
        fv = df[strcol].loc[fvi]

        if str(fv).endswith("%") or strcol.endswith("%"):
            df[strcol] = (
                df[strcol].astype(str).str.replace("%", "").astype(float) / 100.0
            )
        else:
            for date_regex, date_format in DATE_FORMATS:
                if isinstance(fv, str) and date_regex.match(fv):
                    df[strcol] = df[strcol].apply(
                        pd.to_datetime, errors="ignore", format=date_format
                    )
                    df[strcol] = df[strcol].convert_dtypes(convert_string=False)
                    break

    df.rename(
        columns={col: col.replace(".", "_") for col in df.columns.values if "." in col},
        inplace=True,
    )
    return df
