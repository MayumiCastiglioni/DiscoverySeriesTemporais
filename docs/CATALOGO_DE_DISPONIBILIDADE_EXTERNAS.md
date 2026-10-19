# Catálogo de disponibilidade das variáveis externas

## Finalidade

Este catálogo transforma a regra de disponibilidade temporal em uma configuração verificável. A matriz comum de features é construída por `src/discovery_series_temporais/features.py` a partir de `configs/feature_availability_policy.json`.

Ele não afirma que uma observação externa é conhecida antecipadamente. Enquanto não houver documentação da origem e do horário de divulgação, a regra conservadora é usar somente o valor da variável externa observado no período imediatamente anterior. As variáveis de calendário são calculadas para a data a ser prevista, pois essa data já é conhecida na origem.

## Regra operacional comum

- A linha de origem `t` usa `external_lag_1__variavel = variavel(t-1)`.
- A resposta é `target(t+h)`; logo, não entra nenhum valor observado posterior a `t` na linha de origem.
- Uma ausência externa não exclui a origem: a imputação, quando aplicável, será ajustada somente com o treino de cada origem. Isso evita deslocar a agenda comum por falhas em apenas uma fonte.
- Ausências no alvo da origem ou do rótulo futuro excluem a origem de todos os modelos, incluindo Holt-Winters. A agenda também requer pelo menos três alvos consecutivos até a origem, pois este é o mínimo técnico da referência Holt-Winters não sazonal; a exigência é comum a todos os modelos. Uma ausência em um lag ou janela histórica é mantida como feature ausente e tratada pelo mecanismo ajustado apenas no treino de cada origem; isso evita eliminar artificialmente toda a Base 5 por suas lacunas semanais históricas.
- O catálogo e seu hash devem acompanhar toda execução final.

## Variáveis permitidas na configuração provisória

| Base | Variáveis externas incluídas, sempre com defasagem de 1 período | Excluídas por enquanto |
| --- | --- | --- |
| 1 | `Open`, `High`, `Low`, `Volume` | `Adj Close` |
| 2 | `temp`, `rain_1h`, `snow_1h`, `clouds_all` | `holiday`, `weather_main`, `weather_description` |
| 3 | `PM10`, `SO2`, `NO2`, `CO`, `O3`, `TEMP`, `PRES`, `DEWP`, `RAIN`, `WSPM` | `wd`, `station`, identificadores e componentes de data fornecidos |
| 4 | variáveis meteorológicas numéricas, incluindo seno e cosseno da direção do vento | nenhuma adicional |
| 5 | nenhuma | `TREASURY_10Y`, `FED_FUNDS_RATE` |

## Limite que ainda exige decisão

O catálogo é uma política conservadora e reproduzível, não uma confirmação de calendário de publicação das fontes. Antes da avaliação final, o grupo deve confirmar se aprova essa regra de uma defasagem ou fornecer, para cada variável, a disponibilidade real. Até isso ocorrer, o código pode ser testado, mas não serão produzidos resultados finais.

## Relação com a comparabilidade

O `eligible_for_common_schedule` não depende de uma ausência pontual externa nem de um lag ausente; esses valores serão imputados de modo ajustado apenas dentro do treino de cada origem. Ele exige alvo atual, alvo futuro no horizonte, calendário regular e três alvos consecutivos até a origem, o mínimo comum imposto por Holt-Winters. Assim, depois de criada a agenda canônica, os quatro modelos recebem os mesmos `origin_id`, na mesma ordem, com o mesmo `h` e os mesmos valores reais. O check de igualdade de origens bloqueia o MAE se uma previsão tiver origem ausente, extra ou reordenada.
