# Skill: Clean Architecture / DDD Leve (API)

## Descrição
Organizar o `homefinapp-api` em camadas com separação de preocupações, onde o domínio não depende de infraestrutura nem de frameworks.

## Camadas do workspace
| Camada | Pasta | Responsabilidade |
|--------|-------|------------------|
| Domain | `src/domain` | Entidades, value objects, regras de negócio pura (sem dependências externas) |
| Application | `src/application` | Casos de uso, orquestração, DTOs de entrada/saída |
| Infra | `src/infra` | Repositórios (TypeORM/Prisma), provedores externos (email, AWS SES) |
| Controllers | `src/controllers` | Entrada HTTP: receber request, chamar caso de uso, devolver response |
| Routes | `src/routes` | Definição de rotas Express e middlewares |
| Shared | `src/shared` | Utilitários, exceções, constantes compartilhadas |

## Regras da skill
1. **Domínio puro**: `src/domain` não importa nada de `src/infra`, `src/controllers` ou bibliotecas externas (exceto utilitários puros).
2. **Casos de uso em `application`**: regra de negócio que não cabe na entidade fica aqui.
3. **Repositórios em `infra`**: acesso a banco de dados fica aqui, atrás de interfaces definidas no domain/application.
4. **Controllers finos**: não contêm regra de negócio; apenas traduzem HTTP para caso de uso.
5. **Aliases de importação**: usar `@domain/*`, `@application/*`, `@infra/*`, `@controllers/*`, `@routes/*`, `@shared/*` conforme tsconfig.

## Exemplo de fluxo
```
Rota → Controller → Caso de Uso (application) → Repositório (infra) → Banco
```

## Quando aplicar
Qualquer alteração no `homefinapp-api` que envolva nova entidade, caso de uso, repositório ou endpoint.