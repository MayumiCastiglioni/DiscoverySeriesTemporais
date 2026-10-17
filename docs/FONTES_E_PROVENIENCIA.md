# Fontes e proveniência das bases

## Objetivo e regra de uso

Este registro distingue a origem confirmada de uma identificação apenas provável. As cópias em `data/raw` são a evidência de entrada congelada; uma fonte externa só é tratada como confirmada quando a documentação e a estrutura do arquivo são compatíveis. A redistribuição das bases continua bloqueada até que a licença aplicável de cada uma seja confirmada.

| Base | Situação | Fonte ou evidência | Consequência operacional |
| --- | --- | --- | --- |
| 1 | Fonte designada pelo grupo | [Bitget — histórico de Bitcoin](https://www.bitget.com/price/bitcoin/historical-data), informado pelo grupo. A página disponibiliza histórico diário com abertura, máxima, mínima, fechamento e volume. | Tratar `Close` como alvo diário. A cópia congelada continua sendo a entrada experimental e não será redistribuída sem confirmar a licença aplicável. |
| 2 | Confirmada | [UCI Machine Learning Repository — Metro Interstate Traffic Volume](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume). O registro documenta o volume de tráfego na I-94 westbound, o período e as variáveis meteorológicas e de calendário. | Usar `traffic_volume` como alvo candidato horário. As unidades meteorológicas e a localidade podem ser descritas a partir da fonte, mas valores de tempo futuros continuam indisponíveis sem previsão. |
| 3 | Confirmada | [UCI — Beijing Multi-Site Air Quality](https://doi.org/10.24432/C5RK5G). A estrutura, estação `Aotizhongxin` e período horário coincidem com a base fornecida. | Usar `PM2.5` como alvo candidato em microgramas por metro cúbico; confirmar a licença diretamente no registro antes de redistribuir. |
| 4 | Fonte designada pelo grupo e estrutura corroborada | [Kaggle — Weather Archive Jena](https://www.kaggle.com/datasets/pankrzysiu/weather-archive-jena), informado pelo grupo; [tutorial oficial do TensorFlow](https://www.tensorflow.org/tutorials/structured_data/time_series) corrobora a estrutura de 10 minutos e os sentinelas `-9999`. | A unidade dos campos é a indicada no cabeçalho. A regra aprovada é média horária de leituras válidas. |
| 5 | Fonte e tratamento designados pelo grupo | [Base adaptada](https://github.com/TheoMGtech/pls-regration-comparation/tree/develop/bases/grupo5), [fonte diária original](https://github.com/dengyishuo/quantitative-finance/blob/master/gold.daily.prices.csv) e [tratamento](https://github.com/TheoMGtech/pls-regration-comparation/tree/develop/bases/grupo5-tratamento). | Trabalhar semanalmente pelo último preço observado até sexta-feira. Não usar `TARGET` ou features pré-calculadas. |

## Convenções de unidade documentadas

- **Base 2:** `temp` é temperatura em Kelvin; `rain_1h` e `snow_1h` são precipitação em milímetros; `clouds_all` é percentual. `weather_main` e `weather_description` são categorias observadas, não previsões.
- **Base 3:** poluentes (`PM2.5`, `PM10`, `SO2`, `NO2`, `CO`, `O3`) usam microgramas por metro cúbico; `TEMP` e `DEWP` usam graus Celsius; `PRES` usa hPa; `RAIN` usa mm; `WSPM` usa m/s. Essas unidades vêm da documentação do conjunto UCI e serão citadas no relatório final.
- **Base 4:** as unidades já constam nos cabeçalhos e foram corroboradas pela fonte: temperatura em °C, pressão em mbar, umidade relativa em %, direção do vento em graus e velocidades de vento em m/s.

## Pendências que exigem evidência adicional

1. Licença aplicável às Bases 1, 4 e 5 antes de incluir qualquer bruto na entrega.
2. Unidade de `GOLD_PRICE` e regra de construção do `TARGET` pré-calculado da Base 5, que seguirá excluído.
3. Confirmação de que a licença de cada fonte permite incluir o arquivo bruto na entrega. Até lá, permanecem apenas cópias locais ignoradas pelo Git.
