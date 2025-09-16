import pandas as pd

def process_csv(input_file, output_file, only_hei_columns=False):
    """
    Calculate HEI-2015 scores from a dietary intake CSV file.

    Parameters
    ----------
    input_file : str
        Path to the input CSV file.
    output_file : str
        Path where the output CSV will be saved.
    only_hei_columns : bool, optional (default=False)
        - If False: Adds HEI columns to the existing file.
        - If True: Outputs only the HEI columns (plus SEQN).
    """

    # ------------------------------
    # Step 1: Load input data
    # ------------------------------
    # The CSV must include dietary intake columns (e.g., kcal, F_TOTAL, etc.)
    # Optionally, it can also contain SEQN (respondent ID).
    df = pd.read_csv(input_file)

    # ------------------------------
    # Step 2: HEI Calculation Section
    # ------------------------------
    # NOTE: Current formulas are placeholders.
    # Replace with official HEI-2015 scoring rules for accuracy.

    # Total Fruits score (per 1000 kcal)
    df["HEI_total_fruits"] = (df["F_TOTAL"] / df["kcal"]) * 1000

    # Whole Fruits (simplified placeholder: half of F_TOTAL)
    df["HEI_whole_fruits"] = (df["F_TOTAL"] / 2)

    # Total Vegetables (per 1000 kcal)
    df["HEI_total_veg"] = (df["V_TOTAL"] / df["kcal"]) * 1000

    # Greens & Beans (sum of dark green veg + legumes per 1000 kcal)
    df["HEI_green_and_beans"] = (df["V_DRKGR"] + df["V_LEGUMES"]) / df["kcal"] * 1000

    # Whole Grains (per 1000 kcal)
    df["HEI_whole_grains"] = (df["G_WHOLE"] / df["kcal"]) * 1000

    # Dairy (per 1000 kcal)
    df["HEI_total_dairy"] = (df["D_TOTAL"] / df["kcal"]) * 1000

    # Protein Foods (per 1000 kcal)
    df["HEI_total_protein"] = (df["PF_TOTAL"] / df["kcal"]) * 1000

    # Seafood & Plant Proteins (seafood + soy + nuts & seeds per 1000 kcal)
    df["HEI_sea_food"] = (df["PF_SEAFD_HI"] + df["PF_SEAFD_LOW"] +
                          df["PF_SOY"] + df["PF_NUTSDS"]) / df["kcal"] * 1000

    # Fatty Acids ratio (simplified placeholder: inverse of saturated fats)
    if "SOLID_FATS" in df.columns:
        df["HEI_fatty_acids"] = 1 / (df["SOLID_FATS"] + 1)
    else:
        df["HEI_fatty_acids"] = 0

    # Refined Grains (per 1000 kcal)
    df["HEI_refined_grains"] = (df["G_REFINED"] / df["kcal"]) * 1000

    # Sodium score (supports multiple column names like Sodium, NA, etc.)
    sodium_col = next((c for c in ["Sodium", "SODIUM", "NA", "sodium"] if c in df.columns), None)
    if sodium_col:
        df["HEI_sodium"] = df[sodium_col] / 1000
    else:
        df["HEI_sodium"] = 0
        print("⚠️ Warning: Sodium column not found, setting HEI_sodium = 0")

    # Added Sugar (per 1000 kcal, placeholder formula)
    if "ADD_SUGARS" in df.columns:
        df["HEI_added_sugar"] = df["ADD_SUGARS"] / df["kcal"] * 1000
    else:
        df["HEI_added_sugar"] = 0

    # Saturated Fat (per 1000 kcal, placeholder)
    if "SOLID_FATS" in df.columns:
        df["HEI_saturated_fat"] = df["SOLID_FATS"] / df["kcal"] * 1000
    else:
        df["HEI_saturated_fat"] = 0

    # ------------------------------
    # Step 3: Calculate Total HEI Score
    # ------------------------------
    # Collect all HEI_* columns and compute total
    hei_columns = [col for col in df.columns if col.startswith("HEI_")]
    df["HEI_total"] = df[hei_columns].sum(axis=1)

    # ------------------------------
    # Step 4: Handle Output
    # ------------------------------
    if only_hei_columns:
        # If user only wants HEI results, keep SEQN (if present) + HEI columns
        if "SEQN" in df.columns:
            keep_cols = ["SEQN"] + hei_columns + ["HEI_total"]
        else:
            keep_cols = hei_columns + ["HEI_total"]
        df_out = df[keep_cols]
    else:
        # Otherwise, return original dataset with HEI columns appended
        df_out = df

    # ------------------------------
    # Step 5: Save Results
    # ------------------------------
    df_out.to_csv(output_file, index=False)
    print(f"✅ HEI results saved to {output_file}")
