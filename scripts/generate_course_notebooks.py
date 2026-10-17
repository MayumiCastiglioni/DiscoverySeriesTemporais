"""Generate the five base notebooks and twenty one-model training notebooks."""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_NOTEBOOK_DIR = PROJECT_ROOT / "notebooks" / "bases"
MODEL_NOTEBOOK_DIR = PROJECT_ROOT / "notebooks" / "modelos"
MODELS = (
    ("sarimax", "SARIMAX"),
    ("holt_winters", "Holt-Winters"),
    ("random_forest", "Random Forest"),
    ("xgboost", "XGBoost"),
)


def _root_cell() -> str:
    return """from pathlib import Path
import sys

ROOT = Path.cwd().resolve()
if not (ROOT / \"configs\").exists():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / \"src\"))
"""


def _base_notebook(base_id: int) -> nbformat.NotebookNode:
    return new_notebook(
        cells=[
            new_markdown_cell(
                f"""# Base {base_id}: exploração, ACF, STL e tratamento

Este notebook transforma apenas a entrada estrutural da Base {base_id} em um CSV `cleaned`, sem alterar os arquivos congelados. A ACF e a STL usam o maior segmento regular e completo do alvo. Se nenhum segmento permitir a STL, uma cópia exclusivamente diagnóstica pode interpolar lacunas internas; o CSV `cleaned` continua sem essa interpolação."""
            ),
            new_code_cell(
                _root_cell()
                + f"""
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

from discovery_series_temporais.cleaning import build_cleaned_dataset, plot_cleaned_diagnostics

BASE_ID = {base_id}
cleaned, summary = build_cleaned_dataset(BASE_ID, ROOT / \"data\" / \"processed\")
display(pd.DataFrame([{{
    \"base\": summary.base_id,
    \"target_original\": summary.target_name,
    \"rows\": summary.rows,
    \"columns\": summary.columns,
    \"missing_target\": summary.missing_target,
    \"cleaned_output\": str(summary.output_path),
    \"actions\": \"; \".join(summary.actions),
}}]))
display(cleaned.head())
display(cleaned.isna().sum().rename(\"missing_values\").to_frame())
"""
            ),
            new_code_cell(
                """figure, axis = plt.subplots(figsize=(12, 4))
axis.plot(cleaned[\"timestamp\"], cleaned[\"target\"], linewidth=0.7)
axis.set(title=f\"Base {BASE_ID}: alvo após tratamento\", xlabel=\"Tempo\", ylabel=\"Alvo\")
figure.tight_layout()
plt.show()

diagnostic = plot_cleaned_diagnostics(
    cleaned,
    BASE_ID,
    ROOT / \"reports\" / \"generated\" / \"exploration\" / f\"base{BASE_ID}\",
)
display(pd.DataFrame([{
    \"segment_start\": diagnostic.data[\"timestamp\"].min(),
    \"segment_end\": diagnostic.data[\"timestamp\"].max(),
    \"segment_points\": len(diagnostic.data),
    \"stl_seasonal_period\": diagnostic.seasonal_period,
    \"acf_lags\": diagnostic.acf_lags,
    \"diagnostic_interpolated_values\": diagnostic.diagnostic_interpolated_values,
}]))
"""
            ),
        ],
        metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
    )


def _model_notebook(base_id: int, model_name: str, model_label: str) -> nbformat.NotebookNode:
    return new_notebook(
        cells=[
            new_markdown_cell(
                f"""# Base {base_id}: treinamento piloto — {model_label}

Este notebook executa somente o {model_label} na primeira origem da agenda canônica da Base {base_id}. A entrada é o CSV `cleaned` gerado pelo notebook da base. É um piloto de integração, não uma busca de hiperparâmetros nem resultado final de MAE."""
            ),
            new_code_cell(
                _root_cell()
                + f"""
import pandas as pd
from IPython.display import display

from discovery_series_temporais.model_pilots import run_model_pilot
from discovery_series_temporais.series import build_origin_schedule, load_cleaned_candidate_target

BASE_ID = {base_id}
MODEL_NAME = \"{model_name}\"
candidate = load_cleaned_candidate_target(BASE_ID, ROOT / \"data\" / \"processed\")
canonical_schedule = build_origin_schedule(candidate)
result = run_model_pilot(candidate, canonical_schedule, MODEL_NAME)

if not result[\"origin_id\"].eq(canonical_schedule.iloc[0][\"origin_id\"]).all():
    raise AssertionError(\"The model pilot did not use the canonical origin.\")

output_dir = ROOT / \"reports\" / \"generated\" / \"training_notebooks\"
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / f\"base{{BASE_ID}}_{{MODEL_NAME}}_pilot.csv\"
result.to_csv(output_path, index=False)
display(result)
print(f\"Saved pilot: {{output_path}}\")
"""
            ),
        ],
        metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
    )


def main() -> None:
    BASE_NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    for base_id in range(1, 6):
        notebook = _base_notebook(base_id)
        nbformat.write(notebook, BASE_NOTEBOOK_DIR / f"base{base_id:02d}_exploracao_stl_tratamento.ipynb")
    index = 1
    for base_id in range(1, 6):
        for model_name, model_label in MODELS:
            notebook = _model_notebook(base_id, model_name, model_label)
            destination = MODEL_NOTEBOOK_DIR / f"{index:02d}_base{base_id:02d}_{model_name}_treinamento.ipynb"
            nbformat.write(notebook, destination)
            index += 1
    print(f"Generated 5 base notebooks and {index - 1} model-training notebooks.")


if __name__ == "__main__":
    main()
