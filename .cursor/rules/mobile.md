# Rule: Regras do Mobile (homefinapp-mobile)

Aplica-se a `homefinapp-mobile` (React Native / Expo).

## Navegação e telas
- Navegação organizada por fluxo (stacks/tabs): dashboard, transações, perfil, etc.
- Layouts responsivos para diferentes tamanhos de tela móvel.

## Rede e API
- Tratar falta de conexão com mensagem amigável e opção de retry.
- Usar os mesmos contratos (schemas/Swagger) da API do backend.
- Tratar loading, error e empty state em toda tela que consome dados.

## Ambiente e build
- URL da API por ambiente via variável de ambiente; nunca commitar valor real.
- Manter `app.json` atualizado; configurar EAS/Expo para builds.

## Quando aplicar
Trabalho em telas, navegação ou integração com API no `homefinapp-mobile`.