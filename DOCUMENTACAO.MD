# Galaxy Bank - Documentação do Projeto

## Sumário
- [Visão Geral](#visão-geral)
- [Modelo Entidade Relacionamento (MER)](#modelo-entidade-relacionamento-mer)
- [Funcionalidades Implementadas](#funcionalidades-implementadas)
- [Como Executar o Projeto](#como-executar-o-projeto)
- [Usuários de Demonstração](#usuários-de-demonstracao)
- [Próximos Passos](#próximos-passos)
- [Histórico de Alterações](#histórico-de-alterações)

---

## Visão Geral
Sistema de banco digital com autenticação para três tipos de usuários: **Cliente**, **Atendente** e **Gerente**. O projeto utiliza Django, Bootstrap 5 e segue boas práticas de organização e segurança.

---

## Modelo Entidade Relacionamento (MER)

### Entidades Principais
- **Cliente**: id_cliente (PK), nome, cpf, email, senha, telefone, score_pontos
- **Conta**: id_conta (PK), numero_conta, saldo, tipo, id_cliente (FK)
- **Transacao**: id_transacao (PK), data_hora, valor, tipo, id_conta_origem (FK), id_conta_destino (FK)
- **Credito**: id_credito (PK), limite, limite_utilizado, status, id_cliente (FK), id_gerente (FK)
- **Emprestimo**: id_emprestimo (PK), valor, parcelas, juros, status, id_cliente (FK), id_gerente (FK)
- **Investimento**: id_investimento (PK), tipo, valor_aplicado, data_inicio, rendimento, id_cliente (FK)
- **Shopping**: id_produto (PK), nome_produto, preco, pontos_necessarios
- **Compra**: id_compra (PK), data_hora, id_cliente (FK), id_produto (FK)
- **Gerente**: id_gerente (PK), nome, email, senha
- **Atendente (ChatBot)**: id_atendente (PK), nome_bot, versao
- **Atendimento**: id_atendimento (PK), data_hora, mensagem, id_cliente (FK), id_atendente (FK)

### Relacionamentos
- Cliente possui Conta (1:N)
- Conta realiza Transações (1:N)
- Cliente pode solicitar Crédito (1:N) → autorizado por Gerente
- Cliente pode solicitar Empréstimo (1:N) → autorizado por Gerente
- Cliente investe em Investimentos (1:N)
- Cliente compra Produtos no Shopping (N:M via Compra)
- Cliente interage com Atendente (N:M via Atendimento)

---

## Funcionalidades Implementadas

### Autenticação e Usuários
- Modelo customizado de usuário (`Usuario`) baseado em `AbstractUser`.
- Três tipos de usuário: Cliente, Gerente, Atendente.
- Perfis específicos para cada tipo (Cliente, Gerente, Atendente).
- Backend de autenticação customizado (login por email ou username).
- Redirecionamento automático para dashboard conforme tipo de usuário.
- Sistema de mensagens e feedback.

### Interface e Templates
- Templates responsivos com Bootstrap 5.
- Dashboard exclusivo para cada tipo de usuário.
- Sidebar e navegação contextual.
- Componentes visuais modernos e animados.

### Configuração e Organização
- Estrutura de pastas organizada.
- Arquivos estáticos (CSS/JS) customizados.
- Migrações aplicadas e banco de dados pronto.
- Comando para criar usuários de demonstração.

---

## Como Executar o Projeto

1. Instale as dependências do projeto (Django 5+).
2. Execute as migrações:
   ```bash
   python manage.py migrate
   ```
3. Crie usuários de demonstração:
   ```bash
   python manage.py create_demo_users
   ```
4. Inicie o servidor:
   ```bash
   python manage.py runserver
   ```
5. Acesse: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Usuários de Demonstração

| Tipo      | Usuário                | Senha        |
|-----------|------------------------|--------------|
| Admin     | admin                  | admin123     |
| Cliente   | cliente@galaxy.com     | cliente123   |
| Gerente   | gerente@galaxy.com     | gerente123   |
| Atendente | atendente@galaxy.com   | atendente123 |

---

## Próximos Passos

- [ ] Implementar funcionalidades de Conta e Transação
- [ ] Criar módulos de Investimento e Empréstimo
- [ ] Adicionar sistema de notificações em tempo real
- [ ] Melhorar segurança e validações
- [ ] Documentar APIs e endpoints
- [ ] Testes automatizados
- [ ] Melhorar interface mobile
- [ ] Adicionar logs e monitoramento

---

## Histórico de Alterações

- **24/09/2025**: Estrutura inicial, autenticação, dashboards, usuários de demonstração, documentação organizada.

---

> Mantenha esta documentação sempre atualizada conforme novas funcionalidades forem implementadas!
