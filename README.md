# CMDA Personal — Backend

API do backend do **CMDA Personal** (Central de Mapeamento de Desempenho Automotivo), desenvolvida na Fase 01 do 6º período do Projeto Integrador. Implementa autenticação, regras de negócio e persistência de dados para o monitoramento veicular via OBD2/ELM327.

Esta API é desacoplada de qualquer cliente específico: hoje serve o frontend web do projeto, integrado na Fase 02, e foi desenhada para futuramente servir também o app mobile (Flutter) e um simulador de leituras de sensor, sem necessidade de reescrita.

## Estrutura de arquivos

```
├── app/
│   ├── main.py                       # Ponto de entrada da aplicação FastAPI
│   ├── api/
│   │   ├── deps.py                   # Dependências compartilhadas (auth, ownership de veículo)
│   │   └── v1/
│   │       ├── router.py             # Agregador das rotas da v1
│   │       ├── auth.py                # Rotas de autenticação e recuperação de senha
│   │       ├── users.py               # Rotas de usuário
│   │       ├── vehicles.py            # Rotas de veículo
│   │       ├── telemetry.py           # Rotas de telemetria (leituras)
│   │       ├── alerts.py              # Rotas de alertas
│   │       └── diagnostics.py         # Rotas de diagnóstico
│   ├── core/
│   │   ├── config.py                  # Configurações e variáveis de ambiente
│   │   ├── database.py                # Conexão e sessão do banco (SQLAlchemy)
│   │   ├── exceptions.py              # Exceções customizadas
│   │   ├── security.py                # Hash de senha e JWT
│   │   └── timeutils.py               # Utilitários de data/hora
│   ├── models/                        # Mapeamento ORM das tabelas
│   │   ├── usuario.py
│   │   ├── veiculo.py
│   │   ├── leitura.py
│   │   ├── alerta.py
│   │   ├── diagnostico.py
│   │   ├── diagnostico_item.py
│   │   ├── password_reset.py
│   │   └── revoked_token.py
│   ├── repositories/                  # Acesso a dados (SQLAlchemy puro)
│   │   ├── usuario_repository.py
│   │   ├── veiculo_repository.py
│   │   ├── leitura_repository.py
│   │   ├── alerta_repository.py
│   │   ├── diagnostico_repository.py
│   │   ├── password_reset_repository.py
│   │   └── revoked_token_repository.py
│   ├── schemas/                       # Validação de payloads (Pydantic)
│   │   ├── usuario.py
│   │   ├── veiculo.py
│   │   ├── leitura.py
│   │   ├── alerta.py
│   │   ├── diagnostico.py
│   │   ├── auth.py
│   │   └── common.py
│   ├── services/                      # Regras de negócio (RN-001 a RN-013)
│   │   ├── auth_service.py
│   │   ├── veiculo_service.py
│   │   ├── telemetria_service.py
│   │   ├── alerta_service.py
│   │   └── diagnostico_service.py
│   └── seed/
│       └── seed_data.py               # Popula dados de demonstração
├── alembic/
│   ├── env.py                         # Configuração das migrations
│   └── versions/                      # Histórico de migrations do schema
├── alembic.ini                        # Configuração do Alembic
├── tests/
│   ├── conftest.py                    # Fixtures (SQLite em memória)
│   ├── test_auth.py                   # Login, recuperação de senha, logout
│   ├── test_vehicles_ownership.py     # Regra de posse de veículo (RN-004/RN-011)
│   ├── test_vehicles_list.py          # GET /vehicles (só veículos do usuário logado)
│   ├── test_telemetry.py              # Telemetria e estado de conexão (RN-005)
│   ├── test_alerts.py                 # Fluxo de alertas
│   └── test_faixas_leitura.py         # Alertas e diagnóstico gerados pela leitura (RN-013)
├── requirements.txt                   # Dependências do projeto
├── .env.example                       # Modelo de variáveis de ambiente
└── README.md
```

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
  -> service (app/services)  -> regras de negócio (RN-001 a RN-013)
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

Para o aplicativo mobile acessar a API pelo celular, rode escutando na rede:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

E libere a porta 8000 no firewall do Windows, rodando uma vez no PowerShell como administrador:

```bash
Get-NetFirewallRule -DisplayName "python.exe" | Where-Object Action -eq Block | Disable-NetFirewallRule
New-NetFirewallRule -DisplayName "CMDA API 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

No app, informe o endereço `http://<ip-do-notebook>:8000/api/v1`. O IP aparece no comando `ipconfig`. O passo a passo completo da demonstração, com o simulador e o app, está no [roteiro do cmda-personal-mobile](https://github.com/jean-aluno-uni/cmda-personal-mobile#roteiro-completo-da-demonstração).

### 6. Rodar os testes

```bash
pytest -v
```

Os testes usam SQLite em memória (não precisam do MySQL rodando) e cobrem: login, fluxo completo de recuperação de senha (incluindo token de uso único), logout invalidando sessão, a regra de posse de veículo (RN-004/RN-011 — o caso mais citado na avaliação), telemetria respeitando o estado de conexão (RN-005), o fluxo de alertas e os alertas e diagnósticos gerados a partir das leituras (RN-013).

## Alertas e diagnóstico gerados pela leitura (RN-013)

Cada leitura recebida em `POST /vehicles/{id}/readings` é comparada com a faixa de referência de cada indicador em `app/services/telemetria_service.py`. Quando um indicador sai da faixa, a API cria um alerta com a origem `Motor` ou `Bateria`. Enquanto o valor continua fora da faixa o alerta não se repete, e só volta a ser criado depois que o valor normaliza e sai de novo. A cada leitura a API também grava um diagnóstico novo com valor, referência e a marcação de alerta de cada item, e as telas mostram sempre o mais recente.

| Indicador | Faixa de referência |
|---|---|
| RPM | 750 a 3000 RPM |
| Velocidade | até 120 km/h |
| Temp. geral | até 110 °C |
| Temp. óleo | até 120 °C |
| Temp. líquido arrefecimento | até 105 °C |
| Temp. ar admissão | até 45 °C |
| Tensão da bateria | 12 a 15 V |

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
| Veículo | `GET /vehicles`, `GET /vehicles/{id}`, `GET /vehicles/{id}/status`, `POST /vehicles/{id}/{connect,disconnect}` |
| Telemetria | `GET /vehicles/{id}/telemetry/latest`, `POST /vehicles/{id}/readings`, `GET /vehicles/{id}/temperature/history` |
| Alertas | `GET /vehicles/{id}/alerts/summary`, `GET /vehicles/{id}/alerts`, `POST /vehicles/{id}/alerts` |
| Diagnóstico | `GET /vehicles/{id}/diagnostics`, `POST /vehicles/{id}/diagnostics` |

## Integração com o frontend

A mesma API atende o aplicativo Android [`cmda-personal-mobile`](https://github.com/jean-aluno-uni/cmda-personal-mobile), que lê o veículo por Bluetooth e envia as leituras em `POST /vehicles/{id}/readings`, e o [`cmda-personal-simulador`](https://github.com/jean-aluno-uni/cmda-personal-simulador), usado nas demonstrações.

O frontend (`cmda-personal-frontend`) consome esta API por HTTP, sempre passando pelo `apiCall` de `js/api.js`.

- **`GET /vehicles`** devolve a lista de veículos do usuário do token (usa `VeiculoRepository.list_by_usuario`). O front chama logo depois do login para descobrir o `id` do veículo e guardar no `sessionStorage`; todas as outras rotas usam esse id em `/vehicles/{id}/...`.
- **Formato:** tudo trafega em JSON. Os campos saem em **camelCase** (`accessToken`, `dataHora`, `tabelaAlertas`) por causa do `CamelModel` em `app/schemas/common.py`; o código Python continua em snake_case. Datas saem em UTC sem fuso (`2026-10-05T14:30:00`).
- **Autenticação:** o front manda `Authorization: Bearer <token>` em toda requisição. Token inválido, expirado ou revogado no logout → `401`.
- **Erros:** regras de negócio respondem `{"error": "mensagem"}` com o status certo (`401`, `403`, `404`, `409`). Erros de validação do payload (Pydantic) saem no formato padrão do FastAPI, `422` com `{"detail": [...]}`.
- **CORS:** configurado em `app/main.py` pela variável `CORS_ORIGINS`. Com `*` (padrão de dev) qualquer origem pode chamar; para fixar o front, use ex.: `CORS_ORIGINS=http://127.0.0.1:5500,http://localhost:5500`. Como o token vai no header (e não em cookie), não é preciso `allow_credentials`.

## Decisões de design (trade-offs assumidos pelo prazo da Fase 01)

- **Blacklist simples de tokens** (tabela `revoked_tokens`) em vez de um cache dedicado (ex: Redis) para RN-012 — suficiente para o volume da aplicação nesta fase, evita introduzir infraestrutura nova.
- **Sem refresh token** ainda — token de acesso com expiração de 60 minutos; renovação automática fica como evolução futura.
- **Testes contra SQLite em memória**, não contra o MySQL real — mais rápido e não exige MySQL disponível para rodar a suíte (a aplicação em si roda contra MySQL normalmente).
- **Extensões ao modelo de dados original** (documentadas na Parte 18 do documento de especificação): coluna `Conectado`/`UltimaConexao` em `veiculos`, coluna `Role` em `usuarios`, colunas `Referencia`/`Alerta` em `diagnostico_itens`, coluna `TempArC` em `leituras`, e as tabelas novas `password_resets` e `revoked_tokens`.
