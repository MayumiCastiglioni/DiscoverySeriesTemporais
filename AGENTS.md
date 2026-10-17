# AGENTS.md

## Propósito do repositório

Este repositório reúne uma análise comparativa, reproduzível e tecnicamente interpretável de séries temporais com variáveis externas. O escopo acadêmico inclui cinco bases congeladas, SARIMAX, Holt-Winters, Random Forest e um modelo de especialização ainda a ser informado pelo grupo.

O planejamento aprovado é a fonte operacional de escopo. Antes de implementar uma etapa, consulte `docs/PLANO_INICIAL.md`; para critérios de qualidade, consulte `docs/RULES_E_CHECKS.md`.

## Limites de escopo

- Não definir, presumir ou redistribuir integrantes, responsabilidades ou o modelo de especialização. Essas informações serão fornecidas separadamente.
- Não inventar bases, fontes, frequência, horizonte, datas de origem ou regras de disponibilidade de variáveis externas. Registrar o que estiver pendente e solicitar a informação necessária.
- Não incluir valores futuros observados em features, transformações, normalizações, ajuste de hiperparâmetros ou qualquer decisão tomada na data de origem da previsão.
- Não admitir vazamento temporal em nenhuma fase da análise; em caso de dúvida sobre a disponibilidade de uma variável, excluí-la até que a regra esteja documentada.
- Tratar Holt-Winters como referência univariada; os demais modelos só podem usar variáveis externas cuja disponibilidade temporal esteja documentada.

## Organização esperada

Criar diretórios de código, dados, resultados e relatório somente quando a fase correspondente for aprovada. Quando criados, usar nomes previsíveis e separar claramente:

- entradas brutas congeladas;
- dados processados e features;
- código reutilizável;
- configurações de experimento;
- resultados rastreáveis por base, modelo e execução;
- fontes do relatório e entregáveis finais.

Dados brutos congelados nunca devem ser alterados. Transformações devem gerar novos arquivos e manter a origem rastreável.

## Método obrigatório

1. Documentar cada base antes da modelagem: fonte, período, frequência, unidade, alvo, variáveis externas e disponibilidade no momento da previsão.
2. Validar a integridade temporal antes de analisar: frequência, duplicidades, ausências, lacunas e outliers.
3. Fazer STL e a interpretação de tendência, sazonalidade, resíduos e força sazonal por base.
4. Construir features temporalmente válidas e remover apenas as linhas inevitavelmente incompletas, documentando a decisão.
5. Definir uma mesma divisão temporal, horizonte, datas de origem e protocolo walk-forward para todos os modelos de uma base.
6. Escolher hiperparâmetros sem consultar o teste final. Fixá-los antes da avaliação walk-forward final.
7. Registrar parâmetros, ambiente, sementes, duração, previsões e resíduos de toda execução.
8. Comparar modelos por MAE dentro de cada base; não agregar MAE entre bases de escalas diferentes.
9. Avaliar resíduos fora da amostra, incluindo gráfico temporal, ACF e Ljung-Box, e interpretar as limitações.
10. Produzir interpretação compatível para cada modelo e destacar o papel e a disponibilidade das variáveis externas.

## Qualidade e reprodutibilidade

- Toda mudança deve preservar ou atualizar a documentação afetada.
- Toda rotina deve poder ser executada do zero a partir das entradas versionadas ou das fontes explicitamente registradas.
- Fixar versões de dependências e sementes aleatórias quando aplicável.
- Evitar estado escondido em notebooks; mover lógica repetida para código reutilizável e manter notebooks orientados à narrativa e à inspeção.
- Nunca substituir resultados antigos sem preservar o identificador da execução ou uma justificativa documentada.
- Executar os checks pertinentes de `docs/RULES_E_CHECKS.md` antes de considerar uma etapa concluída.

## Entregas e comunicação

O relatório final deverá manter o mesmo conteúdo em HTML paginado e PDF, com narrativa interpretativa. Códigos, fontes das bases, resultados consolidados, previsões, resíduos e referências devem permitir auditoria.

O registro de divisão diária de demandas está fora do escopo deste repositório nesta etapa, por solicitação explícita da usuária. Se ele for integrado posteriormente, não alterar seu conteúdo sem instrução expressa.

## Retomada do trabalho

No início de uma nova sessão, ler `AGENTS.md`, `docs/HANDOFF.md`, o plano aprovado e o estado do Git. Ao encerrar, atualizar `docs/HANDOFF.md` com o que foi feito, os resultados validados, riscos, decisões pendentes e o próximo passo seguro.
