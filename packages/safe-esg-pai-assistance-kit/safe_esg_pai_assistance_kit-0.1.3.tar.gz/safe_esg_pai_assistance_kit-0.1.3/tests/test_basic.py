import pandas as pd
from safe_esg_pai_assistance_kit import run_informative_regression_ols

def test_import_and_run():
    df = pd.DataFrame({"y": [1.0, 2.0, 3.0], "x": [1, 2, 3]})
    model = run_informative_regression_ols(
        df, "y", categorical_features=[], numeric_features=["x"], print_summary=False
    )
    assert model is not None
