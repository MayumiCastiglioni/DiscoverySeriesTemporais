# Fontes e proveniência das bases

## Objetivo e regra de uso

Este registro distingue a origem confirmada de uma identificação apenas provável. As cópias em `data/raw` são a evidência de entrada congelada; uma fonte externa só é tratada como confirmada quando a documentação e a estrutura do arquivo são compatíveis. A redistribuição das bases continua bloqueada até que a licença aplicável de cada uma seja confirmada.

| Base | Situação | Fonte ou evidência | Consequência operacional |
| --- | --- | --- | --- |
| 1 | Identidade provável; origem original pendente | Os valores e o formato são compatíveis com uma série diária histórica de Bitcoin. Há uma referência pública com linhas coincidentes, mas ela não comprova a fonte original nem a licença. | Tratar `Close` como alvo candidato em unidade monetária não confirmada. Não publicar a cópia nem apresentar a procedência como fechada. |
| 2 | Confirmada | [UCI Machine Learning Repository — Metro Interstate Traffic Volume](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume). O registro documenta o volume de tráfego na I-94 westbound, o período e as variáveis meteorológicas e de calendário. | Usar `traffic_volume` como alvo candidato horário. As unidades meteorológicas e a localidade podem ser descritas a partir da fonte, mas valores de tempo futuros continuam indisponíveis sem previsão. |
| 3 | Confirmada | [UCI — Beijing Multi-Site Air Quality](https://doi.org/10.24432/C5RK5G). A estrutura, estação `Aotizhongxin` e período horário coincidem com a base fornecida. | Usar `PM2.5` como alvo candidato em microgramas por metro cúbico; confirmar a licença diretamente no registro antes de redistribuir. |
| 4 | Confirmada | [Tutorial oficial de séries temporais do TensorFlow](https://www.tensorflow.org/tutorials/structured_data/time_series), que referencia os dados meteorológicos do Max Planck Institute, a cadência de 10 minutos e os sentinelas `-9999` do vento. | A unidade dos campos é a indicada no cabeçalho. A agregação horária ainda é uma decisão metodológica, não uma propriedade do arquivo bruto. |
| 5 | Parcial | [FRED — DGS10](https://fred.stlouisfed.org/series/DGS10) e [FRED — DFF](https://fred.stlouisfed.org/series/DFF) confirmam as duas séries de taxas compatíveis com as colunas. A fonte, unidade e regra de formação de `GOLD_PRICE` não foram encontradas. | Não atribuir uma fonte única à base e não usar `TARGET` ou features pré-calculadas. Solicitar a planilha, o link ou a regra que gerou a série de ouro. |

## Convenções de unidade documentadas

- **Base 2:** `temp` é temperatura em Kelvin; `rain_1h` e `snow_1h` são precipitação em milímetros; `clouds_all` é percentual. `weather_main` e `weather_description` são categorias observadas, não previsões.
- **Base 3:** poluentes (`PM2.5`, `PM10`, `SO2`, `NO2`, `CO`, `O3`) usam microgramas por metro cúbico; `TEMP` e `DEWP` usam graus Celsius; `PRES` usa hPa; `RAIN` usa mm; `WSPM` usa m/s. Essas unidades vêm da documentação do conjunto UCI e serão citadas no relatório final.
- **Base 4:** as unidades já constam nos cabeçalhos e foram corroboradas pela fonte: temperatura em °C, pressão em mbar, umidade relativa em %, direção do vento em graus e velocidades de vento em m/s.

## Pendências que exigem evidência do grupo

1. Link, planilha de origem ou licença da Base 1.
2. Fonte e unidade de `GOLD_PRICE`, regra de construção da Base 5 e significado de `TARGET`.
3. Confirmação de que a licença de cada fonte permite incluir o arquivo bruto na entrega. Até lá, permanecem apenas cópias locais ignoradas pelo Git.

## Referência pública de coincidência da Base 1

A referência abaixo é mantida somente como evidência de identificação de conteúdo, não como citação da fonte original: [amostra pública de cotações históricas](https://gist.github.com/yasserius/61ebfe583cb6d5122c3ba23064441ac5). A origem primária e a licença continuam pendentes.
