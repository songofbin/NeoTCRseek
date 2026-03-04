from pathlib import Path
import pandas as pd
import shutil

from neotcrseek.detect import run_detect


def test_run_detect_smoke():
    # 测试数据路径
    case_file = Path(__file__).parent / "data" / "example_case.tsv"
    control_file = Path(__file__).parent / "data" / "example_control.tsv"

    # 固定输出目录
    out_dir = Path(__file__).parent / "result"

    # 调用 run_detect
    run_detect(
        case_file=case_file,
        control_file=control_file,
        fc_threshold=2.0,
        freq_c_cutoff=0.001,
        FDR_threshold=0.05,
        freq_b_threshold=-1,
        out_dir=out_dir,
    )

    # 输出文件路径
    expanded_file = out_dir / "expanded_TCRs.txt"
    stat_file = out_dir / "expanded_TCRs.stat.txt"

    assert expanded_file.exists(), "expanded_TCRs.txt not generated"
    assert stat_file.exists(), "expanded_TCRs.stat.txt not generated"

    # 读取结果
    df_expanded = pd.read_csv(expanded_file, sep="\t")
    df_stat = pd.read_csv(stat_file, sep="\t")

    required_expanded_cols = [
        "ID",
        "cdr3aa",
        "count_c",
        "freq_c",
        "convergence_c",
        "countSum_c",
        "count_b",
        "freq_b",
        "convergence_b",
        "countSum_b",
        "FC",
        "OR",
        "Pvalue",
        "FDR",
        "Expanded",
    ]

    for col in required_expanded_cols:
        assert col in df_expanded.columns, \
            f"{col} missing in expanded_TCRs.txt"

    required_stat_cols = [
        "filter_info",
        "num_case",
        "num_control",
        "num_expand",
        "freq_case",
        "freq_control",
    ]

    for col in required_stat_cols:
        assert col in df_stat.columns, \
            f"{col} missing in expanded_TCRs.stat.txt"

