# Walk-forward implementado

## Objetivo

O walk-forward mede uma previsão feita em uma origem temporal usando somente o histórico disponível naquela origem. Para uma origem `t` e horizonte `h = 1`, cada modelo é treinado com observações até `t`, prevê o alvo em `t + 1` e só então esse alvo é usado para calcular o erro.

## O que já foi implementado e executado

O módulo `src/discovery_series_temporais/series.py` cria uma agenda canônica de origens antes da execução dos modelos. A rotina `scripts/build_target_only_origins.py` foi executada sobre as cinco bases estruturais com as opções provisórias abaixo:

| Regra | Implementação atual |
| --- | --- |
| Horizonte | Uma etapa à frente (`h = 1`). |
| Teste final | Últimos 20% das origens temporalmente válidas. O tamanho é arredondado para cima. |
| Janela de treino | Expansiva: toda a história anterior à origem. |
| Agenda | Um CSV por base em `reports/generated/origin_schedules`, ignorado pelo Git por ser produto reexecutável. |
| Checagem | `assert_same_origins` exige que SARIMAX, Holt-Winters, Random Forest e XGBoost recebam exatamente a mesma agenda, na mesma ordem. |

Os testes automatizados verificam tanto a aceitação de agendas iguais quanto a rejeição de uma agenda com uma origem removida. Um modelo não poderá reportar MAE se sua agenda for diferente da agenda canônica da base.

## Interpretação de uma etapa por base

| Base | Regra temporal aplicada à origem `t` | Origens provisórias no teste final |
| --- | --- | ---: |
| 1 | `target_timestamp = t + 1 dia` | 567 |
| 2 | `target_timestamp = t + 1 hora`; lacunas de calendário são excluídas | 7.598 |
| 3 | `target_timestamp = t + 1 hora`; origem ou alvo ausente é excluído | 6.786 |
| 4 | Média horária exploratória e `target_timestamp = t + 1 hora`; horas sem observação são excluídas | 14.008 |
| 5 | Próxima observação de negociação disponível | 1.973 |

## Fluxo final obrigatório

1. Construir uma matriz de features comum e temporalmente permitida para a base.
2. Formar uma máscara de elegibilidade que exclua qualquer origem sem o histórico mínimo dessa matriz.
3. Gerar novamente a agenda canônica usando essa máscara comum, sem separar agendas por modelo.
4. Ajustar hiperparâmetros somente no período anterior ao teste final, com walk-forward expansivo interno.
5. Para cada origem da agenda final, reestimar cada modelo com a janela expansiva, produzir uma previsão e salvar `origin_id`, data da origem, data do alvo, modelo, previsão, observado e erro absoluto.
6. Executar `assert_same_origins` sobre as quatro tabelas de previsões antes de calcular MAE e rankings.

## Limite da execução atual

As agendas geradas agora são **provisórias e baseadas apenas no alvo**. Elas comprovam a infraestrutura temporal, a regra de lacunas e a igualdade de origens entre consumidores. Antes do resultado final, serão regeneradas a partir da interseção das features aprovadas para os quatro modelos. Assim, uma observação não será removida para apenas um modelo e a comparação continuará justa.
