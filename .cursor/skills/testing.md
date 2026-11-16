# Skill: Testes Automatizados

## Descrição
Escrever testes que deem confiança para entregar alterações com regressão controlada nos apps do workspace.

## Regras da skill
1. **API (`homefinapp-api`)**: testes de integração nos endpoints críticos (autenticação, transações, categorias, orçamentos, pagamentos) usando a pasta `tests/`.
2. **Contratos**: validar que a resposta da API respeita os schemas Zod/Swagger.
3. **Fluxos críticos**: login → cadastro → transação → dashboard → relatório.
4. **Casos de borda**: dados inválidos, campos obrigatórios ausentes, valores negativos, erro de rede.
5. **Frontend/Mobile**: teste de renderização de componentes principais e fluxos de usuário quando houver ferramenta de teste configurada.
6. **Nomes de teste descritivos**: `deve retornar 400 quando descrição for vazia`, `deve autenticar usuário com credenciais válidas`.
7. **Rodar testes antes de abrir PR** e no pipeline de CI.

## Quando aplicar
Qualquer nova funcionalidade, correção de bug ou alteração de endpoint no `homefinapp-api` (e frontend/mobile quando aplicável).