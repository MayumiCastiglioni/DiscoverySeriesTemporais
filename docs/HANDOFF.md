# Handoff

## Estado atual

- **Data:** 17/10/2026
- **Fase:** Fase 1 - ingestão, congelamento, regras por base e pilotos de infraestrutura concluídos; features e avaliação final pendentes.
- **Situação:** em andamento. As cinco bases foram recebidas, a preparação estrutural, as regras específicas e os notebooks 01–05 foram executados. Ainda não há avaliação final nem modelo comparado por MAE.
- **Repositório local:** criado a partir de `MayumiCastiglioni/DiscoverySeriesTemporais`, originalmente vazio.
- **Git:** o último estado publicado antes desta continuação foi `ce3c9c4` no branch `main`. Para o commit atualmente publicado, consultar `git log --oneline -1`.
- **Descrição do repositório:** atualizada para refletir a comparação reprodutível de modelos com validação walk-forward.

## O que foi preparado

- `AGENTS.md` com o contrato de trabalho contínuo, limites de escopo, método, regras de reprodutibilidade e procedimento de retomada.
- `docs/PLANO_INICIAL.md` com objetivo, escopo, decisões pendentes, fases e critérios de avanço.
- `docs/RULES_E_CHECKS.md` com regras contra vazamento temporal e checklists de dados, features, validação, resultados e entrega.
- `README.md` com uma apresentação concisa do repositório e links para a documentação inicial.
- Cópias locais congeladas em `data/raw`, identificadas por checksum em `docs/DECISOES_DE_DADOS.md`.
- Dicionário preliminar, auditoria inicial e rotina reproduzível de preparação estrutural.
- Registro de fontes e proveniência: Bases 2, 3 e 4 confirmadas; Base 1 identificada apenas de forma provável; Base 5 confirmada apenas para as duas séries de taxa.
- Perfil numérico reproduzível em `scripts/profile_candidate_series.py` e `docs/EXPLORACAO_INICIAL.md`.
- Protocolo de avaliação proposto, ainda não aprovado, em `docs/PROTOCOLO_EXPERIMENTAL_RASCUNHO.md`.
- XGBoost definido como modelo de especialização, com documentação e piloto de uma origem por base em `docs/MODELO_XGBOOST.md` e `notebooks/02_origens_e_xgboost_piloto.ipynb`.
- Agenda de origens compartilhadas implementada em `src/discovery_series_temporais/series.py`, testada contra divergências e explicada em `docs/WALK_FORWARD_IMPLEMENTADO.md`.
- Configuração por base em `configs/base_experiment_rules.json`: granularidade, corte temporal e semente foram fornecidos pelo grupo e são lidos pelos adaptadores.
- Transformações confirmadas: Base 4 por média horária válida; Base 5 por último preço semanal em sexta-feira; Base 2 consolida o alvo depois de comprovar que as repetições não divergem.
- Adaptadores-piloto de SARIMAX, Holt-Winters, Random Forest e XGBoost em `src/discovery_series_temporais/model_pilots.py`. Os quatro foram executados em uma origem comum por base; o artefato ignorado pelo Git é `reports/generated/model_pilots/shared_origin_model_pilots.csv`.
- `notebooks/01_auditoria_e_stl_preliminar.ipynb` a `05_avaliacao_walk_forward_final.ipynb` executados em kernel limpo, sem erro. A STL foi feita somente na Base 1; todos os modelos permanecem pilotos, não resultados finais.

## Requisitos confirmados do enunciado

- Cinco bases congeladas com variável-alvo temporal e variáveis externas.
- SARIMAX, Holt-Winters univariado, Random Forest e um modelo de especialização.
- STL, engenharia de features temporalmente válida, ajuste prévio de hiperparâmetros e validação walk-forward.
- MAE como métrica principal por base, diagnóstico de resíduos e interpretação de features/modelos.
- Relatório em HTML paginado e PDF com o mesmo conteúdo, acompanhado dos materiais que tornam a análise reproduzível.

## Itens deliberadamente pendentes

1. Horizonte final de previsão, comum ou por base. Até receber essa decisão, `h = 1` é apenas piloto e não deve gerar MAE ou ranking.
2. Catálogo definitivo de disponibilidade temporal das variáveis externas, incluindo a agregação por tipo na Base 2.
3. Unidade de `GOLD_PRICE` e licenças/permissões de redistribuição das Bases 1, 4 e 5.
4. Material de divisão e registro de demandas, que a usuária informou que fornecerá separadamente.

## Próximo passo seguro

Após receber o horizonte e o catálogo de externas, criar a matriz de features, reconstruir a agenda pela interseção de linhas elegíveis e executar a busca temporal interna. Só então executar o walk-forward final, gerar MAE, ranking, resíduos e interpretação comparativa.

## Retomada rápida

1. Ler `AGENTS.md`, este arquivo e `docs/PLANO_INICIAL.md`.
2. Conferir o estado do Git e as decisões fornecidas pelo grupo.
3. Atualizar esta seção com os novos fatos e a próxima ação verificável ao final de cada sessão.
