# Skill: Documentação de API (Swagger / OpenAPI)

## Descrição
Manter a documentação da API do `homefinapp-api` atualizada usando Swagger/OpenAPI, para que frontend, mobile e outros consumidores conheçam os contratos.

## Regras da skill
1. **Documentar todo endpoint novo ou alterado**: método, rota, parâmetros, body, respostas (200, 400, 401, 500) e exemplos.
2. **Manter schemas coerentes com Zod**: o modelo no Swagger deve refletir o schema de validação usado no backend.
3. **Versionamento**: anotar mudanças quebrantes (breaking changes) na documentação.
4. **Acessível**: Swagger UI disponível em ambiente de desenvolvimento para consulta rápida.

## Quando aplicar
Criação ou alteração de rotas/controllers no `homefinapp-api`.