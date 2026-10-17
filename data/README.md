# Dados

## Organização adotada

- `raw/`: cópias locais e imutáveis dos cinco arquivos recebidos. Não editar, renomear ou sobrescrever esses arquivos.
- `processed/`: saídas geradas por rotinas de preparação estrutural. Nunca editar manualmente.
- `features/`: matrizes de modelagem criadas somente após definir o horizonte e validar a disponibilidade temporal de cada variável.

As cópias em `raw/` foram verificadas por checksum e seus identificadores estão em `docs/DECISOES_DE_DADOS.md`. Elas permanecem fora do Git por enquanto, pois as fontes e os termos de redistribuição ainda não foram documentados. Isso evita publicar dados sem confirmar a permissão adequada. O relatório final incluirá as bases ou as fontes, conforme o requisito acadêmico e a decisão de distribuição registrada.

Para regenerar a preparação estrutural, executar `python scripts/prepare_structural_data.py`. A rotina lê apenas `raw/` e grava apenas em `processed/`.
