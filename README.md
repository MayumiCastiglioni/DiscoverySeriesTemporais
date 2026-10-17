# DiscoverySeriesTemporais

Projeto de modelagem comparativa e reprodutível de séries temporais com variáveis externas.

O trabalho comparará SARIMAX, Holt-Winters, Random Forest e um modelo de especialização definido pelo grupo, com validação walk-forward e MAE como métrica principal.

## Situação

A Fase 1 reuniu o congelamento, o dicionário, a auditoria e as regras específicas das cinco bases. Os quatro adaptadores de modelo já têm um piloto de origem compartilhada; não há MAE ou ranking final enquanto o horizonte de previsão e o catálogo de variáveis externas não forem fechados.

Consulte [o plano](docs/PLANO_INICIAL.md), as [regras por base](docs/REGRAS_POR_BASE.md), o [plano de execução](docs/PLANO_DE_EXECUCAO.md), as [decisões de dados](docs/DECISOES_DE_DADOS.md), a [auditoria inicial](docs/AUDITORIA_INICIAL_DAS_BASES.md), a [exploração inicial](docs/EXPLORACAO_INICIAL.md), o [protocolo experimental](docs/PROTOCOLO_EXPERIMENTAL_RASCUNHO.md), a [implementação de walk-forward](docs/WALK_FORWARD_IMPLEMENTADO.md), o [modelo XGBoost](docs/MODELO_XGBOOST.md), as [fontes e proveniência](docs/FONTES_E_PROVENIENCIA.md), as [regras e verificações](docs/RULES_E_CHECKS.md) e o [handoff](docs/HANDOFF.md).

## Execução local

Com as dependências de `requirements.txt` instaladas, a sequência inicial pode ser reexecutada a partir da raiz do repositório:

```powershell
python scripts/prepare_structural_data.py
python scripts/profile_candidate_series.py
python scripts/build_target_only_origins.py
python scripts/run_model_pilots.py
python scripts/run_checks.py
python scripts/execute_notebooks.py
```

Os produtos de execução ficam em `reports/generated` e não são versionados. Eles são reconstruídos a partir das entradas congeladas.
