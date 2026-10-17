# DiscoverySeriesTemporais

Projeto de modelagem comparativa e reprodutível de séries temporais com variáveis externas.

O trabalho comparará SARIMAX, Holt-Winters, Random Forest e um modelo de especialização definido pelo grupo, com validação walk-forward e MAE como métrica principal.

## Situação

A Fase 1 reuniu o congelamento, o dicionário, a auditoria, o tratamento por base, ACF, STL e as regras específicas das cinco bases. Há cinco notebooks de exploração/tratamento e vinte notebooks de treinamento individual. Não há MAE ou ranking final enquanto o horizonte de previsão e o catálogo de variáveis externas não forem fechados.

Consulte [o plano](docs/PLANO_INICIAL.md), as [regras por base](docs/REGRAS_POR_BASE.md), o [plano de execução](docs/PLANO_DE_EXECUCAO.md), o [tratamento e diagnósticos](docs/TRATAMENTO_E_DIAGNOSTICOS_POR_BASE.md), o [guia de execução manual](docs/EXECUCAO_MANUAL.md), as [decisões de dados](docs/DECISOES_DE_DADOS.md), a [auditoria inicial](docs/AUDITORIA_INICIAL_DAS_BASES.md), a [exploração inicial](docs/EXPLORACAO_INICIAL.md), o [protocolo experimental](docs/PROTOCOLO_EXPERIMENTAL_RASCUNHO.md), a [implementação de walk-forward](docs/WALK_FORWARD_IMPLEMENTADO.md), o [modelo XGBoost](docs/MODELO_XGBOOST.md), as [fontes e proveniência](docs/FONTES_E_PROVENIENCIA.md), as [regras e verificações](docs/RULES_E_CHECKS.md) e o [handoff](docs/HANDOFF.md).

## Execução local

Com as dependências de `requirements.txt` instaladas, a sequência inicial pode ser reexecutada a partir da raiz do repositório:

```powershell
python scripts/prepare_structural_data.py
python scripts/build_cleaned_data.py
python scripts/generate_course_notebooks.py
python scripts/run_checks.py
python scripts/execute_notebooks.py
python scripts/verify_training_pilots.py
```

Os produtos de execução ficam em `reports/generated` e não são versionados. Eles são reconstruídos a partir das entradas congeladas.
