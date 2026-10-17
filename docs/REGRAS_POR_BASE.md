# Regras confirmadas por base

As regras nesta página foram fornecidas pelo grupo em 17/10/2026 e estão espelhadas em `configs/base_experiment_rules.json`. Todos os modelos de uma base leem a mesma configuração.

| Grupo | Base | Fonte designada | Granularidade aplicada | Treino / teste | Semente |
| --- | ---: | --- | --- | --- | ---: |
| Grupo 1 | 1 | [Bitget — histórico de Bitcoin](https://www.bitget.com/price/bitcoin/historical-data) | Diária | 70% / 30% | 42 |
| Grupo 2 | 2 | [UCI — Metro Interstate Traffic Volume](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume) | Horária | 80% / 20% | 67 |
| Grupo 3 | 3 | [UCI — Beijing Multi-Site Air Quality](https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data) | Horária | 80% / 20% | 42 |
| Grupo 4 | 4 | [Kaggle — Weather Archive Jena](https://www.kaggle.com/datasets/pankrzysiu/weather-archive-jena) | Horária | 80% / 20% | 42 |
| Grupo 5 | 5 | [Base adaptada do grupo](https://github.com/TheoMGtech/pls-regration-comparation/tree/develop/bases/grupo5) | Semanal | 75% / 25% | 42 |

## Regras de transformação necessárias

### Base 1

`Close` permanece o alvo diário. A fonte designada pelo grupo disponibiliza dados históricos diários com abertura, máxima, mínima, fechamento e volume. Os campos do mesmo dia só poderão entrar como defasagens ao prever o período seguinte.

### Base 2

O alvo é consolidado em uma observação por hora após verificar que valores repetidos de `traffic_volume` não divergem. As variáveis meteorológicas repetidas serão agregadas por regra documentada antes da matriz de features: média para medidas contínuas e moda determinística para categorias, com desempate lexicográfico. Horas sem observação continuam lacunas, não valores de tráfego iguais a zero.

### Base 3

O alvo `PM2.5` já é horário. As ausências permanecem ausências. Uma origem ou um alvo de horizonte sem valor observado é removido da agenda comum de todos os modelos, nunca apenas de um modelo.

### Base 4

O dado de 10 minutos é convertido para uma série horária pela média das leituras válidas de `T (degC)` em cada hora. Uma hora sem leitura permanece ausente. O arquivo bruto de 10 minutos não é modificado.

### Base 5

A série é convertida para semanas encerradas na sexta-feira (`W-FRI`), usando o último `GOLD_PRICE` observado na semana. Essa convenção preserva uma semana de negociação incompleta sem inventar preço para o fim de semana. Na versão recebida há 2.398 semanas no intervalo, 254 delas sem preço observado; elas continuam ausentes e não formam origem ou alvo de avaliação. `TARGET`, lags, médias móveis e calendário já presentes no CSV continuam excluídos e serão recriados por código.

As fontes da série original e do tratamento informado são [a fonte diária original](https://github.com/dengyishuo/quantitative-finance/blob/master/gold.daily.prices.csv) e [o repositório de tratamento](https://github.com/TheoMGtech/pls-regration-comparation/tree/develop/bases/grupo5-tratamento).

## Horizonte e comparabilidade

O grupo não informou um horizonte de previsão final. Por isso, `h = 1` é usado somente para os pilotos de infraestrutura. Antes de gerar MAE final, o horizonte deve ser registrado nesta configuração. Independentemente do horizonte escolhido, a agenda de origens será gerada uma única vez por base e aplicada, na mesma ordem, a SARIMAX, Holt-Winters, Random Forest e XGBoost.
