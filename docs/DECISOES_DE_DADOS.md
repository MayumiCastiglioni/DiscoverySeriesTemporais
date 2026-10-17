# Decisões de organização dos dados

## Decisão registrada em 17/10/2026

O projeto utilizará a estrutura `data/raw`, `data/processed` e `data/features`.

- `data/raw` contém cópias congeladas, byte a byte, dos arquivos recebidos. Os originais em `Downloads` não foram alterados.
- `data/processed` recebe somente saídas geradas por código e ainda não contém decisões de features ou de modelagem.
- `data/features` permanecerá vazia até que o horizonte e a disponibilidade temporal sejam definidos; os pilotos atuais usam somente lags do alvo, construídos em memória.

As bases brutas não serão publicadas no Git por enquanto. A decisão será revista quando a fonte, a licença ou a permissão de redistribuição de cada uma forem documentadas. O requisito de entrega poderá ser atendido por bases redistribuíveis ou por referências claras às fontes, conforme aplicável.

## Registro de congelamento

| Base | Arquivo recebido | Cópia local | Tamanho (bytes) | SHA-256 |
| --- | --- | --- | ---: | --- |
| 1 | `raw_base1.csv` | `data/raw/base1.csv` | 282364 | `DCB86B9461168A1CC3F122A40D7AA6B53AC773A5703423320A2A90C3823C38F7` |
| 2 | `raw_base2.csv` | `data/raw/base2.csv` | 3237208 | `749C90D720360A4215BB15345526073C079BA4CC95E3FA558796D083F85FCE9E` |
| 3 | `raw_base3.csv` | `data/raw/base3.csv` | 2835880 | `38155611E0E2DC738CBC546855D8170FB0E39C31243406B07A175DD7B9878B31` |
| 4 | `raw_base4.csv` | `data/raw/base4.csv` | 43584741 | `14539FA8E185A53E97F13936716472243570E310DFB8569495FD0F7BB24F56CF` |
| 5 | `raw_base5.csv` | `data/raw/base5.csv` | 1537922 | `C852759B32F534918F76F9C3A31342228BF0BBC8A61FC5A26A63E61BF93EE64F` |

## Regras de preparação

1. Nunca editar arquivos em `data/raw`.
2. Normalizar a chave de tempo em uma coluna chamada `timestamp` e ordenar os dados cronologicamente.
3. Remover apenas duplicatas que sejam idênticas em todas as colunas. Duplicidades temporais com informações distintas exigem uma regra documentada por base.
4. Converter sentinelas comprovadas em valores ausentes antes de qualquer imputação.
5. Imputar, escalar e criar features dentro de cada janela de treinamento, jamais usando o teste final ou o futuro.
6. Preservar lacunas temporais e dias sem negociação até decidir o tratamento próprio de cada domínio. Não preencher datas automaticamente.

## Situação das decisões por base

| Base | Chave temporal | Alvo de trabalho proposto | Situação |
| --- | --- | --- | --- |
| 1 | `Date` | `Close` | Fonte designada: Bitget; diária; divisão temporal 70% / 30%; semente 42. |
| 2 | `date_time` | `traffic_volume` | Fonte confirmada: UCI; horária; divisão 80% / 20%; semente 67. A agregação das externas repetidas será documentada antes das features. |
| 3 | `year`, `month`, `day`, `hour` | `PM2.5` | Fonte confirmada: UCI; horária; divisão 80% / 20%; semente 42. Ausências do alvo permanecem ausências. |
| 4 | `Date Time` | `T (degC)` | Fonte designada: Kaggle; média horária de leituras válidas; divisão 80% / 20%; semente 42. |
| 5 | `DATE` | `GOLD_PRICE` | Fonte adaptada e tratamento designados; semanal `W-FRI` pelo último preço observado; divisão 75% / 25%; semente 42. `TARGET` permanece excluído. |

O script `scripts/prepare_structural_data.py` implementa somente as decisões estruturais já aprovadas nesta página. Ele não escolhe features, não imputa ausências e não realiza qualquer ajuste de modelo.
