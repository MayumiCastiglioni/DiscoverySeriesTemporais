# Tratamento, ACF e STL por base

## Estrutura executada

Cada Base possui um notebook em `notebooks/bases`. Ele gera `data/processed/base<N>_cleaned.csv`, mostra a série limpa, ACF e STL e salva as figuras em `reports/generated/exploration/base<N>`. Os CSVs `cleaned` são derivados, ignorados pelo Git e nunca substituem os brutos congelados.

| Base | Tratamento que gera o CSV `cleaned` | STL | ACF |
| --- | --- | ---: | ---: |
| 1 | Mantém OHLCV diário, renomeia `Close` para `target` e exclui `Adj Close`, pois duplica o alvo. | 7 dias | 60 defasagens |
| 2 | Consolida timestamps repetidos: média para externas numéricas e moda determinística para externas categóricas, após verificar que `traffic_volume` não diverge. | 24 horas | 336 defasagens |
| 3 | Mantém alvo e externas horárias observadas; exclui identificador, componentes redundantes do timestamp e a estação constante. | 24 horas | 336 defasagens |
| 4 | Agrega leituras de 10 minutos para hora pela média; transforma direção do vento em seno e cosseno antes da agregação. | 24 horas | 336 defasagens |
| 5 | Agrega em semanas encerradas na sexta-feira pelo último valor observado de ouro; mantém somente taxas externas não pré-calculadas. | 52 semanas | 104 defasagens |

Para não criar informação artificial, a ACF e a STL usam o maior trecho regular com alvo observado. Quando esse trecho não comporta dois ciclos sazonais, como na Base 5, é criada uma **cópia exclusivamente diagnóstica** com interpolação temporal das lacunas internas. A saída `base5_cleaned.csv`, os notebooks de modelos e a avaliação walk-forward preservam as lacunas: essa interpolação nunca é usada como dado de treino, feature, alvo ou MAE.

## Uso dos gráficos

ACF e STL são diagnósticos exploratórios. Eles ajudam a descrever dependência temporal e sazonalidade, mas não escolhem sozinhos o horizonte de previsão nem autorizam uma variável futura como feature. A seleção do horizonte continua documentada no protocolo e deverá ocorrer antes do MAE final.
