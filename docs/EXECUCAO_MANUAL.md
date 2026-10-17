# Execução manual

## Local do repositório neste computador

`C:\Users\mayumishimizu-ieg\.codex\.chatgpt-projects\g-p-6ad36ceb09bc81918ea40186a7712f30\DiscoverySeriesTemporais`

Os CSVs recebidos estão em `data/raw` neste computador, mas não são enviados ao Git por ainda dependerem de permissões de redistribuição. Em outro computador, coloque cópias idênticas dos cinco arquivos nesse diretório antes de executar a preparação.

## Preparar o ambiente

No PowerShell, abra a pasta do repositório e instale as dependências uma única vez:

```powershell
cd "C:\Users\mayumishimizu-ieg\.codex\.chatgpt-projects\g-p-6ad36ceb09bc81918ea40186a7712f30\DiscoverySeriesTemporais"
python -m pip install -r requirements.txt
```

## Executar por script

Esta é a sequência reproduzível. Ela não altera os arquivos em `data/raw`.

```powershell
python scripts/prepare_structural_data.py
python scripts/profile_candidate_series.py
python scripts/build_target_only_origins.py
python scripts/run_model_pilots.py
python scripts/run_checks.py
python scripts/execute_notebooks.py
```

Os arquivos gerados ficam em `reports/generated` e podem ser reconstruídos a qualquer momento.

## Executar pelos notebooks

Abra a interface de notebooks com:

```powershell
jupyter lab
```

Execute os notebooks na ordem numérica, usando **Run All Cells** em cada um:

1. `01_auditoria_e_stl_preliminar.ipynb`
2. `02_origens_e_xgboost_piloto.ipynb`
3. `03_regras_e_preparacao_por_grupo.ipynb`
4. `04_pilotos_dos_quatro_modelos.ipynb`
5. `05_avaliacao_walk_forward_final.ipynb`

O notebook 05 contém `HORIZON_STEPS_BY_BASE`. Cada número é contado na granularidade da própria base: uma etapa representa um dia na Base 1, uma hora nas Bases 2–4 e uma semana encerrada na sexta-feira na Base 5. A célula mostra como a escolha muda as origens e os alvos, mas `HORIZON_APPROVED` começa como `False`; portanto, não use esse notebook para gerar MAE ou ranking final antes de uma decisão metodológica aprovada.
