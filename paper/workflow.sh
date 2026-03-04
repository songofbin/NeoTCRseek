#!/bin/bash
set -euo pipefail

bash 01convert.sh
bash 02detect_validated_tcr.sh
bash 03detect_expanded_tcr.sh
bash 04predict_cocluster_tcr.sh
bash 05merge_NeoTCRseek.sh
