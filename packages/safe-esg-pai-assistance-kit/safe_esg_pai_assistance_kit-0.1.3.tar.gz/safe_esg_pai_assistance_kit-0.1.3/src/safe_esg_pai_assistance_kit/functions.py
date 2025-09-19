from sklearn.preprocessing import OneHotEncoder
import numpy as np
import pandas as pd

def _ohe(drop='first', handle_unknown='ignore'):
    """Return OneHotEncoder, compatible with sklearn <1.2 and >=1.2."""
    try:
        return OneHotEncoder(drop=drop, sparse_output=False, handle_unknown=handle_unknown)
    except TypeError:
        return OneHotEncoder(drop=drop, sparse=False, handle_unknown=handle_unknown)

#
#region
def interpolate_missing_values_regression_ols(
    df,
    target_variable,
    categorical_features,
    numeric_features,
    identifier='hl_isin',
    drop_invalids_below_zero=True,
    verbose=True,
    diagnostic= False  # If you'd like to harmonize
):
    #region
    """
    ---------------------------------------------------
    Regression-based interpolation using OneHotEncoder
    ---------------------------------------------------

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with missing values to be interpolated.
    
    target_variable : str
        Name of the column to be predicted (e.g., 'hl_SCOPE_1_GHG_EMISSIONS').
    
    categorical_features : list of str
        List of categorical feature names (to be one-hot encoded).
    
    numeric_features : list of str
        List of numeric feature names (used as-is).
    
    identifier : str, default='hl_isin'
        Column name used to merge predictions back into the original DataFrame.
    
    drop_invalids_below_zero : bool, default=True
        If True, set negative or zero predictions to NaN.
    
    verbose : bool, default=True
        If True, print summary message when interpolation is done.
    
    Returns
    -------
    pd.DataFrame
        Updated DataFrame with interpolated target values and a new flag column:
        '<target_variable>_INTERPOLATED'
    """
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.linear_model import LinearRegression
    import warnings

    # 1. Define predictors and subset rows with full data
    all_features = categorical_features + numeric_features
    train_df = df[df[[target_variable] + all_features].notna().all(axis=1)].copy()

    if train_df.empty:
        if verbose:
            print(f"[{target_variable}] No complete cases found for training. No interpolation performed.")
        return df

    X_train = train_df[all_features]
    y_train = train_df[target_variable].astype(float)

    # 2. Subset test data (target missing but predictors available)
    test_df = df[df[target_variable].isna() & df[all_features].notna().all(axis=1)].copy()
    if test_df.empty:
        if verbose:
            print(f"[{target_variable}] No missing values found to interpolate.")
        return df

    X_test = test_df[all_features]

    # 3. Prepare OneHotEncoder + ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', _ohe(drop='first', handle_unknown='ignore'), categorical_features),
            ('num', 'passthrough', numeric_features)
        ]
    )

    # 4. Pipeline: Encoding + Regression
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', LinearRegression())
    ])

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, message="Found unknown categories.*")
        pipeline.fit(X_train, y_train)

        # 5. Predict missing values
        y_pred = pipeline.predict(X_test)
        
    test_df[f'{target_variable}_pred'] = y_pred
    test_df[f'{target_variable}_INTERPOLATED'] = True

    # 6. Optional: Drop invalid predictions ! Important - this is different for the Probits !
    if drop_invalids_below_zero:
        test_df.loc[test_df[f'{target_variable}_pred'] <= 0, f'{target_variable}_pred'] = np.nan
        test_df.loc[test_df[f'{target_variable}_pred'].isna(), f'{target_variable}_INTERPOLATED'] = np.nan

    # 7. Merge predictions back
    merged = df.merge(
        test_df[[identifier, f'{target_variable}_pred', f'{target_variable}_INTERPOLATED']],
        how='left',
        on=identifier,
        suffixes=('', '_new')
    )

    # 8. Combine original and predicted values
    merged[target_variable] = merged[target_variable].combine_first(merged[f'{target_variable}_pred'])
    merged[f'{target_variable}_INTERPOLATED'] = merged[f'{target_variable}_INTERPOLATED'].combine_first(
        merged[f'{target_variable}_INTERPOLATED_new']
    )

    # 9. Cleanup
    merged.drop(columns=[
        f'{target_variable}_pred',
        f'{target_variable}_INTERPOLATED_new'
    ], inplace=True)

    if verbose:
        interpolated = merged[f'{target_variable}_INTERPOLATED'].sum(skipna=True)
        print(f"REGRESSION DONE ({target_variable}): {int(interpolated)} values interpolated")

    return merged

#endregion
#endregion

#region
def interpolate_missing_values_regression_probit(
    # 0.1) General Input variables
    dataframe,
    target_variable,
    categorical_features,
    numeric_features,

    # 0.2) Robustness options against multicollinearity issues (mirrors informative probit)
    robust=True,
    robustness_threshold=1,
    col_mode="vif",                 # 'vif', 'corr', or ['vif','corr']
    vif_threshold="auto",           # 'auto' or numeric (e.g. 10)
    corr_threshold=0.95,
    protect_features=None,          # e.g. ['const','hl_InvtrRevenue']

    # 0.3) Merge/validation options specific to factual interpolation
    identifier="hl_isin",
    drop_invalids_outside_unit_interval=True,

    # 0.4) Documentation configuration (optional parity with informative; no prints)
    output_path_html=None,
    pai_name="PAI_PROBIT_FACTUAL",
    fractional = False
):
    #region 
    """

    """
    import warnings
    from typing import List, Optional, Dict, Union

    import numpy as np
    import pandas as pd
    import statsmodels.api as sm
    from statsmodels.discrete.discrete_model import Probit
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder
    from itertools import combinations
    from statsmodels.tools.sm_exceptions import ConvergenceWarning, PerfectSeparationWarning
  

    # 1) Filter Complete Cases
    feature_columns = (categorical_features or []) + (numeric_features or [])
    sub_df = dataframe[dataframe[[target_variable] + feature_columns].notna().all(axis=1)].copy()
    if sub_df.empty:
        # no training possible → return original df unchanged
        return dataframe

    # 1.1) Dependent/Independent variables
    X_raw = sub_df[feature_columns]
    y = sub_df[target_variable].astype(float)

    # 2) Transform categorical variables (OHE) + passthrough numeric
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", _ohe(drop='first', handle_unknown='ignore'), categorical_features),
            ("num", "passthrough", numeric_features),
        ]
    )

    # 3) Transform & build design matrix with constant
    X_array = preprocessor.fit_transform(X_raw)
    cat_feature_names = (
        preprocessor.named_transformers_["cat"].get_feature_names_out(categorical_features).tolist()
        if categorical_features else []
    )
    feature_names = cat_feature_names + (numeric_features or [])
    X = pd.DataFrame(X_array, columns=feature_names, index=y.index)
    X = sm.add_constant(X).astype(float)

    # 4) Robustness bookkeeping
    dropped_constant_vars_inform  = []
    dropped_corr_vars_inform = []
    dropped_vif_vars_inform  = []
    protected_vars = ["const"]
    if protect_features:
        protected_vars.extend(list(protect_features))
    protected_vars = list(dict.fromkeys(protected_vars))

    # 5) Near-constant dummy filtering (only 0/1 columns)
    if robust:
        low_info_cols = []
        for col in X.columns:
            if col in protected_vars:
                continue
            uniq = set(X[col].dropna().unique())
            if uniq.issubset({0.0, 1.0}):
                ones = int((X[col] == 1).sum())
                zeros = int((X[col] == 0).sum())
                if min(ones, zeros) < robustness_threshold:
                    low_info_cols.append(col)
        if low_info_cols:
            X.drop(columns=low_info_cols, inplace=True)
            dropped_constant_vars_inform = low_info_cols.copy()
   

    # 6) Multicollinearity reduction
    modes = [col_mode] if isinstance(col_mode, str) else list(col_mode or [])
    valid_modes = {"vif", "corr"}
    modes = [m for m in modes if m in valid_modes]

    # 6a) Correlation-based approach
    if "corr" in modes:
        dummy_cols = []
        for c in X.columns:
            if c == "const":
                continue
            vals = set(X[c].dropna().unique())
            if vals.issubset({0.0, 1.0}):
                dummy_cols.append(c)

        if len(dummy_cols) > 1:
            corr_frame = X[dummy_cols]
            corr_mat = corr_frame.corr().abs()
            to_drop = []
            for col_i, col_j in combinations(dummy_cols, 2):
                if corr_mat.loc[col_i, col_j] > corr_threshold:
                    i_prot = (col_i in protected_vars)
                    j_prot = (col_j in protected_vars)
                    if i_prot and j_prot:
                        continue
                    elif i_prot and not j_prot:
                        drop_candidate = col_j
                    elif j_prot and not i_prot:
                        drop_candidate = col_i
                    else:
                        ones_i = int((corr_frame[col_i] == 1).sum())
                        ones_j = int((corr_frame[col_j] == 1).sum())
                        drop_candidate = col_i if ones_i < ones_j else col_j
                    if (drop_candidate not in to_drop) and (drop_candidate not in protected_vars):
                        to_drop.append(drop_candidate)
                        dropped_corr_vars_inform.append({
                            "variable": drop_candidate,
                            "reason": f"high correlation (> {corr_threshold})"
                        })
            if to_drop:
                X.drop(columns=list(to_drop), inplace=True)

  
    # 6b) VIF-based approach
    if "vif" in modes:
        # Always protect the intercept
        if "const" not in protected_vars:
            protected_vars.append("const")

        if isinstance(vif_threshold, str) and vif_threshold == "auto":
            # Try a descending ladder of thresholds until a stable model can be fit
            ladder = [float("inf"), 100, 75, 50, 40, 30, 20, 15, 12, 10, 8, 6, 5]
            fit_success = False

            for threshold in ladder:
                X_temp = X.copy()

                while True:
                    # Compute VIFs for all columns of X_temp
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", message="divide by zero encountered in scalar divide")
                        vif_values = [variance_inflation_factor(X_temp.values, i) for i in range(X_temp.shape[1])]

                    # Pack into a small DataFrame for easy filtering/sorting
                    vif_df = pd.DataFrame({"variable": X_temp.columns, "VIF": vif_values})

                    # Select all non-protected variables with VIF >= current threshold
                    high_vif = vif_df[
                        (vif_df["VIF"] >= threshold) & (~vif_df["variable"].isin(protected_vars))
                    ].sort_values("VIF", ascending=False)

                    # If nothing to drop at this threshold, try to fit a quick model to validate stability
                    if high_vif.empty:
                        try:
                            with warnings.catch_warnings():
                                warnings.filterwarnings("ignore", message="Maximum Likelihood optimization failed to converge")
                            if fractional:
                                # Fractional response (0–1): GLM Binomial with logit link
                                _test = sm.GLM(
                                    y, X_temp, family=sm.families.Binomial(link=sm.families.links.Logit())
                                ).fit()
                            else:
                                # Binary response: Probit
                                _test = Probit(y, X_temp).fit(disp=0)

                            # Basic sanity checks (robust to GLM vs Probit)
                            if np.all(np.isnan(_test.params.values)):
                                raise ValueError("All coefficients are NaN")
                            if hasattr(_test, "prsquared") and not np.isfinite(_test.prsquared):
                                raise ValueError("Pseudo R² invalid")
                            if not np.isfinite(getattr(_test, "llf", np.nan)):
                                raise ValueError("Log-likelihood invalid")
                            if getattr(_test, "nobs", X_temp.shape[0]) != X_temp.shape[0]:
                                raise ValueError("Observation mismatch")

                            # Accept this reduced design matrix
                            X = X_temp
                            fit_success = True
                        except Exception:
                            fit_success = False
                        break  # leave the inner while-loop

                    # Otherwise: drop the single worst offender (highest VIF)
                    to_drop = high_vif.iloc[0]["variable"]
                    if to_drop in protected_vars:
                        # Defensive: never drop protected variables
                        break
                    X_temp = X_temp.drop(columns=[to_drop])
                    dropped_vif_vars_inform.append({"variable": to_drop, "reason": f"high VIF (>= {threshold})"})

                if fit_success:
                    # Stop trying lower thresholds once a stable fit is confirmed
                    break

        else:
            # User provided a numeric threshold
            threshold = float(vif_threshold)

            while True:
                # Compute VIFs for all columns of X
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", message="divide by zero encountered in scalar divide")
                    vif_values = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]

                vif_df = pd.DataFrame({"variable": X.columns, "VIF": vif_values})

                # Find non-protected variables at/above the threshold
                high_vif = vif_df[
                    (vif_df["VIF"] >= threshold) & (~vif_df["variable"].isin(protected_vars))
                ].sort_values("VIF", ascending=False)

                if high_vif.empty:
                    # Nothing else to drop — we're done
                    break

                # Drop the worst offender
                to_drop = high_vif.iloc[0]["variable"]
                if to_drop in protected_vars:
                    # Defensive: never drop protected variables
                    break
                X = X.drop(columns=[to_drop])
                dropped_vif_vars_inform.append({"variable": to_drop, "reason": f"high VIF (>= {threshold})"})

    # 7) Final NA guard (rows)
    X_clean = X.copy()
    y_clean = y.copy()
    mask = ~(X_clean.isna().any(axis=1) | y_clean.isna())
    X_clean = X_clean[mask]
    y_clean = y_clean[mask]

    # 8) Fit Probit (silent)
    warnings.filterwarnings("ignore", message="Maximum Likelihood optimization failed to converge")

    if fractional:
        # Fractional response in [0,1] -> GLM Binomial with logit link (Papke & Wooldridge)
        # Note: This accepts 0 and 1 without clipping.
        model = sm.GLM(
            y_clean, X_clean, family=sm.families.Binomial(link=sm.families.links.Logit())
        ).fit()
    else:
        # Binary response -> Probit
        model = Probit(y_clean, X_clean).fit(maxiter=1500, disp=0)
        
    # 9) Build X_test with same preprocessing/columns as X
    # 9.1) Identify rows to predict (missing target but predictors available)
    pred_mask = dataframe[target_variable].isna() & dataframe[feature_columns].notna().all(axis=1)
    if not pred_mask.any():
        return dataframe
    test_df = dataframe[pred_mask].copy()

    X_test_array = preprocessor.transform(test_df[feature_columns])
    X_test = pd.DataFrame(X_test_array, columns=feature_names, index=test_df.index)
    X_test = sm.add_constant(X_test).astype(float)
    X_test = X_test.reindex(columns=X_clean.columns, fill_value=0.0)

    # 10) Predict probabilities
    y_pred = model.predict(X_test)

    # 11) Merge predictions back
    pred_col = f"{target_variable}_pred"
    flag_col = f"{target_variable}_INTERPOLATED"
    test_df[pred_col] = y_pred
    test_df[flag_col] = True

    if drop_invalids_outside_unit_interval:
        invalid = (test_df[pred_col] < 0) | (test_df[pred_col] > 1) | (~np.isfinite(test_df[pred_col]))
        test_df.loc[invalid, pred_col] = np.nan
        test_df.loc[invalid, flag_col] = np.nan

    merged = dataframe.merge(
        test_df[[identifier, pred_col, flag_col]],
        how="left",
        on=identifier,
        suffixes=("", "_new")
    )
    merged[target_variable] = merged[target_variable].combine_first(merged[pred_col])
    merged[flag_col] = merged[flag_col].combine_first(merged[f"{flag_col}_new"])
    merged.drop(columns=[c for c in [pred_col, f"{flag_col}_new"] if c in merged.columns], inplace=True)

    # 12) Optional HTML artifacts (silent)
    if output_path_html is not None:
        try:
            with open(f"{output_path_html}_{pai_name}_probit_regression_summary.html", "w") as f:
                f.write(model.summary().as_html())

            if dropped_constant_vars_inform:
                pd.DataFrame({
                    "variable": dropped_constant_vars_inform,
                    "reason": [f"constant/near-constant (threshold={robustness_threshold})"] * len(dropped_constant_vars_inform)
                }).to_html(f"{output_path_html}_{pai_name}_probit_regression_dropped_constant.html", index=False)

            if dropped_corr_vars_inform:
                pd.DataFrame(dropped_corr_vars_inform).to_html(
                    f"{output_path_html}_{pai_name}_probit_regression_dropped_corr.html", index=False
                )

            if dropped_vif_vars_inform:
                pd.DataFrame(dropped_vif_vars_inform).to_html(
                    f"{output_path_html}_{pai_name}_probit_regression_dropped_vif.html", index=False
                )
        except Exception:
            # fail-silent for artifact writing
            pass

    return merged
    #endregion
    #endregion

#
#region
def run_informative_regression_ols(
    dataframe,
    target_variable,
    categorical_features,
    numeric_features,
    output_path_html=None,
    print_summary=True
):
    """
    ------------------
    Diagnostic OLS Regression (with OneHotEncoder)
    ------------------

    Parameters
    ----------
    dataframe : pd.DataFrame
        Input DataFrame with all required variables.

    target_variable : str
        Name of the target column (dependent variable).

    categorical_features : list of str
        Names of categorical features to be one-hot encoded.

    numeric_features : list of str
        Names of numeric features to be passed through.

    output_path_html : str or None, optional
        Path to save the HTML summary of the regression. If None, no file is saved.

    print_summary : bool, optional
        If True, print the regression summary to console.
    """
    import statsmodels.api as sm
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.compose import ColumnTransformer
    #  1. Filter complete cases
    feature_columns = categorical_features + numeric_features
    sub_df = dataframe[
        dataframe[[target_variable] + feature_columns].notna().all(axis=1)
    ].copy()

    X_raw = sub_df[feature_columns]
    y = sub_df[target_variable].astype(float)

    #  2. Set up ColumnTransformer with OneHotEncoder
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(drop='first', sparse_output =False, handle_unknown='ignore'), categorical_features),
            ('num', 'passthrough', numeric_features)
        ]
    )

    #  3. Transform features and extract names
    X_array = preprocessor.fit_transform(X_raw)
    feature_names = (
        preprocessor.named_transformers_['cat']
        .get_feature_names_out(categorical_features)
        .tolist() + numeric_features
    )

    #  4. Create DataFrame with constant and correct column names
    X = pd.DataFrame(X_array, columns=feature_names, index=y.index)
    X = sm.add_constant(X).astype(float)
    
    # #  4b. Drop multicollinear columns automatically (like Stata's force)
    # # Multicollinearity remedy - if needed
    # X_reduced, col_index = sm_tools.fullrank(X, rcond=1e-10)
    # X = pd.DataFrame(X_reduced, index=y.index, columns=X.columns[col_index])
    # dropped_cols = set(X.columns) - set(X.columns[col_index])
    # if dropped_cols:
    #   print(f"[INFO] Dropped collinear columns: {sorted(dropped_cols)}")
    

    #  5. Run OLS regression
    model = sm.OLS(y, X).fit()

    #  6. Print summary
    if print_summary:
        print(model.summary())

    #  7. Save to HTML
    if output_path_html is not None:
        with open(output_path_html, "w") as f:
            f.write(model.summary().as_html())

    return model
#endregion

#
#region
def run_informative_regression_probit(
    # 0.1) General Input variables
    dataframe,  
    target_variable, 
    categorical_features, 
    numeric_features,
   
    # 0.2)  Robustness options against multicolinearity issues
    robust, 
    robustness_threshold, 
    col_mode, 
    # 0.2.1) Tresholds for VIF or CORR based robustness option
    vif_threshold,
    corr_threshold,
    # 0.3) Protected Feature Definition
    # Define Features that shall never be dropped in robustness operations (e.g., ['const', 'hl_InvtrRevenue']) - ("hl_headquarters_country_", "hl_nace_code_collapsed_"),
    protect_features,  
    # 0.4) Documentation Configuration    
    output_path_html, 
    print_summary,  
    pai_name,
    fractional = False): 

    
    #region
    import warnings
    from typing import List, Optional, Dict, Union  # <-- Tuple entfernt

    import numpy as np
    import pandas as pd
    import statsmodels.api as sm
    from statsmodels.discrete.discrete_model import Probit
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder
    from itertools import combinations 
    from statsmodels.tools.sm_exceptions import ConvergenceWarning, PerfectSeparationWarning

       
    #######
    # 0.) General Information
    ######
    
    
    # dataframe: expects an input dataframe containing your dependent and explanatory variables 
    # target_variable: expects a target variable as a string,
    # categorical_features: expects your categorical features that you want to use 
    # numeric_features: expects your numerical features that you want to use
    # output_path_html: insert where you want to see your autput path Optional[str] = None 
    # print_summary: a True or false switch if you want to see whats happening bool = True 
    

    #  1) Filter Complete Cases
    # We filter for complete cases and create a sub data frame sub_df
    feature_columns = categorical_features + numeric_features
    sub_df = dataframe[dataframe[[target_variable] + feature_columns].notna().all(axis=1)].copy()

    # If our sub_df is empty, we raise an error 
    if sub_df.empty:
        raise ValueError("No complete cases found for informative Probit regression.")

    # 1.1) Definition of Dependent and Independent Variables
    
    # 1.1.1) Independent Variable Raw
    X_raw = sub_df[feature_columns]
    # 1.1.2) Dependent Variable Raw
    y = sub_df[target_variable].astype(float)

    #  2.) Transform our categorical variables 
    # We use now here column transformer in order to transform our categorical variables, our numeric variables are passed through and remain unchanged.
    # The result is a combined feature matrix where categorical variables are represented as dummies and numeric variables remain intact.
    preprocessor = ColumnTransformer(
        transformers=[("cat", _ohe(drop='first', handle_unknown='ignore'), categorical_features,),
                      ("num", "passthrough", numeric_features),])

    #  3) Transform and build design matrix with constant
    # 3.1) Now we run the previously defined preprocessor. The result is an array with all transformed values.
    X_array = preprocessor.fit_transform(X_raw)
    # 3.2) Collect the Feature Names for the dummy columns. If there are no categorical features, just return an empty list []
    cat_feature_names = (preprocessor.named_transformers_["cat"].get_feature_names_out(categorical_features).tolist()
        if len(categorical_features) > 0
        else []
    )
    # Combine all feature names and create a dataframe with those names
    feature_names = cat_feature_names + numeric_features
    # columns = feature_names (so the dummy columns get readable names)
    # index = y.index (so rows line up with the target variable)
    X = pd.DataFrame(X_array, columns=feature_names, index=y.index)
    # Add a constant column ("const") to the design matrix (required)
    X = sm.add_constant(X).astype(float)

    #  4) Robustness bookkeeping - leep track of variables that get dropped during robustness checks
    dropped_constant_vars_inform  = []
    dropped_corr_vars_inform = []
    dropped_vif_vars_inform  = []
    # Add protected variables if chosen
    protected_vars = ["const"]
    if protect_features:
        protected_vars.extend(list(protect_features))


    #  5) Near-constant dummy filtering (only affects 0/1 columns)
    # Robustness Treshhold Module
    if robust:
        # Prepare list to collect columns that should be dropped
        low_info_cols = []
        
        # Loop over all columns in the design matrix
        for col in X.columns:
            if col in protected_vars:
              continue

            # Check if the column looks like a dummy variable (only 0/1 values)
            if set(X[col].dropna().unique()).issubset({0, 1}):
                # Count the number of zero and one entries
                count_ones = int((X[col] == 1).sum())
                count_zeros = int((X[col] == 0).sum())

                # If one of the classes is too rare (< robustness_threshold), mark column as low-info
                if min(count_ones, count_zeros) < robustness_threshold:
                    low_info_cols.append(col)            
        if low_info_cols:
            X.drop(columns=low_info_cols, inplace=True)
            dropped_constant_vars_inform = low_info_cols.copy()

    
    #  6) Multicollinearity reduction
    # Make sure col_mode is a list
    modes = [col_mode] if isinstance(col_mode, str) else list(col_mode)
    valid_modes = {"vif", "corr"}
    # Sanity check: warn if the user passed something invalid
    for m in modes:
        if m not in valid_modes:
            print(f"[WARNING] You selected an invalid mode: '{m}'. Only 'vif' or 'corr' are allowed.")


    # 6a) Correlation-based approach
    if "corr" in modes:
      # Collect all dummy columns (binary 0/1), except the constant
        dummy_cols = []
        for c in X.columns:
          if c == "const":
            continue
          # Keep only columns that look like dummy variables (only 0/1 values)
          if set(X[c].dropna().unique()).issubset({0, 1}):
            dummy_cols.append(c)
        
        # Check if we have at least 2 dummy columns
        if len(dummy_cols) > 1:
            
            # Create a smaller DataFrame with only these dummy columns
            corr_frame = X[dummy_cols]
            # Calculate the absolute correlation matrix and take absolute values
            corr_mat = corr_frame.corr().abs()
            
            # Create an empty Set to remember which columns we decided to drop
            to_drop = []
            
            ## Actual Comparison of all pairs - compare every pair of dummy columns
            for col_i, col_j in combinations(dummy_cols, 2):
                # If they are highly correlated, decide which one to drop
                if corr_mat.loc[col_i, col_j] > corr_threshold:

                    # Protection rules: never drop protected variables
                    i_prot = (col_i in protected_vars)
                    j_prot = (col_j in protected_vars)

                    # Case 1: both protected -> keep both
                    if i_prot and j_prot:
                        continue

                    # Case 2: one protected -> drop the other one
                    elif i_prot and not j_prot:
                        drop_candidate = col_j
                    elif j_prot and not i_prot:
                        drop_candidate = col_i

                    # Case 3: none protected -> drop the rarer dummy
                    else:
                        ones_i = int((corr_frame[col_i] == 1).sum())
                        ones_j = int((corr_frame[col_j] == 1).sum())
                        drop_candidate = col_i if ones_i < ones_j else col_j

                    # Add to list if not already scheduled for dropping
                    if drop_candidate not in to_drop:
                        to_drop.append(drop_candidate)
                        dropped_corr_vars_inform.append({
                            "variable": drop_candidate,
                            "reason": f"high correlation (> {corr_threshold})"
                            })
            if to_drop:
                X.drop(columns=list(to_drop), inplace=True)

    
    # 6b) VIF-based approach
    # vif_threshold == "auto": try a sequence of thresholds (∞, 100, 90, ..., 1)
    # and validate that a Probit can be fit after dropping high-VIF variables.
    # 2) vif_threshold is a number: drop variables with VIF >= threshold until stable.

    if "vif" in modes:

      # Always protect the intercept/constant column from being dropped
      if "const" not in protected_vars:
          protected_vars.append("const")

      ##### AUTO MODE #####
      if isinstance(vif_threshold, str) and vif_threshold == "auto":
        
          # Define list of treshold for the loop down below
          fallback_thresholds = [float("inf"),100, 75, 50, 20, 10, 5, 2, 1]
          # Set fit_success = False
          fit_success = False

          # Work on a copy so we can try different thresholds without losing original X
          X_temp = X.copy()


          for trial_vif in fallback_thresholds:
              with warnings.catch_warnings():
                  warnings.filterwarnings("ignore", message="divide by zero encountered in scalar divide")

                  # Iteratively drop the worst (highest VIF) variable until all VIFs are below the current threshold
                  # until break!
                  while True:
                      # For each column, calculate the VIF value with variance_inflation_factor(...) Store the result in the list vif_values
                      vif_values = []
                      for i in range(X_temp.shape[1]):
                          value = variance_inflation_factor(X_temp.values, i)
                          vif_values.append(value)
                                         
                      # Create a DataFrame with two columns:
                      vif_df = pd.DataFrame({"variable": X_temp.columns, "VIF": vif_values})

                      # Select only the variables that are NOT protected and have VIF >= current threshold
                      # Sort them so the variable with the highest VIF is at the top
                      high_vif = vif_df[(vif_df["VIF"] >= trial_vif) & 
                                        (~vif_df["variable"].isin(protected_vars))].sort_values("VIF", ascending=False)

                      # If no variables are above the threshold:  Try to fit a Probit model to check that the reduced dataset still works
                      if high_vif.empty:
                          try:
                              warnings.simplefilter("ignore", ConvergenceWarning)
                              warnings.simplefilter("ignore", PerfectSeparationWarning)
                              if fractional:
                                test_model = sm.GLM(
                                    y, X_temp, family=sm.families.Binomial(link=sm.families.links.Logit())
                                ).fit()
                              else:                         
                                test_model = Probit(y, X_temp).fit(disp=0)

                              # Basic sanity checks on the fitted model
                              if np.all(np.isnan(test_model.params.values)):
                                  raise ValueError("All coefficients are NaN")
                              if hasattr(test_model, "prsquared") and not np.isfinite(test_model.prsquared):
                                  raise ValueError("Pseudo R² invalid")
                              if not np.isfinite(getattr(test_model, "llf", np.nan)):
                                  raise ValueError("Log-likelihood invalid")
                              if getattr(test_model, "nobs", X_temp.shape[0]) != X_temp.shape[0]:
                                  raise ValueError("Observation mismatch")
                                                            
                              

                              # If everything looks good: accept this X_temp and mark as success
                              X = X_temp
                              fit_success = True
                          except Exception:
                              fit_success = False
                          break  # Exit the while-loop

                      # Otherwise: drop the variable with the highest VIF (worst offender)
                      to_drop = high_vif.iloc[0]["variable"]
                      # Never drop the constant column or any variable that is in the protected list
                      if to_drop in protected_vars:
                          break  

                      # Remove the selected column from X_temp
                      X_temp = X_temp.drop(columns=[to_drop])

                      # Keep track of what was dropped and why
                      dropped_vif_vars_inform.append(
                          {"variable": to_drop, "reason": f"high VIF (>= {trial_vif})"}
                      )
                    
                    # If we successfully validated a fit, stop trying lower thresholds
              if fit_success:
                  break
              
      ##### SELF SELECTED THRESHOLD MODE #####
      else:
          # Convert the user-provided threshold (vif_threshold) into a float number
          manual_vif_treshhold = float(vif_threshold)

          # Ignore harmless runtime warnings
          with warnings.catch_warnings():
              warnings.filterwarnings("ignore", message="divide by zero encountered in scalar divide")

              # Keep looping until all VIF values are below the chosen threshold
              while True:
                  # 1) Calculate VIF values for every column in X
                  vif_values = []
                  for i in range(X.shape[1]):
                      value = variance_inflation_factor(X.values, i)
                      vif_values.append(value)

                  # 2) Put the results into a DataFrame (variable name + its VIF value)
                  vif_df = pd.DataFrame({"variable": X.columns, "VIF": vif_values})

                  # 3) Select variables with VIF >= threshold and not in the protected list
                  #    Sort them so that the one with the highest VIF comes first
                  high_vif = (
                      vif_df[(vif_df["VIF"] >= manual_vif_treshhold) & (~vif_df["variable"].isin(protected_vars))]
                      .sort_values("VIF", ascending=False)
                  )

                  # 4) If there are no more variables above the threshold -> stop the loop
                  if high_vif.empty:
                      break

                  # 5) Otherwise: drop the single worst offender (highest VIF)
                  to_drop = high_vif.iloc[0]["variable"]

                  # Never drop the constant column or other protected variables
                  if to_drop in protected_vars:
                      break

                  # Drop the variable from X
                  X = X.drop(columns=[to_drop])

                  # Record which variable was dropped and why
                  dropped_vif_vars_inform.append(
                      {"variable": to_drop, "reason": f"high VIF (>= {manual_vif_treshhold})"}
                  )
    
    #  7) Final NA guard (rows)
    # Keep only rows without missing values in both X and y
    X_clean = X.copy()
    y_clean = y.copy()
    mask = ~(X_clean.isna().any(axis=1) | y_clean.isna())
    X_clean = X_clean[mask]
    y_clean = y_clean[mask]

    #  8) Fit Probit
    warnings.filterwarnings("ignore", message="Maximum Likelihood optimization failed to converge")
    
    if fractional:
      model = sm.GLM(
          y_clean, X_clean, family=sm.families.Binomial(link=sm.families.links.Logit())
      ).fit()
    else:
      model = Probit(y_clean, X_clean).fit(maxiter=1500, disp=0)
  

    #  9) Output
    if print_summary:
        print(model.summary())
        
    if output_path_html is not None:
      
      with open(f"{output_path_html}_{pai_name}_probit_regression_summary.html", "w") as f:
        f.write(model.summary().as_html())
  
      if dropped_constant_vars_inform:
        pd.DataFrame({
            "variable": dropped_constant_vars_inform,
            "reason": [f"constant/near-constant (threshold={robustness_threshold})"]
                      * len(dropped_constant_vars_inform)
                      }).to_html(f"{output_path_html}_{pai_name}_probit_regression_dropped_constant.html", index=False)

      if dropped_corr_vars_inform:
          pd.DataFrame(dropped_corr_vars_inform).to_html(
              f"{output_path_html}_{pai_name}_probit_regression_dropped_corr.html", index=False
          )

      if dropped_vif_vars_inform:
          pd.DataFrame(dropped_vif_vars_inform).to_html(
              f"{output_path_html}_{pai_name}_probit_regression_dropped_vif.html", index=False
          )

 
#endregion
#endregion


#
#region
def apply_group_interpolation(
    df,             # pd.DataFrame: input table containing the target column and grouping columns
    group_keys,     # list[str]: columns to group by (e.g., ['hl_nace_code_collapsed'] or ['hl_headquarters_country'])
    target,         # str: name of the numeric target column to fill (e.g., 'hl_SCOPE_1_GHG_EMISSIONS')
    style,          # str: interpolation style: 'mean' | 'median' | 'min' | 'max' | 'percentile'
    percentile_q = 0.9,  # float in [0,1]: quantile used when style == 'percentile' (default: 0.90)
    row_mask = None       # (optional): boolean mask; only rows where mask == True are eligible for filling
):
    """
    ----------
    Information
    ----------
    Purpose:
      Fill missing values (NaNs) in `target` by computing a group-wise statistic (mean/median/min/max/percentile),
      and writing it only into the missing spots. Optionally restrict filling to rows selected by `row_mask`.

    Supported styles:
      'mean', 'median', 'min', 'max', 'percentile'

    Flagging:
      Updates `{target}_INTERPOLATED` to True for newly filled values; keeps False for already observed;
      sets pd.NA for still-missing values after the step.

    -------
    Parameters
    -------
    row_mask : pd.Series[bool] or None
        Optional row filter. If provided, only rows where (row_mask == True) are considered for filling.
        All other rows remain unchanged even if they have NaNs.

    Returns
    -------
    df : pd.DataFrame
        Updated DataFrame (target values and interpolation flags possibly modified).
    """
    import pandas as pd

    # 0.) Resolve mask (default: all rows eligible)
    if row_mask is None:
        row_mask = pd.Series(True, index=df.index)

    # 1.) Count current non-null values (for logging)
    prev_count = df[target].count()

    # 2.) Compute the per-row "fill value" for each group
    if style == 'median':
        fill_series = df.groupby(group_keys)[target].transform('median')
    elif style == 'mean':
        fill_series = df.groupby(group_keys)[target].transform('mean')
    elif style == 'max':
        fill_series = df.groupby(group_keys)[target].transform('max')
    elif style == 'min':
        fill_series = df.groupby(group_keys)[target].transform('min')
    elif style == 'percentile':
        try:
            fill_series = df.groupby(group_keys)[target].transform('quantile', q=percentile_q)
        except Exception:
            fill_series = df.groupby(group_keys)[target].transform(
                lambda s: s.quantile(percentile_q, interpolation='linear')
            )
    else:
        raise ValueError(
            f"Unsupported style: {style}. Use one of 'mean','median','min','max','percentile'."
        )

    # 3.) Fill only where:
    #    (a) target was NaN BEFORE,
    #    (b) row_mask is True,
    #    (c) a group statistic exists (fill_series notna)
    before_was_nan = df[target].isna()
    eligible = before_was_nan & row_mask & fill_series.notna()
    df.loc[eligible, target] = fill_series[eligible]

    # 4.) Update interpolation flag
    now_has_value = df[target].notna()
    interp_col = f"{target}_INTERPOLATED"
    if interp_col not in df.columns:
        df[interp_col] = pd.NA  # init if missing

    df.loc[eligible & now_has_value, interp_col] = True
    df.loc[before_was_nan & ~now_has_value, interp_col] = pd.NA

    return df
#endregion
