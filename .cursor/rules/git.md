# Rule: Regras de Git e Commits

1. **Conventional Commits**: `tipo(escopo): descrição`
   - Tipos: feat, fix, docs, style, refactor, test, chore, perf, ci, build, revert
   - Escopos sugeridos: api, web, backoffice, mobile, infra, docs
   - Exemplo: `feat(api): endpoint criar transação`
2. **Branches**: `tipo/descricao-resumida`
   - Exemplo: `feat/novo-endpoint-transacao`, `fix/correcao-login`
3. **Commits atômicos**: uma mudança lógica por commit; não misturar refatoração com funcionalidade.
4. **Não commitar segredos**: `.env`, `node_modules`, `dist`, builds.
5. **Mensagens em português**, descritivas e curtas.

## Quando aplicar
Todo commit e criação de branch no workspace homefin.