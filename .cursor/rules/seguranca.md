# Rule: Regras de Segurança (AppSec)

Aplica-se a todo o workspace, com ênfase no `homefinapp-api`.

1. **Senhas**: hashear com bcryptjs; nunca texto puro.
2. **JWT**: expiração curta, segredo forte em variável de ambiente, nenhum dado pessoal/financeiro no payload.
3. **Validação de entrada**: Zod em todos os endpoints que recebem dados do cliente.
4. **Respostas**: nunca retornar senha, token ou campos internos nos DTOs de resposta.
5. **Headers de segurança**: helmet, CORS restrito, rate-limit, hpp.
6. **Logs**: nunca logar senhas, tokens, CPF completo ou dados de pagamento.
7. **Segredos**: `.env` no `.gitignore`; segredos de produção fora do repositório.

## Quando aplicar
Qualquer alteração que envolva autenticação, autorização, dados de usuário ou pagamentos.