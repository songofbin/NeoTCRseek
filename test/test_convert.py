from pathlib import Path
import pandas as pd
import shutil

from neotcrseek.convert import run_convert


def test_run_convert():
    # 输入测试文件路径
    input_file = Path(__file__).parent / "data" / "example_vdjtools.tsv"

    out_dir = Path(__file__).parent / "result"

    # 若已存在旧结果，先清空（避免测试污染）
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    output_file = out_dir / "converted.tsv"

    # 调用 convert 功能
    run_convert(input_file=input_file, output_file=output_file)

    # 验证输出文件是否存在
    assert output_file.exists()

    # 读取输出文件
    df = pd.read_csv(output_file, sep="\t")

    # 验证列是否按 NeoTCRseek 标准
    expected_cols = [
        "cdr3aa", "count", "freq", "convergence",
        "countSum", "v", "d", "j", "vdj"
    ]
    assert list(df.columns) == expected_cols

