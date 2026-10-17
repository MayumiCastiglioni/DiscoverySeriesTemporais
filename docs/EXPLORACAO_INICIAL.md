# Exploração inicial das séries candidatas

## Escopo da exploração

Este documento registra uma exploração numérica reproduzível das saídas estruturais, executada por `scripts/profile_candidate_series.py`. Não há imputação, filtro de outliers, transformação, seleção de variáveis, ajuste de modelo ou resultado de previsão nesta etapa.

Nas Bases 2 e 4, os números explicitamente marcados como *exploratórios* não criam um conjunto de modelagem: servem apenas para informar a decisão de agregação descrita no protocolo rascunhado.

## Resumo temporal e do alvo candidato

| Base | Alvo candidato | Cobertura | Observações úteis | Achado inicial |
| --- | --- | --- | ---: | --- |
| 1 | `Close` | 2017-01-01 a 2024-10-06 | 2.836 diárias | Sem ausências ou timestamps repetidos. |
| 2 | `traffic_volume` | 2012-10-02 09:00 a 2018-09-30 23:00 | 48.204 brutas; 40.575 timestamps distintos | Há 5.445 grupos de timestamps repetidos e 11.976 horas de calendário sem observação após a consolidação apenas do alvo. |
| 3 | `PM2.5` | 2013-03-01 00:00 a 2017-02-28 23:00 | 35.064 horárias | 925 ausências no alvo; a grade temporal continua regular. |
| 4 | `T (degC)` | 2009-01-01 00:10 a 2017-01-01 00:00 | 420.224 em 10 min após deduplicação | A média horária exploratória tem 70.129 horas, das quais 88 não têm observação. |
| 5 | `GOLD_PRICE` | 1968-04-29 a 2014-04-09 | 9.864 dias observados | Série de negociações; fins de semana e feriados não são valores ausentes a preencher. |

## Persistência inicial

As correlações abaixo são descritivas, não comprovam estacionariedade e não definem automaticamente lags de modelos.

| Base | Correlações de defasagem | Interpretação inicial |
| --- | --- | --- |
| 1 | 1 dia: 0,998693; 7 dias: 0,990909; 30 dias: 0,959931; 365 dias: 0,352448 | Forte dependência de curto prazo, coerente com nível de preço não estacionário. Transformações e diagnóstico serão decididos dentro dos treinos. |
| 2 | 1 h: 0,913759; 24 h: 0,863785; 168 h: 0,947736 | A dependência semanal exploratória é muito forte; a base requer uma regra de consolidação e de lacunas antes de aplicar STL. |
| 3 | 1 h: 0,969436; 24 h: 0,394051; 168 h: 0,018116 | Grande persistência de curtíssimo prazo, mas as ausências no alvo impedem qualquer preenchimento retrospectivo. |
| 4 | 1 h: 0,993584; 24 h: 0,919218; 168 h: 0,763729 na média horária exploratória | Há estrutura diária e semanal potencial. A análise formal dependerá da escolha da agregação horária. |
| 5 | 1 observação: 0,999749; 5: 0,998815; 20: 0,995410; 252: 0,937168 | Persistência extrema de nível; o horizonte deve ser definido em observações de negociação, não em dias de calendário preenchidos. |

## Estatísticas do alvo candidato

| Base | Média | Mediana | Mínimo | Máximo | Ausências | Pontos fora da cerca de Tukey |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 23.262,04 | 16.603,53 | 777,76 | 73.083,50 | 0 | 0 |
| 2* | 3.290,65 | 3.427,00 | 0,00 | 7.280,00 | 0 | 0 |
| 3 | 82,77 | 58,00 | 3,00 | 898,00 | 925 | 1.624 |
| 4* | 9,44 | 9,41 | -22,65 | 37,04 | 88 horas | 248 |
| 5 | 446,17 | 364,05 | 34,78 | 1.891,00 | 0 | 1.416 |

\* Base 2 usa uma série exploratória de um alvo por timestamp; Base 4 usa média horária exploratória. Não são dados de treinamento aprovados.

## Implicações já registradas

- Os valores altos de poluição e de ouro não devem ser removidos por uma regra estatística isolada: podem representar episódios reais ou mudanças de nível. Qualquer tratamento precisará de justificativa de domínio e será aprendido apenas no treino.
- A Base 2 precisa manter lacunas como lacunas; não será criado tráfego sintético para horas não observadas.
- A Base 3 não pode usar `PM2.5` futuro para preencher suas próprias ausências; as janelas de avaliação inválidas serão descartadas de modo explícito, se essa for a decisão aprovada.
- A Base 4 preserva a cadência de 10 minutos no dado estrutural. A média por hora é somente uma proposta para tornar a comparação e a decomposição mais manejáveis.
- A Base 5 terá calendário e lags reconstruídos a partir da data e do alvo, descartando os campos pré-calculados recebidos.

## Próximo artefato de exploração

Após a aprovação das frequências e horizontes propostos, gerar gráficos de nível, sazonalidade e STL por base, com períodos escolhidos e justificados. O script acima poderá ser reexecutado para auditar que essa próxima etapa parte das mesmas entradas estruturais.
