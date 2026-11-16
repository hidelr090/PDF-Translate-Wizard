# Rule: Regras do Backend API (homefinapp-api)

Aplica-se ao `homefinapp-api` (Node.js/Express + TypeScript + TypeORM + PostgreSQL).

## Camadas (Clean Architecture)
- `src/domain`: entidades e regras de negócio pura. **Não importa nada de infra/controllers.**
- `src/application`: casos de uso e DTOs.
- `src/infra`: repositórios (TypeORM/Prisma) e provedores externos.
- `src/controllers`: finos — apenas traduzem HTTP para caso de uso.
- `src/routes`: definição de rotas e middlewares.

## Entrada e validação
- Todo endpoint que recebe dados deve validar com **Zod** antes do caso de uso.
- Respostas nunca expõem senha, token ou dados internos (usar DTOs de resposta).

## Banco de dados
- Mudanças de esquema só via **migration TypeORM** (`migration:generate`, `migration:run`).
- Consultas parametrizadas (QueryBuilder/Repository) — nunca concatenar strings em SQL.

## Segurança na API
- Senhas hasheadas com **bcryptjs**.
- JWT com expiração; segredo em variável de ambiente.
- Middleware de autenticação em rotas protegidas.
- helmet, cors, express-rate-limit, hpp ativos.

## Documentação
- Endpoint novo ou alterado → documentar no **Swagger/OpenAPI**.

## Quando aplicar
Qualquer trabalho no `homefinapp-api`.