# Plano de execução

## Estado atual

A configuração de granularidade, semente e divisão temporal foi registrada para as cinco bases. Os quatro adaptadores de modelos existem e são executados em um piloto de origem compartilhada. O resultado final ainda depende do horizonte de previsão e da aprovação de disponibilidade das variáveis externas.

## Etapas

| Etapa | Entrega | Regra de conclusão |
| --- | --- | --- |
| 1. Configurar séries | Aplicar as granularidades por grupo, congelar as regras em JSON e verificar as lacunas após a agregação. | Nenhuma entrada bruta é alterada; cada série possui timestamps ordenados e regra de agregação rastreável. |
| 2. Explorar e decompor | Executar gráficos e STL com períodos compatíveis para cada série regularizada. | Tendência, sazonalidade, resíduos e força sazonal documentados sem imputação retrospectiva. |
| 3. Construir features | Criar lags, janelas e calendário; incluir apenas variáveis externas disponíveis na origem. | A mesma matriz de features aprovada serve Random Forest e XGBoost; Holt-Winters permanece univariado. |
| 4. Definir origens | Aplicar o horizonte final e a interseção de linhas elegíveis para criar uma agenda canônica por base. | SARIMAX, Holt-Winters, Random Forest e XGBoost recebem a mesma lista e ordem de `origin_id`. |
| 5. Ajustar modelos | Otimizar parâmetros em walk-forward interno apenas no treino. | Hiperparâmetros ficam congelados antes de tocar o teste final. |
| 6. Avaliar | Executar walk-forward expansivo final e salvar previsões, resíduos e MAE. | A checagem de origens passa antes de qualquer ranking. |
| 7. Interpretar e relatar | Gerar diagnósticos de resíduos, importância e relatório HTML/PDF. | Conclusões citam a execução e suas limitações. |

## Notebooks

| Notebook | Papel | Situação |
| --- | --- | --- |
| `01_auditoria_e_stl_preliminar.ipynb` | Auditoria e STL onde a série já está regular. | Executável; STL completa das demais bases depende da etapa 1. |
| `02_origens_e_xgboost_piloto.ipynb` | Agenda de origens e piloto de XGBoost. | Executável; não calcula MAE final. |
| `03_regras_e_preparacao_por_grupo.ipynb` | Verifica configurações, granularidades e divisões específicas. | Executável. |
| `04_pilotos_dos_quatro_modelos.ipynb` | Executa SARIMAX, Holt-Winters, Random Forest e XGBoost na mesma origem piloto. | Executável; não é comparação final. |
| `05_avaliacao_walk_forward_final.ipynb` | Orquestra a avaliação final depois da definição de horizonte e features. | Preparado; bloqueia resultados finais enquanto essas decisões não existirem. |

## Próxima decisão necessária

Informar o horizonte final por base ou uma regra comum. Com isso, a próxima execução cria a matriz de features aprovada, regenera as origens por grupo e inicia a busca temporal de hiperparâmetros.
