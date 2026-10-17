# Dicionário preliminar de variáveis

Este dicionário descreve o que pode ser identificado pelos arquivos recebidos. As fontes e unidades confirmadas estão detalhadas em `docs/FONTES_E_PROVENIENCIA.md`; a disponibilidade futura é uma decisão operacional separada. Nenhuma variável observada no futuro será usada diretamente em uma previsão.

## Base 1

| Variável | Tipo | Descrição preliminar | Uso temporal previsto |
| --- | --- | --- | --- |
| `Date` | data | Chave temporal diária. | Índice temporal. |
| `Open`, `High`, `Low`, `Close` | numérico | Valores de abertura, máximo, mínimo e fechamento de uma série identificada provavelmente como Bitcoin. A fonte original e a unidade ainda não estão confirmadas. | `Close` é alvo proposto. Os demais exigem defasagem ou regra comprovada de disponibilidade. |
| `Adj Close` | numérico | Valor ajustado de fechamento. É idêntico a `Close` nas 2836 linhas recebidas. | Não usar como feature. Manter apenas no bruto para auditoria. |
| `Volume` | numérico | Volume negociado. Unidade não informada no arquivo. | Usar apenas defasado, salvo prova de disponibilidade antecipada. |

## Base 2

| Variável | Tipo | Descrição preliminar | Uso temporal previsto |
| --- | --- | --- | --- |
| `date_time` | data e hora | Timestamp horário. | Índice temporal, com consolidação de timestamps repetidos a definir. |
| `traffic_volume` | numérico | Volume horário de tráfego na I-94 westbound, segundo a fonte UCI. | Alvo proposto. |
| `holiday` | categórico | Nome do feriado. Células vazias representam ausência de feriado e são normalizadas para `No holiday`. | Calendário conhecido antecipadamente, após confirmação da regra de calendário e localidade. |
| `temp`, `rain_1h`, `snow_1h`, `clouds_all` | numérico | Medidas meteorológicas: Kelvin, mm, mm e percentual, respectivamente. | Observações futuras não podem entrar diretamente. Usar previsão disponível na origem, lags ou excluir. |
| `weather_main`, `weather_description` | categórico | Classificação meteorológica. | Mesma regra das medidas meteorológicas. |

## Base 3

| Variável | Tipo | Descrição preliminar | Uso temporal previsto |
| --- | --- | --- | --- |
| `year`, `month`, `day`, `hour` | inteiro | Componentes do timestamp horário. | Formam o índice temporal e permitem features de calendário. |
| `No` | inteiro | Identificador sequencial de registro. | Não usar como feature de previsão. |
| `PM2.5` | numérico | Material particulado fino, em microgramas por metro cúbico, segundo a fonte UCI. | Alvo proposto. |
| `PM10`, `SO2`, `NO2`, `CO`, `O3` | numérico | Medições de poluentes, em microgramas por metro cúbico segundo a fonte UCI. | Lags ou previsão disponível na origem; nunca valor futuro observado. |
| `TEMP`, `PRES`, `DEWP`, `RAIN`, `WSPM` | numérico | Temperatura (°C), pressão (hPa), ponto de orvalho (°C), chuva (mm) e velocidade do vento (m/s). | Lags ou previsão disponível na origem. |
| `wd` | categórico | Direção do vento. | Codificar de forma temporalmente válida. |
| `station` | categórico | Estação de medição. Há um único valor: `Aotizhongxin`. | Remover da matriz de features por não variar. |

## Base 4

| Variável | Tipo | Descrição preliminar | Uso temporal previsto |
| --- | --- | --- | --- |
| `Date Time` | data e hora | Timestamp a cada dez minutos. | Índice temporal. |
| `T (degC)` | numérico | Temperatura em graus Celsius nos dados meteorológicos do Max Planck Institute. | Alvo proposto. |
| `p (mbar)`, `Tpot (K)`, `Tdew (degC)`, `rh (%)`, `VPmax (mbar)`, `VPact (mbar)`, `VPdef (mbar)`, `sh (g/kg)`, `H2OC (mmol/mol)`, `rho (g/m**3)` | numérico | Medidas atmosféricas, com unidade declarada no cabeçalho. | Exigem lag, previsão disponível na origem ou exclusão. |
| `wv (m/s)`, `max. wv (m/s)` | numérico | Velocidade do vento e velocidade máxima. O valor `-9999` é sentinela de ausência. | Converter sentinela em ausência e tratar dentro de cada treino. |
| `wd (deg)` | numérico | Direção do vento em graus. | Converter para forma cíclica apenas dentro da pipeline de features. |

## Base 5

| Variável | Tipo | Descrição preliminar | Uso temporal previsto |
| --- | --- | --- | --- |
| `DATE` | data | Data de observação, com dias sem negociação. | Índice por dias observados de negociação. |
| `GOLD_PRICE` | numérico | Preço do ouro. Unidade e fonte pendentes. | Alvo de trabalho proposto. |
| `TREASURY_10Y`, `FED_FUNDS_RATE` | numérico | Séries compatíveis com DGS10 e DFF do FRED; a correspondência do arquivo deve ser confirmada pelo grupo. | Definir defasagem ou publicação disponível na origem antes de usar. |
| `DAY_OF_WEEK`, `MONTH`, `DOW_SIN`, `DOW_COS`, `MONTH_SIN`, `MONTH_COS` | numérico | Calendário e codificações já calculadas. | Recriar em código a partir de `DATE`; não confiar em versões pré-calculadas. |
| `GOLD_LAG_1`, `GOLD_LAG_5`, `GOLD_LAG_20`, `GOLD_ROLLING_MEAN_5`, `GOLD_ROLLING_STD_5` | numérico | Lags e janelas já calculados. | Recriar dentro da pipeline sem usar o futuro. |
| `TARGET` | numérico | Alvo pré-calculado de definição não documentada. | Não usar até validar formalmente o horizonte e a regra de geração. |
