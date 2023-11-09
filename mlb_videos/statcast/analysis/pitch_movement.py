import pandas as pd

REQUIRED_COLUMNS = ["pfx_x", "pfx_z"]
RETURN_COLUMNS = [
    "horizontal_break",
    "vertical_break",
    "total_break",
    "total_break_abs",
]


def pitch_movement(df: pd.DataFrame) -> pd.DataFrame:
    df[RETURN_COLUMNS] = df.swifter.apply(
        lambda x: (0.00,) * len(RETURN_COLUMNS)
        if any(pd.isnull(x[col]) for col in REQUIRED_COLUMNS)
        else (
            (x.pfx_x * -12.00),
            (x.pfx_z * 12.00),
            ((x.pfx_x * -12.00) + (x.pfx_z * 12.00)),
            abs(((x.pfx_x * -12.00) + (x.pfx_z * 12.00))),
        ),
        axis=1,
        result_type="expand",
    )
