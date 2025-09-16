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
        - If True: Outputs only the HEI columns and total score.
    """

    # Load input data
    df = pd.read_csv(input_file)

    # ------------------------------
    # HEI Calculation Section
    # ------------------------------
    # NOTE: Replace placeholder formulas with your actual scoring rules.
    # For example, some components are density-based (per 1000 kcal).

    # Total Fruits (example formula)
    df["HEI_total_fruits"] = (df["F_TOTAL"] / df["kcal"]) * 1000  

    # Whole Fruits (placeholder)
    df["HEI_whole_fruits"] = (df["F_TOTAL"] / 2)

    # Total Vegetables (placeholder)
    df["HEI_total_veg"] = (df["V_TOTAL"] / df["kcal"]) * 1000

    # Greens & Beans (placeholder)
    df["HEI_green_and_beans"] = (df["V_DRKGR"] + df["V_LEGUMES"]) / df["kcal"] * 1000

    # Whole Grains (placeholder)
    df["HEI_whole_grains"] = (df["G_WHOLE"] / df["kcal"]) * 1000

    # Dairy (placeholder)
    df["HEI_total_dairy"] = (df["D_TOTAL"] / df["kcal"]) * 1000

    # Protein Foods (placeholder)
    df["HEI_total_protein"] = (df["PF_TOTAL"] / df["kcal"]) * 1000

    # Seafood & Plant Proteins (placeholder)
    df["HEI_sea_food"] = (df["PF_SEAFD_HI"] + df["PF_SEAFD_LOW"] + df["PF_SOY"] + df["PF_NUTSDS"]) / df["kcal"] * 1000

    # Fatty Acids (placeholder)
    # Ideally: ratio of (PUFAs + MUFAs) / Saturated fats
    if "SOLID_FATS" in df.columns:
        df["HEI_fatty_acids"] = 1 / (df["SOLID_FATS"] + 1)  # placeholder
    else:
        df["HEI_fatty_acids"] = 0

    # Refined Grains (placeholder)
    df["HEI_refined_grains"] = (df["G_REFINED"] / df["kcal"]) * 1000

    # Sodium (placeholder)
    sodium_col = next((c for c in ["Sodium", "SODIUM", "NA", "sodium"] if c in df.columns), None)
    if sodium_col:
        df["HEI_sodium"] = df[sodium_col] / 1000
    else:
        df["HEI_sodium"] = 0
        print("⚠️ Warning: Sodium column not found, setting HEI_sodium = 0")

    # Added Sugar (placeholder)
    if "ADD_SUGARS" in df.columns:
        df["HEI_added_sugar"] = df["ADD_SUGARS"] / df["kcal"] * 1000
    else:
        df["HEI_added_sugar"] = 0

    # Saturated Fat (placeholder)
    if "SOLID_FATS" in df.columns:
        df["HEI_saturated_fat"] = df["SOLID_FATS"] / df["kcal"] * 1000
    else:
        df["HEI_saturated_fat"] = 0

    # ------------------------------
    # Total Score
    # ------------------------------
    hei_columns = [col for col in df.columns if col.startswith("HEI_")]
    df["HEI_total"] = df[hei_columns].sum(axis=1)

    # ------------------------------
    # Output Handling
    # ------------------------------
    if only_hei_columns:
        df_out = df[hei_columns + ["HEI_total"]]
    else:
        df_out = df

    # Save output
    df_out.to_csv(output_file, index=False)
    print(f"✅ HEI results saved to {output_file}")
