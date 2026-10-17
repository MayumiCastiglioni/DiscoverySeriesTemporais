# Handoff

## Estado atual

- **Data:** 17/10/2026
- **Fase:** Fase 1 - ingestão, congelamento e qualidade dos dados; exploração descritiva iniciada.
- **Situação:** em andamento. As cinco bases foram recebidas, a preparação estrutural foi executada e os alvos candidatos foram perfilados sem modelagem.
- **Repositório local:** criado a partir de `MayumiCastiglioni/DiscoverySeriesTemporais`, originalmente vazio.
- **Git:** esta continuação parte do commit `b0f05bf` no branch `main`. Para o commit atualmente publicado, consultar `git log --oneline -1`.
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

## Requisitos confirmados do enunciado

- Cinco bases congeladas com variável-alvo temporal e variáveis externas.
- SARIMAX, Holt-Winters univariado, Random Forest e um modelo de especialização.
- STL, engenharia de features temporalmente válida, ajuste prévio de hiperparâmetros e validação walk-forward.
- MAE como métrica principal por base, diagnóstico de resíduos e interpretação de features/modelos.
- Relatório em HTML paginado e PDF com o mesmo conteúdo, acompanhado dos materiais que tornam a análise reproduzível.

## Itens deliberadamente pendentes

1. Fonte original, unidade e permissão de redistribuição da Base 1; fonte, unidade e formação de `GOLD_PRICE` na Base 5.
2. Modelo de especialização do grupo.
3. Aprovação ou revisão das frequências, horizonte e recorte temporal propostos no protocolo rascunhado.
4. Regra de agregação das variáveis externas na Base 2 e confirmação da média horária na Base 4.
5. Catálogo definitivo de disponibilidade temporal, em especial taxas da Base 5 e medições meteorológicas/ambientais.
6. Material de divisão e registro de demandas, que a usuária informou que fornecerá separadamente.

## Próximo passo seguro

Após a aprovação das decisões pendentes, criar a configuração versionada por base e os checks de validação temporal. Só então gerar as saídas de modelagem, STL e gráficos. Não criar dados sintéticos, resultados ou modelos antes disso.

## Retomada rápida

1. Ler `AGENTS.md`, este arquivo e `docs/PLANO_INICIAL.md`.
2. Conferir o estado do Git e as decisões fornecidas pelo grupo.
3. Atualizar esta seção com os novos fatos e a próxima ação verificável ao final de cada sessão.
