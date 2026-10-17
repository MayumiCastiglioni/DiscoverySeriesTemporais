# Protocolo experimental

## Status

**Parcialmente confirmado.** Granularidade, cortes temporais e sementes foram fornecidos pelo grupo e estão configurados. O horizonte final e o catálogo de disponibilidade temporal de variáveis externas ainda não foram fornecidos; por isso não há MAE, ranking ou conclusão final.

## Convenção comum

| Elemento | Regra atual | Proteção contra vazamento |
| --- | --- | --- |
| Horizonte | **Pendente.** Uma etapa à frente (`h = 1`) é usada apenas no piloto de infraestrutura, sem resultado final. | O alvo da previsão será estritamente posterior à origem. |
| Teste final | Últimas 30%, 20%, 20%, 20% e 25% das origens válidas das Bases 1–5, respectivamente. | Não usar o teste para imputar, selecionar features ou otimizar hiperparâmetros. |
| Ajuste de hiperparâmetros | Validação walk-forward expansiva somente dentro dos 80% iniciais. | Fixar a configuração vencedora antes do walk-forward final. |
| Avaliação final | Walk-forward expansivo, reestimando cada modelo em cada origem válida. Registrar previsão, valor observado, erro absoluto e resíduos. | Mesmas origens e horizonte para todos os modelos de uma mesma base. |
| Métrica | MAE por base e por modelo. | Não calcular média de MAE entre bases de escalas diferentes. |

O percentual de teste vem das regras recebidas do grupo. O horizonte deverá ser registrado antes da criação da matriz de features e antes da avaliação final.

## Regras por base

| Base | Frequência confirmada | Alvo | Tratamento anterior à modelagem | Ponto pendente |
| --- | --- | --- | --- | --- |
| 1 | Diária; 70% / 30%; semente 42 | `Close` | Manter o calendário diário observado; criar lags e calendário apenas com dados anteriores à origem. | Horizonte final e disponibilidade das externas. |
| 2 | Horária; 80% / 20%; semente 67 | `traffic_volume` | Consolidar um alvo por timestamp porque os valores do alvo são idênticos no grupo. Para variáveis externas, documentar uma agregação determinística por tipo antes de gerar qualquer arquivo. | Horizonte final e catálogo das externas. |
| 3 | Horária; 80% / 20%; semente 42 | `PM2.5` | Manter a grade de horas; não imputar o alvo. Imputar externas somente dentro do treino, se aprovadas como disponíveis. | Horizonte final e catálogo das externas. |
| 4 | Horária pela média das leituras válidas; 80% / 20%; semente 42 | `T (degC)` | Preservar o bruto de 10 minutos; criar saída horária separada, sem preencher horas ausentes. | Horizonte final e catálogo das externas. |
| 5 | Semanal encerrada na sexta-feira; 75% / 25%; semente 42 | `GOLD_PRICE` | Último preço observado na semana; recriar calendário, lags e janelas. Não usar `TARGET` nem campos pré-calculados. | Horizonte final, unidade do ouro e catálogo das externas. |

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
4. Holt-Winters será univariado. SARIMAX, Random Forest e XGBoost só receberão variáveis externas que estejam no catálogo como temporalmente permitidas.

## Condições para a avaliação final

1. Registro explícito do horizonte final, comum ou por base.
2. Catálogo de disponibilidade das variáveis externas e regra de agregação da Base 2.
3. Criação da máscara comum de elegibilidade que será compartilhada pelos quatro modelos.

Com essas decisões, a configuração versionada por base será completada com o horizonte e a máscara comum, e a avaliação final poderá ser liberada.
