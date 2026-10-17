# Plano de execução

## Estado atual

A configuração de granularidade, semente e divisão temporal foi registrada para as cinco bases. Os cinco tratamentos, ACFs e STLs foram executados em notebooks separados; os vinte notebooks de treinamento piloto também foram executados. O resultado final ainda depende do horizonte de previsão e da aprovação de disponibilidade das variáveis externas.

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
| `notebooks/bases/base01` a `base05` | Uma exploração, tratamento, ACF e STL por base. | Executados; cada um produz o respectivo CSV `cleaned`. |
| `notebooks/modelos/01` a `20` | Um treinamento piloto para cada combinação base-modelo. | Executados; são 20 notebooks e não geram MAE final. |
| `05_avaliacao_walk_forward_final.ipynb` | Mostra o efeito de `HORIZON_STEPS_BY_BASE` e reserva a avaliação final. | Preparado; a prévia não gera MAE e a avaliação permanece bloqueada enquanto essas decisões não existirem. |

As relações de tratamento, períodos de STL e limites de ACF estão em `docs/TRATAMENTO_E_DIAGNOSTICOS_POR_BASE.md`.

## Próxima decisão necessária

Informar o horizonte final por base ou uma regra comum. Com isso, a próxima execução cria a matriz de features aprovada, regenera as origens por grupo e inicia a busca temporal de hiperparâmetros.
