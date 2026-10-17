# Planejamento inicial

## Status

**Fase 1 em andamento; regras por grupo, infraestrutura temporal e pilotos dos quatro modelos concluídos.** As cinco bases foram recebidas, congeladas localmente e auditadas. Granularidade, divisão treino/teste e sementes foram registradas em configuração versionada. XGBoost é o modelo de especialização; SARIMAX, Holt-Winters, Random Forest e XGBoost executaram um piloto na mesma origem por base. O horizonte final e o catálogo de disponibilidade das variáveis externas permanecem pendentes.

## Objetivo

Construir uma análise reprodutível que compare, em cinco séries temporais com variáveis externas, os modelos SARIMAX, Holt-Winters, Random Forest e XGBoost. A avaliação final será feita por MAE em previsões fora da amostra geradas por validação walk-forward.

## Escopo considerado

- Documentação, exploração e congelamento das cinco bases.
- Decomposição STL e interpretação de tendência, sazonalidade, resíduos e força sazonal.
- Feature engineering sem vazamento temporal.
- Otimização prévia e comparação justa de SARIMAX, Holt-Winters, Random Forest e XGBoost em cada base.
- Diagnóstico dos resíduos e interpretação de variáveis e modelos.
- Relatório técnico em HTML paginado e PDF com o mesmo conteúdo, além dos arquivos necessários para reprodução.

Por pedido explícito, este plano **não** divide demandas entre integrantes nem cria o registro diário de tarefas. Esse material poderá ser incorporado quando for entregue pelo grupo.

## Decisões necessárias antes de codificar

1. Qual é o horizonte final de previsão, comum ou específico por base?
2. Quais variáveis externas são conhecidas antecipadamente, previstas na origem ou indisponíveis no futuro?
3. As licenças das fontes permitem incluir os arquivos brutos na entrega? Caso contrário, a entrega usará referências e instruções de obtenção.
4. Qual é a unidade de `GOLD_PRICE`? A coluna pré-calculada `TARGET` permanecerá excluída.

Enquanto essas decisões não forem registradas, o trabalho se limita a preparar a estrutura, sem simular dados ou resultados.

## Andamento registrado

- A estrutura `data/raw`, `data/processed` e `data/features` foi adotada e documentada.
- As cinco entradas foram copiadas e verificadas por SHA-256, sem alteração dos arquivos recebidos.
- O dicionário preliminar e a auditoria inicial estão em `docs/DICIONARIO_DE_VARIAVEIS.md` e `docs/AUDITORIA_INICIAL_DAS_BASES.md`.
- A preparação estrutural foi executada por `scripts/prepare_structural_data.py` e validada nas cinco saídas; ela não executa imputação, feature engineering, modelagem nem cálculo de resultados.
- A exploração numérica dos alvos candidatos está registrada em `docs/EXPLORACAO_INICIAL.md` e pode ser reproduzida por `scripts/profile_candidate_series.py`.
- A confirmação das fontes está registrada em `docs/FONTES_E_PROVENIENCIA.md`; as pendências das Bases 1 e 5 continuam abertas.
- `configs/base_experiment_rules.json` e `docs/REGRAS_POR_BASE.md` registram frequências, cortes e sementes fornecidos pelo grupo.
- `docs/PROTOCOLO_EXPERIMENTAL_RASCUNHO.md` registra o protocolo já confirmado e a única decisão metodológica ainda necessária: o horizonte final.
- O modelo de especialização é XGBoost e está documentado em `docs/MODELO_XGBOOST.md`.
- A geração e checagem de origens walk-forward estão implementadas e explicadas em `docs/WALK_FORWARD_IMPLEMENTADO.md`; as agendas atuais são exploratórias, baseadas apenas no alvo.
- Os notebooks `03_regras_e_preparacao_por_grupo.ipynb`, `04_pilotos_dos_quatro_modelos.ipynb` e `05_avaliacao_walk_forward_final.ipynb` foram criados para checar regras, exercitar os quatro adaptadores e impedir uma avaliação final prematura.

## Fases propostas

### 0. Contrato do experimento

Registrar as cinco bases, o modelo de especialização, a unidade temporal, o horizonte, a regra de corte e o catálogo de disponibilidade das variáveis externas. Converter as decisões em uma configuração versionada por base. Granularidade, cortes e sementes já foram concluídos; falta o horizonte e o catálogo das externas.

**Saída:** ficha de cada base e protocolo de avaliação aprovado.

### 1. Ingestão, congelamento e qualidade dos dados

Armazenar ou referenciar de forma imutável as versões das bases. Verificar chaves temporais, frequência, cobertura, duplicidades, ausências, lacunas e outliers. Documentar qualquer regularização, imputação ou transformação.

**Saída:** inventário de dados, dicionário de variáveis, relatório de qualidade e conjuntos processados rastreáveis.

### 2. Exploração e decomposição

Produzir gráficos da variável-alvo e das variáveis externas principais. Aplicar STL adequando o período sazonal à frequência; calcular a força sazonal e interpretar os componentes.

**Saída:** diagnóstico exploratório e artefatos para a seção de STL do relatório.

### 3. Features e infraestrutura temporal

Implementar lags, janelas móveis, calendário, codificação cíclica e variáveis externas temporalmente permitidas. Criar um único mecanismo de validação walk-forward que gere as mesmas origens, horizonte e conjunto de teste para os modelos comparados.

**Saída:** matriz de features auditável e protocolo walk-forward testado contra vazamento.

### 4. Ajuste e treinamento dos modelos

Ajustar SARIMAX, Holt-Winters, Random Forest e XGBoost. Pesquisar e executar a otimização de hiperparâmetros usando apenas dados anteriores ao teste final. Fixar as configurações vencedoras antes da avaliação final.

**Saída:** configurações finais, registro do espaço de busca, justificativas e artefatos de treinamento.

### 5. Avaliação comparativa e interpretação

Executar o walk-forward final, registrar previsões e resíduos, calcular MAE por base e ordenar os modelos. Consolidar vitórias e posição média sem calcular média de MAE entre escalas distintas. Analisar resíduos com série temporal, ACF e Ljung-Box; calcular ou aplicar o método de interpretação adequado a cada modelo.

**Saída:** tabelas, gráficos e conclusões comparativas rastreáveis.

### 6. Relatório e empacotamento

Escrever uma narrativa técnica que explique decisões e resultados, em vez de apenas listar código. Gerar HTML paginado e PDF com o mesmo conteúdo. Reexecutar os checks, verificar referências e preparar o pacote final com código, fontes de dados, resultados, relatório e material exigido.

**Saída:** entregáveis finais consistentes e reproduzíveis.

## Critérios de aprovação para avançar

- O escopo e as cinco bases foram confirmados.
- O modelo de especialização, granularidade, corte temporal e sementes foram registrados; o horizonte final precisa ser informado.
- O protocolo temporal impede vazamento e é comum aos modelos comparados.
- Cada fase atende aos checks documentados antes de abrir a seguinte.
- A análise de demandas permanece fora deste plano até a entrega separada do grupo.
