# Skill: Git e Conventional Commits

## Descrição
Manter o histórico do repositório limpo, rastreável e automatizável usando Conventional Commits e branches nomeadas por padrão.

## Regras da skill
1. **Conventional Commits**: `<tipo>(<escopo>): <descrição>`
   - Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`, `revert`
   - Escopo sugerido: `api`, `web`, `backoffice`, `mobile`, `infra`, `docs`
   - Exemplo: `feat(api): adicionar endpoint de criar transação`
2. **Branches**: `tipo/descricao-resumida`
   - Exemplo: `feat/novo-endpoint-transacao`, `fix/correcao-login-mobile`
3. **Commits atômicos**: um commit = uma mudança lógica; não misturar refatoração com funcionalidade nova.
4. **Não commitar segredos**: `.env`, `node_modules`, `dist`, builds — manter no `.gitignore`.
5. **Mensagens em português**: descritivas e curtas.

## Quando aplicar
Todo commit e criação de branch no workspace homefin.