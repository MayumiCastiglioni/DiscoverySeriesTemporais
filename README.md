# DiscoverySeriesTemporais

Projeto de modelagem comparativa e reprodutível de séries temporais com variáveis externas.

O trabalho comparará SARIMAX, Holt-Winters, Random Forest e um modelo de especialização definido pelo grupo, com validação walk-forward e MAE como métrica principal.

## Situação

A Fase 1 começou com o congelamento, o dicionário e a auditoria das cinco bases. A exploração descritiva e o registro de procedência também foram iniciados, sem modelagem ou definição implícita de horizonte.

Consulte [o plano](docs/PLANO_INICIAL.md), as [decisões de dados](docs/DECISOES_DE_DADOS.md), a [auditoria inicial](docs/AUDITORIA_INICIAL_DAS_BASES.md), a [exploração inicial](docs/EXPLORACAO_INICIAL.md), o [protocolo experimental em rascunho](docs/PROTOCOLO_EXPERIMENTAL_RASCUNHO.md), a [implementação de walk-forward](docs/WALK_FORWARD_IMPLEMENTADO.md), o [modelo XGBoost](docs/MODELO_XGBOOST.md), as [fontes e proveniência](docs/FONTES_E_PROVENIENCIA.md), as [regras e verificações](docs/RULES_E_CHECKS.md) e o [handoff](docs/HANDOFF.md).

## Execução local

Com as dependências de `requirements.txt` instaladas, a sequência inicial pode ser reexecutada a partir da raiz do repositório:

```powershell
python scripts/prepare_structural_data.py
python scripts/profile_candidate_series.py
python scripts/build_target_only_origins.py
python scripts/execute_notebooks.py
```

Os produtos de execução ficam em `reports/generated` e não são versionados. Eles são reconstruídos a partir das entradas congeladas.
