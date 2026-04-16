# Front-end React

Este front foi criado para funcionar como um projeto separado, mesmo estando dentro do repositorio do backend por enquanto.

## Como rodar

1. Entre na pasta `frontend`
2. Instale as dependencias com `npm install`
3. Copie `.env.example` para `.env`
4. Ajuste `VITE_API_URL` se a API estiver em outra URL
5. Rode `npm run dev`

## Fluxo da API

- Cadastro do seller
- Ativacao da conta com codigo recebido no WhatsApp
- Login com e-mail, senha e token do seller
- Cadastro, edicao e inativacao de produtos
- Registro de vendas

## Observacao importante

Depois que a conta e ativada, a API devolve um `token` do seller. Esse token deve ser guardado porque os proximos logins podem exigir esse valor junto com e-mail e senha.
