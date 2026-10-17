# Regras e checks de qualidade

Estas regras transformam os requisitos acadêmicos em verificações repetíveis. Aplicar o bloco pertinente antes de fechar cada fase.

## Regras inegociáveis

1. **Sem vazamento temporal.** Nenhuma feature, transformação, escalonamento, imputação, seleção ou ajuste pode usar observações posteriores à origem da previsão.
2. **Bases congeladas.** A análise usa exatamente a versão documentada de cada base. Atualizações criam uma nova versão e exigem nova decisão de escopo.
3. **Comparação justa.** Os quatro modelos de uma base usam o mesmo horizonte, as mesmas origens de previsão e o mesmo teste final. Holt-Winters permanece univariado.
4. **Teste final intocado.** A otimização ocorre antes da avaliação final; hiperparâmetros são fixados para o walk-forward final.
5. **MAE por base.** É proibido somar ou tirar média de MAEs de bases em escalas diferentes. Comparar posição, vitórias e resultados dentro de cada base.
6. **Rastreabilidade.** Toda tabela, gráfico, previsão e conclusão deve apontar para uma execução identificável, dados de origem e configuração.
7. **Sem conclusões sem evidência.** Interpretações devem registrar métrica, gráfico, teste ou método que as sustente.
8. **Modelo de especialização.** XGBoost é o quarto modelo obrigatório e só pode usar features temporalmente permitidas na origem.
9. **Origens compartilhadas.** Para uma base, SARIMAX, Holt-Winters, Random Forest e XGBoost devem receber a mesma agenda canônica de origens, na mesma ordem. Uma diferença invalida a comparação até ser corrigida.
10. **Notebooks reexecutáveis.** Todo notebook versionado deve executar a partir de um kernel limpo, chamar código reutilizável em `src` e deixar claro se seus artefatos são exploratórios ou finais.

## Check de entrada de dados

- [ ] Fonte, licença ou referência, versão/data de obtenção, período, frequência e unidade estão documentados.
- [ ] A variável-alvo é numérica e possui chave temporal sem duplicidades.
- [ ] Ausências, lacunas, irregularidades, duplicidades e outliers foram medidos e tratados ou justificados.
- [ ] Pelo menos duas variáveis externas foram catalogadas, quando previsto no enunciado.
- [ ] Cada variável externa foi classificada como conhecida antecipadamente, previsão disponível na origem, somente observada no futuro ou excluída.
- [ ] A versão bruta foi preservada sem alterações.

## Check de análise e features

- [ ] A STL utiliza período sazonal coerente com a frequência.
- [ ] Tendência, sazonalidade, resíduos e força sazonal foram interpretados por base.
- [ ] Lags e janelas foram calculados sem acessar valores futuros.
- [ ] Features de calendário usam apenas informação disponível na origem.
- [ ] Linhas perdidas por lags/janelas foram contabilizadas e justificadas.
- [ ] O mesmo conjunto de features é usado por Random Forest e modelo de especialização quando compatível.

## Check de validação e modelagem

- [ ] A divisão respeita a ordem temporal e separa um teste final.
- [ ] O walk-forward parte apenas do histórico disponível e atualiza o histórico entre origens.
- [ ] Todos os modelos usam as mesmas origens e o mesmo horizonte na mesma base.
- [ ] A checagem automatizada confirmou a igualdade da agenda de origens antes do cálculo de MAE.
- [ ] XGBoost foi ajustado apenas com dados anteriores à origem e sua busca usou somente o período de treino.
- [ ] Hiperparâmetros foram escolhidos sem consultar o teste final e o processo foi registrado.
- [ ] SARIMAX considera ordens e sazonalidade; Holt-Winters considera componentes e período; Random Forest registra sua busca; o modelo de especialização documenta a busca apropriada.
- [ ] Sementes, versões de bibliotecas, duração, parâmetros e identificador da execução foram registrados.

## Checks já executados nesta etapa

- [x] `configs/base_experiment_rules.json` contém exatamente as cinco bases, frações que somam 100% e sementes definidas.
- [x] As agendas provisórias usam os cortes 70/30, 80/20, 80/20, 80/20 e 75/25 e rejeitam lacunas de calendário incompatíveis com o horizonte-piloto.
- [x] O teste automatizado rejeita uma agenda de um modelo que tenha uma origem removida ou reordenada.
- [x] SARIMAX, Holt-Winters, Random Forest e XGBoost executaram um piloto na mesma `origin_id` por base.
- [x] Os pilotos foram identificados como não finais; não há MAE, ranking ou escolha de vencedor registrada.

Para repetir os checks automatizados a partir da raiz, use `python scripts/run_checks.py`.

## Check de resultados e interpretação

- [ ] Previsões fora da amostra e resíduos foram preservados por base e modelo.
- [ ] MAE foi calculado sobre as previsões walk-forward fora da amostra.
- [ ] Há ranking de MAE e vencedor dentro de cada base, além de vitórias e posição média por modelo.
- [ ] Resíduos foram avaliados com gráfico temporal, ACF, Ljung-Box e interpretação do p-valor.
- [ ] SARIMAX interpreta coeficientes externos; Holt-Winters interpreta nível, tendência e sazonalidade; Random Forest e o modelo de especialização usam método de importância compatível.
- [ ] Limitações, incertezas e possíveis padrões residuais foram explicitados.

## Check de entrega

- [ ] O HTML paginado e o PDF possuem o mesmo conteúdo e foram inspecionados visualmente.
- [ ] O relatório inclui narrativa, fontes, decisões metodológicas, resultados, limitações e referências.
- [ ] O projeto pode ser reexecutado do zero a partir dos materiais entregues.
- [ ] O pacote contém código organizado, bases ou fontes claras, resultados consolidados de MAE, relatórios e arquivos-fonte exigidos.
- [ ] O material de divisão de demandas foi anexado somente se entregue e aprovado pelo grupo.
