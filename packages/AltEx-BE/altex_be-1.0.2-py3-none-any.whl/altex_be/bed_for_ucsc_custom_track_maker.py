import pandas as pd

def format_sgrna_for_ucsc_custom_track(
    sgrna_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Purpose : 最終出力のsgRNA情報をUCSCカスタムトラック用のBED形式に変換する
    Parameters:
        sgrna_df (pd.DataFrame): offtarget までの情報を含むsgRNA情報のDataFrame。
    Return : pd.DataFrame 12 bedに修正された DataFrame
    """
    # score 列に1000を超える値が入ることがあるため、1000でクリップする
    sgrna_df["pam+20bp_exact_match_count"] = sgrna_df["pam+20bp_exact_match_count"].apply(lambda x: 1000 if x > 1000 else x)

    bed_df = pd.DataFrame()
    bed_df["chrom"] = sgrna_df["chrom"]
    bed_df["chromStart"] = sgrna_df["sgrna_start_in_genome"]
    bed_df["chromEnd"] = sgrna_df["sgrna_end_in_genome"]
    bed_df["name"] = sgrna_df["geneName"] + "_" + sgrna_df["site_type"] + "_" + sgrna_df["base_editor_name"]  + "_" + sgrna_df["uuid"]
    bed_df["score"] = sgrna_df["pam+20bp_exact_match_count"]
    bed_df["strand"] = sgrna_df["strand"]
    bed_df["thickStart"] = bed_df["chromStart"] # 別に必要ないが、9bed にするために追加
    bed_df["thickEnd"] = bed_df["chromEnd"]

    # Add RGB color based on base editor type
    color_map = {"abe": "176,0,0", "cbe": "0,78,160"} # ABE: red, CBE: blue
    bed_df["itemRgb"] = sgrna_df["base_editor_type"].map(color_map)
    
    # Reorder columns for BED9 format
    bed_df = bed_df[["chrom", "chromStart", "chromEnd", "name", "score", "strand", "thickStart", "thickEnd", "itemRgb"]]
    return bed_df