# Guia de Contribuição — PDF Translate Wizard

Obrigado por considerar contribuir com o PDF Translate Wizard! Este documento contém as diretrizes para contribuições.

## Código de conduta

Este projeto adota o [Contributor Covenant](https://www.contributor-covenant.org/) como seu código de conduta. Leia o [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) antes de contribuir.

## Como começar

1. Faça um fork do repositório
2. Clone seu fork localmente
3. Crie uma branch a partir de `main`
4. Faça suas alterações
5. Commit e push para seu fork
6. Abra um Pull Request contra o branch `main` deste repositório

## Convenções

### Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
tipo(escopo): descrição curta

Corpo opcional com mais detalhes.
```

Tipos aceitos: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.

Exemplos:
- `feat(pdf): adiciona extração de coordenadas de blocos de texto`
- `fix(ai): corrige timeout na requisição ao Ollama`
- `docs(readme): atualiza instruções de instalação`

### Código

- TypeScript com `strict: true`
- Evite `any`
- Siga as regras definidas em `.cursor/rules/` e skills em `.cursor/skills/`
- Escreva testes para funcionalidades críticas
- Não commite credenciais ou arquivos `.env`

### Pull Requests

- Descreva o que muda, por que e como testar
- Vincule issues relacionadas quando existirem
- Mantenha o PR pequeno e focado em uma única funcionalidade
- Certifique-se de que `npm run lint` e `npm test` passam

## Estrutura do projeto

Consulte o [README.md](README.md) para uma visão geral da arquitetura e estrutura de diretórios.

## Relatório de bugs

Use o template de [bug report](.github/ISSUE_TEMPLATE/bug_report.md) ao abrir uma issue de bug.

## Solicitação de funcionalidades

Use o template de [feature request](.github/ISSUE_TEMPLATE/feature_request.md) ao sugerir novas funcionalidades.