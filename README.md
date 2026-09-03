# CMDA Personal — Backend

API do backend do **CMDA Personal** (Central de Mapeamento de Desempenho Automotivo), desenvolvida na Fase 01 do 6º período do Projeto Integrador. Implementa autenticação, regras de negócio e persistência de dados para o monitoramento veicular via OBD2/ELM327.

Esta API é desacoplada de qualquer cliente específico: hoje serve o frontend web mockado do projeto, e foi desenhada para futuramente servir também o app mobile (Flutter), um painel administrativo web e um simulador de leituras de sensor, sem necessidade de reescrita.

## Stack

- **FastAPI** — framework web assíncrono, com documentação interativa automática (Swagger em `/docs`).
- **SQLAlchemy 2.0** — ORM, separando o modelo de dados da lógica de negócio.
- **Alembic** — versionamento de migrations do schema do banco.
- **MySQL** (via **PyMySQL**, driver puro Python) — persistência relacional.
- **Pydantic** — validação de payloads de entrada/saída (schemas em camelCase, código Python em snake_case).
- **PyJWT** — autenticação via JSON Web Token.
- **bcrypt** — hash de senha (usado diretamente, sem a camada `passlib`, que está sem manutenção e é incompatível com versões atuais do bcrypt).
- **pytest** — testes automatizados (rodam contra SQLite em memória, sem depender do MySQL estar no ar).

## Arquitetura em camadas

```
router (app/api/v1)     -> validação HTTP, autenticação, ownership de veículo
  -> service (app/services)  -> regras de negócio (RN-001 a RN-012)
    -> repository (app/repositories) -> acesso a dados (SQLAlchemy puro)
      -> model (app/models)  -> mapeamento ORM das tabelas
```

Essa separação existe para que cada regra de negócio (RN-xxx) fique rastreável a um trecho de código específico, e para que trocar o banco de dados ou estender o schema no futuro não exija tocar na lógica de negócio.

Dependências centrais em `app/api/deps.py`:
- `get_current_user` — aplica RN-001 (só usuário autenticado acessa rotas internas) em qualquer router protegido.
- `get_owned_vehicle` — aplica RN-004/RN-011 (dados de veículo só acessíveis pelo dono) de forma centralizada, reaproveitada em todas as rotas `/vehicles/{id}/...`.

## Como rodar localmente

### 1. Pré-requisitos

- Python 3.14+ instalado.
- Um servidor MySQL rodando (local ou remoto).

### 2. Configuração

```bash
cd cmda-personal-backend
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
copy .env.example .env            # depois edite com suas credenciais reais
```

### 3. Banco de dados e migrations

Crie o banco (se ainda não existir):

```sql
CREATE DATABASE cmda_personal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Aplique as migrations:

```bash
alembic upgrade head
```

Para gerar uma nova migration depois de alterar um model:

```bash
alembic revision --autogenerate -m "descricao da mudanca"
alembic upgrade head
```

### 4. Popular dados de demonstração (opcional, recomendado)

```bash
python -m app.seed.seed_data
```

Cria dois usuários:
- `demo@cmda.app` / `Demo@1234` — com veículo conectado, leituras, alertas e um diagnóstico completo.
- `outro@cmda.app` / `Outro@1234` — com outro veículo, útil para testar manualmente a regra de posse (RN-004/RN-011): tentar acessar o veículo deste usuário autenticado como o `demo@cmda.app` deve retornar 403.

### 5. Rodar a API

```bash
uvicorn app.main:app --reload
```

Acesse a documentação interativa em **http://127.0.0.1:8000/docs**.

### 6. Rodar os testes

```bash
pytest -v
```

Os testes usam SQLite em memória (não precisam do MySQL rodando) e cobrem: login, fluxo completo de recuperação de senha (incluindo token de uso único), logout invalidando sessão, a regra de posse de veículo (RN-004/RN-011 — o caso mais citado na avaliação), telemetria respeitando o estado de conexão (RN-005) e o fluxo de alertas.

## Fluxo de recuperação de senha

Como esta fase não exige envio real de e-mail, o código OTP é apenas registrado no console do servidor (`logger.info`, visível no terminal onde o `uvicorn` está rodando):

```
POST /auth/password/forgot        {email}              -> gera OTP, loga no console
POST /auth/password/otp/resend    {email}               -> invalida o anterior, gera outro
POST /auth/password/otp/verify    {email, codigo}       -> retorna resetToken de uso único
POST /auth/password/reset         {resetToken, novaSenha} -> valida as 5 regras de senha
```

## Principais endpoints

Prefixo: `/api/v1`. Lista completa e interativa em `/docs`.

| Área | Endpoints |
|---|---|
| Auth | `POST /auth/login`, `GET /auth/me`, `POST /auth/logout`, `POST /auth/password/{forgot,otp/resend,otp/verify,reset}` |
| Veículo | `GET /vehicles/{id}`, `GET /vehicles/{id}/status`, `POST /vehicles/{id}/{connect,disconnect}` |
| Telemetria | `GET /vehicles/{id}/telemetry/latest`, `POST /vehicles/{id}/readings`, `GET /vehicles/{id}/temperature/history` |
| Alertas | `GET /vehicles/{id}/alerts/summary`, `GET /vehicles/{id}/alerts`, `POST /vehicles/{id}/alerts` |
| Diagnóstico | `GET /vehicles/{id}/diagnostics`, `POST /vehicles/{id}/diagnostics` |

## Decisões de design (trade-offs assumidos pelo prazo da Fase 01)

- **Blacklist simples de tokens** (tabela `revoked_tokens`) em vez de um cache dedicado (ex: Redis) para RN-012 — suficiente para o volume da aplicação nesta fase, evita introduzir infraestrutura nova.
- **Sem refresh token** ainda — token de acesso com expiração de 60 minutos; renovação automática fica como evolução futura.
- **Testes contra SQLite em memória**, não contra o MySQL real — mais rápido e não exige MySQL disponível para rodar a suíte (a aplicação em si roda contra MySQL normalmente).
- **Extensões ao modelo de dados original** (documentadas na Parte 18 do documento de especificação): coluna `Conectado`/`UltimaConexao` em `veiculos`, coluna `Role` em `usuarios`, colunas `Referencia`/`Alerta` em `diagnostico_itens`, coluna `TempArC` em `leituras`, e as tabelas novas `password_resets` e `revoked_tokens`.
