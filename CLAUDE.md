# CLAUDE.md — CMDA Personal (backend)

Regras do grupo para quem (pessoa ou IA) mexer neste repositório. O front fica em `cmda-personal-frontend` e consome esta API.

## Stack e como rodar

- Python 3.14, FastAPI, SQLAlchemy 2.0, Alembic, MySQL (PyMySQL), Pydantic, PyJWT, bcrypt, pytest.
- Rodar: `uvicorn app.main:app --reload` (docs em `/docs`). Dados de demo: `python -m app.seed.seed_data` (`demo@cmda.app` / `Demo@1234`).
- Testes: `pytest -v` (SQLite em memória, não precisa do MySQL). **Todo PR tem que passar nos testes.**

## Arquitetura (não pular camada)

```
router (app/api/v1) -> service (app/services) -> repository (app/repositories) -> model (app/models)
```

- Router só faz HTTP: recebe, chama o service, devolve o schema. Nada de query no router.
- Regra de negócio (RN-xxx) fica no service. Acesso ao banco fica no repository.
- Antes de criar método novo no repository, ver se já existe (ex: `VeiculoRepository.list_by_usuario`).
- Rota que precisa de login usa `Depends(get_current_user)`. Rota `/vehicles/{veiculo_id}/...` usa `Depends(get_owned_vehicle)` — é ele que garante 404/403 (RN-004/RN-011). Nunca checar dono do veículo na mão.

## Contrato com o front

- JSON em **camelCase**: todo schema herda de `CamelModel` (`app/schemas/common.py`). Código Python em snake_case.
- Erro de regra de negócio: levantar `AppError` ou filhas (`NotFoundError`, `ForbiddenError`, `UnauthorizedError`, `ConflictError`) de `app/core/exceptions.py`. Sai como `{"error": "mensagem"}` — o front mostra essa mensagem para o usuário, então escrever em português e de forma clara.
- Não mudar nome de campo nem formato de rota já usado pelo front sem avisar o grupo (as telas quebram).
- Prefixo de tudo: `/api/v1`. Rotas em inglês (`/vehicles`, `/alerts`), campos em português (`placa`, `dataHora`).

## Testes

- Rota nova = teste novo em `tests/`, usando as fixtures do `conftest.py` (`client`, `usuario_autenticado`, `outro_usuario_com_veiculo`).
- Cobrir pelo menos: caminho feliz, sem token (401) e, se for rota de veículo, veículo de outro usuário (403).

## Banco

- Mudou model → gerar migration: `alembic revision --autogenerate -m "descricao"` e revisar o arquivo gerado antes de commitar.
- Nunca commitar `.env` (só o `.env.example`).

## Git

- Branch `master`. Commits pequenos, em português, no formato `tipo: descrição` (`feat:`, `fix:`, `test:`, `docs:`, `chore:`).
- Rodar `pytest` antes de dar push.
- Comentários no código: curtos, minúsculos, só quando explicam o porquê.
