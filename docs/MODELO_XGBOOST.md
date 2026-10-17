# Modelo de especialização: XGBoost

## Papel no projeto

O modelo de especialização definido pelo grupo é o **XGBoost**, implementado como regressão com `XGBRegressor`. Ele será comparado com SARIMAX, Holt-Winters e Random Forest em cada base, pela mesma métrica MAE e pelas mesmas origens walk-forward.

XGBoost constrói um conjunto sequencial de árvores de decisão. Cada nova árvore procura reduzir o erro deixado pelo conjunto anterior. Isso permite representar relações não lineares e interações entre lags, calendário e variáveis externas que sejam realmente disponíveis na origem da previsão. A API oficial documenta `XGBRegressor`, o objetivo de regressão `reg:squarederror` e o controle explícito de parâmetros. [Documentação oficial do XGBoost](https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.XGBRegressor).

## Como será aplicado de forma temporalmente válida

1. A linha de features de uma origem `t` conterá apenas valores observados até `t`, como o alvo corrente e seus lags, além de calendário e variáveis externas cuja disponibilidade tenha sido documentada.
2. O rótulo será o alvo de `t + 1`; portanto, ele nunca entra nas features daquela mesma linha.
3. Não haverá embaralhamento aleatório nem validação cruzada convencional. A busca de hiperparâmetros usará somente walk-forward dentro do treino.
4. A agenda canônica de origens será idêntica para os quatro modelos. XGBoost não poderá excluir origens extras por usar uma feature diferente.
5. A semente, versões, hiperparâmetros, colunas de entrada e importância de features serão gravados para cada execução final.

## Piloto já preparado

`src/discovery_series_temporais/xgboost_model.py` cria um desenho supervisionado de uma etapa à frente usando somente `target_lag_0`, `target_lag_1`, `target_lag_2` e `target_lag_7`. O notebook de execução faz um ajuste único anterior à primeira origem de teste para verificar o ambiente e a integração com a agenda.

Os parâmetros desse piloto (`n_estimators=50`, profundidade 3, `learning_rate=0,05` e semente 42) **não são hiperparâmetros finais**. Ele não produz MAE final, ranking nem conclusão sobre desempenho. A escolha final será feita apenas pela busca temporal interna, depois da aprovação das features e do horizonte.

## Interpretação planejada

Na avaliação final, a interpretação do XGBoost usará importância de variáveis acompanhada de uma leitura temporal: uma feature só será discutida se estiver permitida na origem e se sua importância vier da execução registrada. Importância não será interpretada como causalidade.
