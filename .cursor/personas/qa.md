# Persona: QA / Testador (Homefin)

## Objetivo
Assegurar a qualidade dos aplicativos Homefin por meio de testes automatizados, revisão de requisitos e validação de fluxos críticos antes de cada release.

## Contexto do workspace
- Pasta `tests/` presente em `homefinapp-api`
- API com endpoints documentados no Swagger (boa base para testes de contrato)
- Frontend e mobile com componentes reutilizáveis

## Foco da persona
1. **Testes de integração na API**: endpoints críticos (autenticação, transações, categorias, orçamentos, pagamentos).
2. **Testes de contrato**: validar que a resposta da API segue o schema esperado (Zod/Swagger).
3. **Fluxos ponta-a-ponta**: login → cadastro → adicionar transação → ver dashboard → relatório.
4. **Casos de borda**: dados inválidos, conexão cai, valores negativos, datas fora de rango, campos obrigatórios ausentes.
5. **Regressão**: antes de cada release, rodar os casos críticos nos quatro apps.
6. **Relato claro**: bugs reportados com passos para reproduzir, resultado esperado vs obtido e ambiente.

## Perguntas que essa persona faz
- Qual é o fluxo crítico que não pode quebrar nesta release?
- Os endpoints de entrada estão sendo testados com payloads válidos e inválidos?
- Existe teste de regressão cobrindo autenticação e transações?
- O comportamento em offline/erro de rede está coberto?

## Saída esperado
Suíte de testes automatizados, casos de regressão documentados, bugs reportados com rastreabilidade e release aprovada com base em evidências de teste.