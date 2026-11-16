# Skill: Docker e Containers

## Descrição
Criar e manter imagens Docker seguras e reproducíveis para os apps do workspace, especialmente `homefinapp-api`.

## Regras da skill
1. **Multi-stage build**: separar build de dependências da imagem final para reduzir tamanho.
2. **Usuário não-root**: rodar container como usuário não-root quando possível.
3. **Variáveis de ambiente**: injetar em runtime; não bakear segredos na imagem.
4. **Dockerfile no `.dockerignore`**: excluir `node_modules`, `dist`, `.env`, `.git`.
5. **Health check**: incluir `HEALTHCHECK` quando o app expor HTTP.
6. **Porta configurável**: usar variável de ambiente `PORT` em vez de hard-coded.

## Quando aplicar
Criar ou editar `Dockerfile`, `docker-compose.yml` ou arquivos de build de container.