from altex_be.sgrna_designer import BaseEditor
import argparse
import pandas as pd
from pathlib import Path

def parse_base_editors(args: argparse.Namespace) -> dict[str, BaseEditor] | None:
    return {
            args.base_editor_name: BaseEditor(
                base_editor_name=args.base_editor_name,
                pam_sequence=args.base_editor_pam.upper(),
                editing_window_start_in_grna=int(args.base_editor_window_start),
                editing_window_end_in_grna=int(args.base_editor_window_end),
                base_editor_type=args.base_editor_type.lower(),
            )
        }

def parse_gene_file(gene_file: Path) -> set[str] | None:
    if not gene_file:
        return None
    if gene_file.suffix.lower() not in [".txt", ".tsv", ".csv"]:
        raise ValueError("Unsupported file extension for gene file. Use .txt, .tsv, or .csv")
    with open(gene_file, "r") as f:
        interest_genes = {line.strip() for line in f if line.strip()} #空の行は if line.strip がFalseになるので除外できる
    return interest_genes

def show_base_editors_info(base_editors: dict[str, BaseEditor]):
    if base_editors is None:
        raise ValueError("No base editors available to display.")

    for base_editor in base_editors.values():
        print(f"  - {base_editor.base_editor_name} (Type: {base_editor.base_editor_type}, PAM: {base_editor.pam_sequence}, "
            f"Window: {base_editor.editing_window_start_in_grna}-{base_editor.editing_window_end_in_grna})")
        

def get_base_editors_from_args(args: argparse.Namespace) -> dict[str, BaseEditor] | None:
    """
    base editorの情報を含むファイルのパスを示す引数を受け取り、BaseEditorのリストを返す。
    csvまたはtxt, tsv形式のファイルをサポートする
    """
    expected_columns = [
    "base_editor_name",
    "pam_sequence",
    "editing_window_start",
    "editing_window_end",
    "base_editor_type"
    ]
    if not args.be_files:
        return None
    else:
        ext = Path(args.be_files).suffix.lower()

    if ext not in [".csv", ".tsv", ".txt"]:
        raise ValueError("Unsupported file extension for base editor file. Use .csv, .tsv, or .txt")
    if ext in [".csv"]:
        be_df = pd.read_csv(args.be_files, header=0)
    elif ext in [".tsv", ".txt"]:
        be_df = pd.read_csv(args.be_files, sep=None, engine="python", header=0)

    # 列名が期待通りかチェック、違うならエラーを投げる
    if set(be_df.columns) != set(expected_columns):
        raise ValueError(
            f"Base editor file columns are invalid. "
            f"Expected columns: {expected_columns}, but got: {list(be_df.columns)}"
        )
    else:
        return {
            row["base_editor_name"]: BaseEditor(
                base_editor_name=row["base_editor_name"],
                pam_sequence=row["pam_sequence"],
                editing_window_start_in_grna=int(row["editing_window_start"]),
                editing_window_end_in_grna=int(row["editing_window_end"]),
                base_editor_type=row["base_editor_type"],
            )
            for _, row in be_df.iterrows()
        }

def check_input_output_directories(refflat_path: Path, fasta_path: Path, output_directory: Path):
    if not refflat_path.is_file():
        raise FileNotFoundError(f"The provided refFlat file '{refflat_path}' does not exist.")
    if not fasta_path.is_file():
        raise FileNotFoundError(f"The provided FASTA file '{fasta_path}' does not exist.")
    if not output_directory.is_dir():
        raise NotADirectoryError(f"The provided output directory '{output_directory}' does not exist.")

def load_supported_assemblies() -> list[str]:
    """
    パッケージ内のcrispr_direct_supported_assemblies.txtを読み込み、アセンブリ名リストを返す
    """
    # このファイルと同じディレクトリにあるtxtを参照
    txt_path = Path(__file__).parent / "crispr_direct_supported_assemblies.txt"
    with open(txt_path, encoding="utf-8") as f:
        supported_assemblies = {line.strip() for line in f if line.strip() and not line.startswith("#")}
    return supported_assemblies

def is_supported_assembly_name_in_crispr_direct(assembly_name:str) -> bool:
    """
    Purpose: ユーザーが入力したアセンブリ名がCRISPRdirectでサポートされているかを確認する。
    Parameter: 
            assembly_name (str): ユーザーが入力したアセンブリ名
            supported_assemblies (list[str]): CRISPRdirectでサポートされているアセンブリ名のリスト 長いので外部txtとして保存
    return : bool
    """
    supported_assemblies = load_supported_assemblies()
    if assembly_name not in supported_assemblies:
        return False
    return True

def split_df_by_column_chunks(df: pd.DataFrame, chunk_sizes=[12, 6, 6]) -> list[pd.DataFrame]:
    """
    DataFrameをchunk_sizesで指定したカラム数ごとに分割し、各DataFrameをリストで返す。
    """
    columns = df.columns.tolist()
    idx = 0
    df = df.head()
    dfs = []
    for size in chunk_sizes:
        cols = columns[idx:idx+size]
        if not cols:
            break
        dfs.append(df[cols].copy())
        idx += size
    # 残りのカラムも追加
    if idx < len(columns):
        cols = columns[idx:]
        dfs.append(df[cols].copy())
    return dfs