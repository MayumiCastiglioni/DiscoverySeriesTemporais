# Protocolo experimental — rascunho para aprovação

## Status

**Proposta, não configuração final.** Este rascunho transforma os achados iniciais em opções explícitas para avaliação. Nenhuma agregação de modelagem, feature, corte de teste ou modelo foi criado a partir dele.

## Convenção comum sugerida

| Elemento | Proposta inicial | Proteção contra vazamento |
| --- | --- | --- |
| Horizonte | Uma observação à frente (`h = 1`) em cada frequência aprovada. Na Base 5, uma observação equivale ao próximo dia de negociação observado. | O alvo da previsão é estritamente posterior à origem. |
| Teste final | Últimos 20% das origens temporalmente válidas de cada base. | Não usar o teste para imputar, selecionar features ou otimizar hiperparâmetros. |
| Ajuste de hiperparâmetros | Validação walk-forward expansiva somente dentro dos 80% iniciais. | Fixar a configuração vencedora antes do walk-forward final. |
| Avaliação final | Walk-forward expansivo, reestimando cada modelo em cada origem válida. Registrar previsão, valor observado, erro absoluto e resíduos. | Mesmas origens e horizonte para todos os modelos de uma mesma base. |
| Métrica | MAE por base e por modelo. | Não calcular média de MAE entre bases de escalas diferentes. |

O percentual de teste e o horizonte são escolhas iniciais para aprovação do grupo. Se o enunciado ou a especialização exigir outro horizonte, esta página deverá ser atualizada antes da criação das features.

## Proposta por base

| Base | Frequência proposta | Alvo | Tratamento anterior à modelagem | Ponto que requer aprovação |
| --- | --- | --- | --- | --- |
| 1 | Diária | `Close` | Manter o calendário diário observado; criar lags e calendário apenas com dados anteriores à origem. | Confirmar fonte, unidade e se a previsão desejada é de preço em nível ou transformação de retorno. |
| 2 | Horária | `traffic_volume` | Consolidar um alvo por timestamp porque os valores do alvo são idênticos no grupo. Para variáveis externas, documentar uma agregação determinística por tipo de variável antes de gerar qualquer arquivo. | Confirmar se a unidade analítica será uma hora e a semântica das medições meteorológicas repetidas. |
| 3 | Horária | `PM2.5` | Manter a grade de horas; não imputar o alvo. Imputar externals somente com transformador ajustado no treino, se forem aprovadas como disponíveis. | Aprovar exclusão documentada de origens/janelas sem alvo observável ou outra política de ausência. |
| 4 | Horária, por média das leituras válidas em cada hora | `T (degC)` | Preservar o bruto de 10 minutos; criar uma saída de modelagem separada, sem preencher as 88 horas sem observação. | Aprovar média horária em vez de amostragem de uma leitura a cada seis registros. |
| 5 | Índice de dias de negociação observados | `GOLD_PRICE` | Recriar calendário, lags e janelas dentro da pipeline. Não usar `TARGET` nem campos pré-calculados do arquivo. | Confirmar fonte, unidade e se `h = 1` significa o próximo pregão. |

## Catálogo inicial de disponibilidade das variáveis externas

| Tipo | Situação inicial | Regra até haver evidência adicional |
| --- | --- | --- |
| Calendário derivado da origem (dia da semana, mês, feriado com localidade confirmada) | Conhecido na origem. | Pode entrar como feature após ser reconstruído em código. |
| Preço de abertura, máximo, mínimo, fechamento e volume na mesma data | Observado após ou durante a janela que se pretende prever. | Usar somente valores defasados; excluir o valor contemporâneo. |
| Meteorologia medida | Observada, não previsão meteorológica documentada. | Usar somente defasagens; valores futuros só serão permitidos com uma fonte de previsão disponível na origem. |
| Poluentes e medidas ambientais na mesma hora | Observadas na hora. | Usar somente defasagens até que exista previsão operacional documentada. |
| Taxas financeiras macroeconômicas | A disponibilidade intradiária e a data de publicação não foram confirmadas. | Excluir por enquanto; se aprovadas, usar defasagem conservadora baseada na publicação. |

## Regras específicas de dados irregulares

1. Não converter lacunas em observações artificiais. Em particular, não criar tráfego para a Base 2, não preencher `PM2.5` futuro e não inventar preço de ouro em dias sem negociação.
2. Transformações numéricas, imputadores, escaladores e codificadores serão ajustados em cada janela de treino e aplicados à origem seguinte, nunca ao conjunto inteiro.
3. Uma origem só é válida quando o histórico exigido pelas features existe e o alvo do horizonte está observado. A razão de exclusões será salva junto às previsões.
4. Holt-Winters será univariado. SARIMAX, Random Forest e o modelo de especialização só receberão variáveis externas que estejam no catálogo como temporalmente permitidas.

## Condições para transformar este rascunho em configuração

1. Aprovação explícita das cinco frequências e do horizonte, ou substituição por escolhas do enunciado.
2. Identificação do modelo de especialização do grupo.
3. Confirmação ou documentação das fontes pendentes das Bases 1 e 5.
4. Para a Base 2, regra de agregação de cada variável externa e para a Base 4, concordância com a agregação horária.

Com essas decisões, a próxima mudança criará uma configuração versionada por base e os testes automáticos de validação temporal.
