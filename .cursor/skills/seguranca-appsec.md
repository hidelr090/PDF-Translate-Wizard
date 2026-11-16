# Skill: Segurança da Informação (AppSec)

## Descrição
Aplicar controles de segurança para proteger dados financeiros e pessoais dos usuários do Homefin.

## Regras da skill
1. **Senhas**: hashear com bcryptjs; nunca armazenar texto puro.
2. **JWT**: expiração curta, segredo forte em variável de ambiente, nenhum dado sensível (CPF, dados bancários) no payload.
3. **Validação de entrada**: Zod em todos os endpoints; prevenir SQL injection (TypeORM parametrizado) e XSS.
4. **Respostas seguras**: não retornar senha, token ou campos internos nos DTOs de resposta.
5. **Headers de segurança**: helmet, CORS restrito, express-rate-limit, hpp.
6. **Logs seguros**: nunca logar senhas, tokens, CPF completo ou dados de pagamento.
7. **Segredos fora do repo**: `.env` no `.gitignore`; segredos em cofre de variáveis de ambiente/CI.

## Quando aplicar
Trabalhos que envolvam autenticação, autorização, dados de usuário, pagamentos ou qualquer ponto de entrada da API.