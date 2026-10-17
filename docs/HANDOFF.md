# Handoff

## Estado atual

- **Data:** 17/10/2026
- **Fase:** Fase 1 - ingestão, congelamento e qualidade dos dados.
- **Situação:** em andamento. As cinco bases foram recebidas e a preparação estrutural inicial foi executada.
- **Repositório local:** criado a partir de `MayumiCastiglioni/DiscoverySeriesTemporais`, originalmente vazio.
- **Git:** estrutura inicial publicada no branch `main` no commit `450284f`.
- **Descrição do repositório:** atualizada para refletir a comparação reprodutível de modelos com validação walk-forward.

## O que foi preparado

- `AGENTS.md` com o contrato de trabalho contínuo, limites de escopo, método, regras de reprodutibilidade e procedimento de retomada.
- `docs/PLANO_INICIAL.md` com objetivo, escopo, decisões pendentes, fases e critérios de avanço.
- `docs/RULES_E_CHECKS.md` com regras contra vazamento temporal e checklists de dados, features, validação, resultados e entrega.
- `README.md` com uma apresentação concisa do repositório e links para a documentação inicial.
- Cópias locais congeladas em `data/raw`, identificadas por checksum em `docs/DECISOES_DE_DADOS.md`.
- Dicionário preliminar, auditoria inicial e rotina reproduzível de preparação estrutural.

## Requisitos confirmados do enunciado

- Cinco bases congeladas com variável-alvo temporal e variáveis externas.
- SARIMAX, Holt-Winters univariado, Random Forest e um modelo de especialização.
- STL, engenharia de features temporalmente válida, ajuste prévio de hiperparâmetros e validação walk-forward.
- MAE como métrica principal por base, diagnóstico de resíduos e interpretação de features/modelos.
- Relatório em HTML paginado e PDF com o mesmo conteúdo, acompanhado dos materiais que tornam a análise reproduzível.

## Itens deliberadamente pendentes

1. Fontes, unidades e permissão de redistribuição das cinco bases.
2. Modelo de especialização do grupo.
3. Horizonte, datas de origem e período de teste de cada base.
4. Catálogo de disponibilidade temporal das variáveis externas.
5. Regra de agregação da base 2, política de ausências da base 3 e regularização da base 4.
6. Material de divisão e registro de demandas, que a usuária informou que fornecerá separadamente.

## Próximo passo seguro

Registrar as decisões pendentes em uma ficha de experimento por base e, então, avançar para a exploração, STL e definição do protocolo walk-forward. Não criar dados sintéticos, resultados ou modelos antes disso.

## Retomada rápida

1. Ler `AGENTS.md`, este arquivo e `docs/PLANO_INICIAL.md`.
2. Conferir o estado do Git e as decisões fornecidas pelo grupo.
3. Atualizar esta seção com os novos fatos e a próxima ação verificável ao final de cada sessão.
