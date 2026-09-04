from sqlalchemy.orm import Session

from app.repositories.diagnostico_repository import DiagnosticoRepository
from app.schemas.diagnostico import DiagnosticoCreate, DiagnosticoItemOut, DiagnosticoOut


class DiagnosticoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DiagnosticoRepository(db)

    def registrar_diagnostico(self, veiculo_id: int, dados: DiagnosticoCreate) -> DiagnosticoOut:
        itens = [item.model_dump(exclude_none=True) for item in dados.itens]
        diagnostico = self.repo.create(veiculo_id, dados.data_hora, itens)
        self.db.commit()
        return self._to_out(diagnostico)

    def obter_diagnostico(self, veiculo_id: int, indicadores: list[str] | None) -> DiagnosticoOut | None:
        diagnostico = self.repo.get_latest(veiculo_id)
        if diagnostico is None:
            return None

        out = self._to_out(diagnostico)
        if indicadores:
            filtro = {i.lower() for i in indicadores}
            out.itens = [item for item in out.itens if item.indicador.lower() in filtro]
        return out

    @staticmethod
    def _to_out(diagnostico) -> DiagnosticoOut:
        itens = [DiagnosticoItemOut.model_validate(item) for item in diagnostico.itens]
        status_geral = any(item.alerta for item in itens)
        return DiagnosticoOut(
            id=diagnostico.id,
            data_hora=diagnostico.data_hora,
            status_geral=status_geral,
            itens=itens,
        )
