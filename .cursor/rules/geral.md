# Rule: Regras Gerais do Workspace Homefin

Aplica-se a todos os apps e colaboradores do monorepo.

## 1. Idioma e comunicação
- Código, comentários, nomes de variáveis, funções, classes e commits: **português** (ou inglês quando exigido por biblioteca/padrão externo).
- Mensagens de erro exibidas ao usuário: **português do Brasil**.

## 2. Versionamento e branches
- Seguir Conventional Commits: `feat(api): ...`, `fix(web): ...`, `docs: ...` etc.
- Nome de branch: `tipo/descricao-resumida` (ex: `feat/nova-transacao`, `fix/login-mobile`).
- Um pull request por funcionalidade/ correção; PR pequeno e focado.

## 3. Qualidade de código antes de commitar
- Rodar `npm run lint` no app alterado e corrigir avisos/erros.
- Rodar `tsc` / build do app para garantir que não há erro de compilação.
- Se houver teste relacionado, rodá-lo e garantir que passe.

## 4. Segredo e variáveis de ambiente
- Nunca commitar `.env`, arquivos com senhas, tokens ou chaves privadas.
- Manter `.env.example` atualizado com as variáveis obrigatórias.
- Segredos de produção ficam fora do repositório (CI/CD / secrets manager).

## 5. Pull Request
- Todo PR deve ter descrição do que muda, por que e como testar.
- PRs que tocam autenticação, banco de dados ou contratos de API precisam de revisão da persona de segurança/backend.
- Linkar issue ou contexto quando existir.

## 6. Documentação
- Alterar contrato de API → atualizar Swagger.
- Adicionar variável de ambiente → atualizar `.env.example` e docs de setup.
- Mudança de comportamento para o usuário → atualizar docs na pasta `docs/` do app correspondente.

## Quando aplicar
Sempre que trabalhar no workspace homefin, independentemente do app.