# Auditoria inicial das bases

## Resultado da inspeção

| Base | Linhas x colunas | Cobertura temporal | Frequência predominante | Achado principal |
| --- | ---: | --- | --- | --- |
| 1 | 2836 x 7 | 2017-01-01 a 2024-10-06 | diária, sem lacunas | Sem ausências ou duplicatas. `Adj Close` duplica `Close`. |
| 2 | 48204 x 9 | 2012-10-02 09:00 a 2018-09-30 23:00 | horária | 5445 timestamps repetidos, sem divergência em `traffic_volume`. |
| 3 | 35064 x 18 | 2013-03-01 00:00 a 2017-02-28 23:00 | horária, regular | 3249 linhas têm ao menos uma ausência, incluindo 925 no alvo proposto `PM2.5`. |
| 4 | 420551 x 15 | 2009-01-01 00:10 a 2017-01-01 00:00 | 10 minutos | 327 duplicatas exatas, 2 inversões de ordem, 5 lacunas e sentinelas `-9999` no vento. |
| 5 | 9864 x 16 | 1968-04-29 a 2014-04-09 | dias observados de negociação | Já contém target e features derivados, portanto exige reconstrução independente. |

## Decisões de tratamento estrutural

### Base 1

- Normalizar e ordenar o timestamp.
- Manter a série íntegra. Não usar `Adj Close` como preditor porque ela é idêntica ao alvo proposto em todas as linhas.
- A fonte Bitget foi designada pelo grupo; confirmar a unidade antes da interpretação final.

### Base 2

- Converter as 48143 células vazias de `holiday` em `No holiday`, preservando o significado de ausência de feriado sem criar uma nova ausência ao reler o CSV.
- Preservar por ora as 5445 chaves repetidas. O alvo é idêntico entre registros de cada uma dessas chaves, mas as variáveis meteorológicas precisam de uma regra de agregação justificada pela fonte antes de consolidar em uma série horária.
- Investigar o único valor de `rain_1h` acima de 100, pois o percentil 99,9% é 13,60 e esse ponto pode ser erro de unidade ou medição extrema.

### Base 3

- Criar `timestamp` a partir de ano, mês, dia e hora e manter a sequência horária regular.
- Não imputar as 925 ausências do alvo. Origens que necessitem desse valor deverão ser excluídas da avaliação ou receber uma política tecnicamente justificada.
- Tratar ausências das variáveis externas dentro de cada janela de treinamento, sem calcular estatísticas com o futuro.
- Remover `station` da futura matriz de features, pois ela possui apenas um valor.

### Base 4

- Remover 327 linhas que são duplicatas exatas e ordenar cronologicamente.
- Converter `-9999` para ausência: 18 ocorrências em `wv (m/s)` e 20 em `max. wv (m/s)`.
- Preservar as cinco lacunas de tempo, cuja maior duração é 3 dias e 2 horas e 20 minutos. A regularização será escolhida antes da STL e do walk-forward, não por preenchimento automático.

### Base 5

- Reamostrar em semanas encerradas na sexta-feira usando o último preço observado, sem criar valores sintéticos para fim de semana ou feriado.
- Não usar `TARGET` nem as features pré-calculadas. A comparação entre `TARGET` e o próximo `GOLD_PRICE` observado coincide em apenas 95,66% das linhas, logo a definição não é suficientemente confiável.
- Reconstruir lags, médias móveis e calendário diretamente de `GOLD_PRICE` e `DATE` dentro da pipeline temporal.

## Preparação estrutural executada

A preparação estrutural reproduzível foi executada por `scripts/prepare_structural_data.py`. Ela normalizou timestamps em todas as bases, corrigiu somente as duplicatas e sentinelas comprovadas, e preservou os demais pontos para decisões posteriores. Os checks confirmaram a ordem temporal e timestamps válidos nas cinco saídas, a remoção das duplicatas exatas da base 4, a ausência de sentinelas `-9999` e a integridade dos checksums dos cinco arquivos congelados.

## Próxima etapa técnica

As frequências, cortes e sementes já estão configurados. O próximo passo técnico depende de registrar o horizonte final e o catálogo de disponibilidade de variáveis externas; então serão geradas features, aplicada a máscara comum de elegibilidade e reconstruídas as agendas walk-forward.
