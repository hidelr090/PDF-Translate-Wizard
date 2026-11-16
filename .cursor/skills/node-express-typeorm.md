# Skill: Node.js + Express + TypeORM + PostgreSQL (API)

## Descrição
Desenvolver e manter o backend `homefinapp-api`: rotas Express, ORM TypeORM, banco PostgreSQL, validação Zod e autenticação JWT.

## Stack
- Express (servidor HTTP)
- TypeORM (mapeamento objeto-relacional)
- PostgreSQL (banco)
- Zod (validação de entrada)
- jsonwebtoken + bcryptjs (autenticação)
- helmet, cors, express-rate-limit, hpp (segurança)
- Swagger (documentação de API)

## Regras da skill
1. **Validação com Zod**: validar `body`, `query` e `params` antes do caso de uso.
2. **TypeORM entities**: definir entidades com decoradores; usar migrations para mudanças de esquema.
3. **Consultas seguras**: usar QueryBuilder/Repository do TypeORM (parametrizado) para evitar SQL injection.
4. **Tratamento de erros**: middleware centralizado de erros; diferenciar erro de negócio (4xx) de erro inesperado (500).
5. **Respostas padronizadas**: usar DTOs de resposta; nunca expor senha, token ou dados internos.
6. **Autenticação**: JWT com expiração; senhas hasheadas com bcrypt; middleware de autenticação em rotas protegidas.
7. **Documentação**: anotar endpoints com Swagger/OpenAPI ao criar ou alterar rotas.

## Comandos relevantes
- `npm run migration:generate` — gerar migration
- `npm run migration:run` — aplicar migrations
- `npm run migration:revert` — reverter última migration
- `npm run lint` — executar ESLint

## Quando aplicar
Qualquer trabalho em `homefinapp-api` (novos endpoints, entidades, migrations, middlewares).