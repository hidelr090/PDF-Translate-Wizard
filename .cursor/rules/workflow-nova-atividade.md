# Rule: Workflow de Nova Atividade de Desenvolvimento

Aplica-se a toda vez que iniciar uma nova atividade (issue, tarefa, bug, funcionalidade) em qualquer app do workspace homefin (`api`, `web`, `backoffice`, `mobile`).

## 1. Iniciar a atividade — criar uma nova branch

Antes de escrever qualquer código, crie uma branch dedicada à atividade:

```bash
# Atualize a branch principal
git checkout main
git pull origin main

# Crie a branch da atividade
git checkout -b tipo/descricao-resumida-da-atividade
```

**Padrão de nome da branch:** `<tipo>/<descricao-resumida>`  
Tipos sugeridos: `feat`, `fix`, `refactor`, `test`, `chore`, `docs`.

Exemplos válidos:
- `feat/nova-transacao`
- `fix/correcao-login-mobile`
- `refactor/validacao-zod-api`
- `docs/setup-mobile`

**Nunca faça commit direto na branch `main` ou `master`.**

## 2. Durante o desenvolvimento

- Faça commits atômicos seguindo [Conventional Commits](rules/git.md): `tipo(escopo): descricao`.
- Um escopo por atividade; não misture atividades distintas na mesma branch.
- Mantenha a branch atualizada com `main` se houver mudanças paralelas:
  ```bash
  git fetch origin
  git rebase origin/main
  ```

## 3. Antes de finalizar a atividade — validações obrigatórias

Antes de abrir o Pull Request ou fazer merge, rode (na ordem) todos os comandos abaixo na raiz do app alterado:

### A) Lint
```bash
# Exemplo para a API
cd homefinapp-api
npm run lint

# Exemplo para o Web
cd homefinapp-web
npm run lint
```
Corrija todos os erros e avisos reportados pelo ESLint.

### B) Testes unitários
```bash
# API (testes existentes na pasta tests/)
cd homefinapp-api
npm run test
# ou o comando de teste configurado no app

# Web / Mobile — rodar suíte de teste do app, quando existir
```

### C) Smoke test temporário
Crie (ou reutilize) um **smoke test temporário** que:
1. Execute o fluxo crítico da atividade (ex: criar uma transação, fazer login, renderizar a tela principal).
2. Valide que a funcionalidade entrega o esperado em ambiente de desenvolvimento/local.
3. **Apague todos os arquivos, registros de banco, uploads ou estado gerados por ele ao finalizar** (limpeza automática).

Exemplo de script temporário (Node):
```js
// smoke-test-temp.js — exemplo ilustrativo
import { criarTransacao } from './src/application/use-cases/criar-transacao.js';
import { limparBancoDeTeste } from './tests/helpers/limpar-banco.js';

try {
  const resultado = await criarTransacao({ ... });
  console.assert(resultado.id, 'Smoke test falhou: transação não criada');
  console.log('✅ Smoke test passou');
} finally {
  await limparBancoDeTeste(); // apaga arquivos/registros gerados
  // remover o próprio arquivo de smoke test, se for gerado dinamicamente
}
```

Após validar, **exclua o arquivo do smoke test temporário** (não commite-o):
```bash
rm smoke-test-temp.js
```

## 4. Finalizar a atividade

1. Certifique-se de que lint, testes unitários e smoke test passaram.
2. Faça o push da branch:
   ```bash
   git push origin tipo/descricao-resumida-da-atividade
   ```
3. Abra um Pull Request para `main` descrevendo:
   - O que foi feito
   - Como testar
   - Evidências de que lint, testes e smoke test passaram

## Checklist de conclusão

- [ ] Nova branch criada a partir de `main`
- [ ] Commits atômicos e seguindo Conventional Commits
- [ ] `npm run lint` executado e sem erros
- [ ] Testes unitários executados e aprovados
- [ ] Smoke test temporário executado e aprovado
- [ ] Arquivos/estado gerados pelo smoke test apagados
- [ ] Smoke test temporário removido (não commitado)
- [ ] Pull Request aberto para `main`

## Quando aplicar

Toda nova atividade de desenvolvimento no workspace homefin, independentemente do app ou da magnitude da mudança.