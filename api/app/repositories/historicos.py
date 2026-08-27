from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, delete, exists, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.domain.entities import (
    CandidatoEquivalencia,
    CorrespondenciaProposta,
    EquivalenciaManual,
    HistoricoDocumento,
    ImportacaoHistorico,
    ItemHistoricoEscolar,
    ItemImportacaoHistorico,
)
from app.models.academic import (
    ComponenteCurricularModel,
    CorrespondenciaDisciplinaModel,
    DisciplinaModel,
    EquivalenciaManualDisciplinaModel,
    HistoricoImportacaoModel,
    ItemHistoricoImportadoModel,
    UsuarioModel,
)


class SqlAlchemyHistoricoImportadoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_student(
        self, matricula: str
    ) -> tuple[ItemHistoricoEscolar, ...]:
        statement = (
            select(
                ItemHistoricoImportadoModel,
                DisciplinaModel.codigo.label("disciplina_codigo"),
                DisciplinaModel.nome.label("disciplina_nome"),
                CorrespondenciaDisciplinaModel.metodo,
                CorrespondenciaDisciplinaModel.confianca,
            )
            .join(
                HistoricoImportacaoModel,
                HistoricoImportacaoModel.id == ItemHistoricoImportadoModel.importacao_id,
            )
            .join(UsuarioModel, UsuarioModel.id == HistoricoImportacaoModel.usuario_id)
            .join(
                CorrespondenciaDisciplinaModel,
                CorrespondenciaDisciplinaModel.item_id == ItemHistoricoImportadoModel.id,
            )
            .join(
                ComponenteCurricularModel,
                ComponenteCurricularModel.id
                == CorrespondenciaDisciplinaModel.ppc_componente_id,
            )
            .join(
                DisciplinaModel,
                DisciplinaModel.codigo == ComponenteCurricularModel.disciplina_codigo,
            )
            .where(
                UsuarioModel.matricula == matricula,
                UsuarioModel.ppc_id.is_not(None),
                HistoricoImportacaoModel.ativa.is_(True),
                CorrespondenciaDisciplinaModel.ppc_id == UsuarioModel.ppc_id,
                CorrespondenciaDisciplinaModel.status == "CONFIRMADA",
            )
            .order_by(
                ItemHistoricoImportadoModel.ano,
                ItemHistoricoImportadoModel.semestre,
                DisciplinaModel.nome,
            )
        )
        rows = (await self._session.execute(statement)).all()
        return tuple(
            ItemHistoricoEscolar(
                matricula=matricula,
                disciplina_codigo=row.disciplina_codigo,
                disciplina=row.disciplina_nome,
                professores=row[0].professores,
                ano=row[0].ano,
                semestre=row[0].semestre,
                codigo_turma="HISTÓRICO",
                media_final=float(row[0].media) if row[0].media is not None else None,
                faltas_total=0,
                situacao_final=row[0].situacao,
                fonte="HISTORICO_IMPORTADO",
                disciplina_codigo_origem=row[0].codigo_original,
                disciplina_origem=row[0].nome_original,
                metodo_correspondencia=row.metodo,
                confianca_correspondencia=float(row.confianca),
            )
            for row in rows
        )


class SqlAlchemyHistoricoImportacaoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def replace_active(
        self,
        *,
        usuario_id: UUID,
        nome_arquivo: str,
        hash_arquivo: str,
        documento: HistoricoDocumento,
        ppc_referencia_id: int,
        correspondencias: tuple[CorrespondenciaProposta, ...],
    ) -> ImportacaoHistorico:
        await self._session.execute(
            update(HistoricoImportacaoModel)
            .where(
                HistoricoImportacaoModel.usuario_id == usuario_id,
                HistoricoImportacaoModel.ativa.is_(True),
            )
            .values(ativa=False)
        )

        now = datetime.now(UTC)
        import_model = HistoricoImportacaoModel(
            usuario_id=usuario_id,
            ppc_referencia_id=ppc_referencia_id,
            nome_arquivo=nome_arquivo,
            hash_arquivo=hash_arquivo,
            curso_codigo_documento=documento.curso_codigo,
            ppc_ano_documento=documento.ppc_ano,
            nome_aluno_documento=documento.nome_aluno,
            matricula_documento=documento.matricula,
            data_emissao=documento.data_emissao,
            media_geral=documento.media_geral,
            carga_horaria_realizada=documento.carga_horaria_realizada,
            carga_horaria_total=documento.carga_horaria_total,
            percentual_concluido=documento.percentual_concluido,
            status="PROCESSADA",
            ativa=True,
            total_itens=len(documento.itens),
            criado_em=now,
        )
        self._session.add(import_model)
        await self._session.flush()

        item_models: list[ItemHistoricoImportadoModel] = []
        for item in documento.itens:
            item_model = ItemHistoricoImportadoModel(
                importacao_id=import_model.id,
                codigo_original=item.codigo,
                nome_original=item.nome,
                carga_horaria=item.carga_horaria,
                creditos=item.creditos,
                ano=item.ano,
                semestre=item.semestre,
                situacao=item.situacao,
                media=item.media,
                dispensa=item.dispensa,
                categoria=item.categoria,
                professores=item.professores,
            )
            self._session.add(item_model)
            item_models.append(item_model)
        await self._session.flush()

        for match in correspondencias:
            self._session.add(
                CorrespondenciaDisciplinaModel(
                    item_id=item_models[match.item_indice].id,
                    ppc_id=match.ppc_id,
                    ppc_componente_id=match.ppc_componente_id,
                    metodo=match.metodo,
                    confianca=match.confianca,
                    status=match.status,
                    criado_em=now,
                )
            )

        await self._session.commit()
        result = await self.get_active(usuario_id)
        if result is None:
            raise RuntimeError("A importação não pôde ser recuperada após a gravação.")
        return result

    async def get_active(self, usuario_id: UUID) -> ImportacaoHistorico | None:
        import_statement = select(HistoricoImportacaoModel).where(
            HistoricoImportacaoModel.usuario_id == usuario_id,
            HistoricoImportacaoModel.ativa.is_(True),
        )
        import_model = (await self._session.scalars(import_statement)).one_or_none()
        if import_model is None:
            return None

        statement = (
            select(
                ItemHistoricoImportadoModel,
                CorrespondenciaDisciplinaModel,
                DisciplinaModel.codigo.label("disciplina_codigo"),
                DisciplinaModel.nome.label("disciplina_nome"),
            )
            .outerjoin(
                CorrespondenciaDisciplinaModel,
                and_(
                    CorrespondenciaDisciplinaModel.item_id
                    == ItemHistoricoImportadoModel.id,
                    CorrespondenciaDisciplinaModel.ppc_id
                    == import_model.ppc_referencia_id,
                ),
            )
            .outerjoin(
                ComponenteCurricularModel,
                ComponenteCurricularModel.id
                == CorrespondenciaDisciplinaModel.ppc_componente_id,
            )
            .outerjoin(
                DisciplinaModel,
                DisciplinaModel.codigo == ComponenteCurricularModel.disciplina_codigo,
            )
            .where(ItemHistoricoImportadoModel.importacao_id == import_model.id)
            .order_by(
                ItemHistoricoImportadoModel.ano,
                ItemHistoricoImportadoModel.semestre,
                ItemHistoricoImportadoModel.nome_original,
            )
        )
        rows = (await self._session.execute(statement)).all()
        items = tuple(self._summary_item(row) for row in rows)
        identified = sum(item.status_correspondencia == "CONFIRMADA" for item in items)
        suggestions = sum(item.status_correspondencia == "SUGERIDA" for item in items)
        return ImportacaoHistorico(
            id=import_model.id,
            nome_arquivo=import_model.nome_arquivo,
            criado_em=import_model.criado_em,
            curso_codigo_documento=import_model.curso_codigo_documento,
            ppc_ano_documento=import_model.ppc_ano_documento,
            ppc_referencia_id=import_model.ppc_referencia_id,
            total_itens=import_model.total_itens,
            identificados=identified,
            requerem_confirmacao=suggestions,
            nao_identificados=import_model.total_itens - identified - suggestions,
            itens=items,
        )

    async def review_correspondence(
        self, *, usuario_id: UUID, correspondencia_id: int, action: str
    ) -> ImportacaoHistorico | None:
        statement = (
            select(CorrespondenciaDisciplinaModel)
            .join(
                ItemHistoricoImportadoModel,
                ItemHistoricoImportadoModel.id
                == CorrespondenciaDisciplinaModel.item_id,
            )
            .join(
                HistoricoImportacaoModel,
                HistoricoImportacaoModel.id
                == ItemHistoricoImportadoModel.importacao_id,
            )
            .where(
                CorrespondenciaDisciplinaModel.id == correspondencia_id,
                HistoricoImportacaoModel.usuario_id == usuario_id,
                HistoricoImportacaoModel.ativa.is_(True),
            )
        )
        model = (await self._session.scalars(statement)).one_or_none()
        if model is None:
            return None
        model.status = "CONFIRMADA" if action == "confirmar" else "REJEITADA"
        model.revisado_em = datetime.now(UTC)
        await self._session.commit()
        return await self.get_active(usuario_id)

    @staticmethod
    def _summary_item(row) -> ItemImportacaoHistorico:
        item = row[0]
        match = row[1]
        return ItemImportacaoHistorico(
            id=item.id,
            codigo_original=item.codigo_original,
            nome_original=item.nome_original,
            carga_horaria=item.carga_horaria,
            ano=item.ano,
            semestre=item.semestre,
            situacao=item.situacao,
            media=float(item.media) if item.media is not None else None,
            correspondencia_id=match.id if match else None,
            disciplina_codigo=row.disciplina_codigo,
            disciplina_nome=row.disciplina_nome,
            metodo_correspondencia=match.metodo if match else None,
            confianca_correspondencia=float(match.confianca) if match else None,
            status_correspondencia=match.status if match else None,
        )


class SqlAlchemyEquivalenciaManualRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_candidates(
        self, *, usuario_id: UUID, ppc_id: int
    ) -> tuple[CandidatoEquivalencia, ...]:
        confirmed_component = aliased(ComponenteCurricularModel)
        manual_component = aliased(ComponenteCurricularModel)
        manual_use = aliased(EquivalenciaManualDisciplinaModel)

        already_matched = exists(
            select(1)
            .select_from(CorrespondenciaDisciplinaModel)
            .join(
                confirmed_component,
                confirmed_component.id
                == CorrespondenciaDisciplinaModel.ppc_componente_id,
            )
            .where(
                CorrespondenciaDisciplinaModel.item_id
                == ItemHistoricoImportadoModel.id,
                CorrespondenciaDisciplinaModel.ppc_id == ppc_id,
                CorrespondenciaDisciplinaModel.status == "CONFIRMADA",
                confirmed_component.tipo_componente == "DISCIPLINA_OBRIGATORIA",
            )
        )
        manually_matched_to_required = exists(
            select(1)
            .select_from(EquivalenciaManualDisciplinaModel)
            .join(
                manual_component,
                manual_component.id
                == EquivalenciaManualDisciplinaModel.ppc_componente_id,
            )
            .where(
                EquivalenciaManualDisciplinaModel.historico_item_id
                == ItemHistoricoImportadoModel.id,
                EquivalenciaManualDisciplinaModel.usuario_id == usuario_id,
                EquivalenciaManualDisciplinaModel.ppc_id == ppc_id,
                manual_component.tipo_componente == "DISCIPLINA_OBRIGATORIA",
            )
        )

        statement = (
            select(
                ItemHistoricoImportadoModel,
                manual_use.ppc_componente_id.label("componente_em_uso_id"),
                manual_use.slot_ordem.label("slot_em_uso"),
            )
            .join(
                HistoricoImportacaoModel,
                HistoricoImportacaoModel.id
                == ItemHistoricoImportadoModel.importacao_id,
            )
            .outerjoin(
                manual_use,
                and_(
                    manual_use.historico_item_id == ItemHistoricoImportadoModel.id,
                    manual_use.usuario_id == usuario_id,
                    manual_use.ppc_id == ppc_id,
                ),
            )
            .where(
                HistoricoImportacaoModel.usuario_id == usuario_id,
                HistoricoImportacaoModel.ativa.is_(True),
                ~already_matched,
                ~manually_matched_to_required,
            )
            .order_by(
                ItemHistoricoImportadoModel.ano.desc(),
                ItemHistoricoImportadoModel.semestre.desc(),
                ItemHistoricoImportadoModel.nome_original,
            )
        )
        rows = (await self._session.execute(statement)).all()
        return tuple(
            CandidatoEquivalencia(
                id=row[0].id,
                codigo_original=row[0].codigo_original,
                nome_original=row[0].nome_original,
                carga_horaria=row[0].carga_horaria,
                ano=row[0].ano,
                semestre=row[0].semestre,
                situacao=row[0].situacao,
                media=float(row[0].media) if row[0].media is not None else None,
                em_uso=row.componente_em_uso_id is not None,
                componente_em_uso_id=row.componente_em_uso_id,
                slot_em_uso=row.slot_em_uso,
            )
            for row in rows
        )

    async def list_mappings(
        self, *, usuario_id: UUID, ppc_id: int
    ) -> tuple[EquivalenciaManual, ...]:
        statement = (
            select(
                EquivalenciaManualDisciplinaModel,
                ItemHistoricoImportadoModel,
                ComponenteCurricularModel,
                DisciplinaModel.nome.label("disciplina_nome"),
            )
            .join(
                ItemHistoricoImportadoModel,
                ItemHistoricoImportadoModel.id
                == EquivalenciaManualDisciplinaModel.historico_item_id,
            )
            .join(
                HistoricoImportacaoModel,
                HistoricoImportacaoModel.id
                == ItemHistoricoImportadoModel.importacao_id,
            )
            .join(
                ComponenteCurricularModel,
                ComponenteCurricularModel.id
                == EquivalenciaManualDisciplinaModel.ppc_componente_id,
            )
            .outerjoin(
                DisciplinaModel,
                DisciplinaModel.codigo
                == ComponenteCurricularModel.disciplina_codigo,
            )
            .where(
                EquivalenciaManualDisciplinaModel.usuario_id == usuario_id,
                EquivalenciaManualDisciplinaModel.ppc_id == ppc_id,
                HistoricoImportacaoModel.ativa.is_(True),
            )
            .order_by(
                ComponenteCurricularModel.semestre_recomendado,
                ComponenteCurricularModel.ordem_semestre,
                EquivalenciaManualDisciplinaModel.slot_ordem,
            )
        )
        rows = (await self._session.execute(statement)).all()
        return tuple(self._mapping(row) for row in rows)

    async def save(
        self,
        *,
        usuario_id: UUID,
        ppc_id: int,
        ppc_componente_id: int,
        slot_ordem: int,
        historico_item_id: int,
    ) -> EquivalenciaManual:
        now = datetime.now(UTC)
        statement = (
            insert(EquivalenciaManualDisciplinaModel)
            .values(
                usuario_id=usuario_id,
                ppc_id=ppc_id,
                ppc_componente_id=ppc_componente_id,
                slot_ordem=slot_ordem,
                historico_item_id=historico_item_id,
                criado_em=now,
                atualizado_em=now,
            )
            .on_conflict_do_update(
                constraint="uk_equivalencia_manual_slot",
                set_={
                    "historico_item_id": historico_item_id,
                    "atualizado_em": now,
                },
            )
        )
        await self._session.execute(statement)
        await self._session.commit()
        mappings = await self.list_mappings(usuario_id=usuario_id, ppc_id=ppc_id)
        return next(
            mapping
            for mapping in mappings
            if mapping.ppc_componente_id == ppc_componente_id
            and mapping.slot_ordem == slot_ordem
        )

    async def delete(
        self,
        *,
        usuario_id: UUID,
        ppc_id: int,
        ppc_componente_id: int,
        slot_ordem: int,
    ) -> bool:
        result = await self._session.execute(
            delete(EquivalenciaManualDisciplinaModel).where(
                EquivalenciaManualDisciplinaModel.usuario_id == usuario_id,
                EquivalenciaManualDisciplinaModel.ppc_id == ppc_id,
                EquivalenciaManualDisciplinaModel.ppc_componente_id
                == ppc_componente_id,
                EquivalenciaManualDisciplinaModel.slot_ordem == slot_ordem,
            )
        )
        await self._session.commit()
        return bool(result.rowcount)

    @staticmethod
    def _mapping(row) -> EquivalenciaManual:
        model = row[0]
        item = row[1]
        component = row[2]
        return EquivalenciaManual(
            id=model.id,
            ppc_id=model.ppc_id,
            ppc_componente_id=model.ppc_componente_id,
            slot_ordem=model.slot_ordem,
            historico_item_id=item.id,
            codigo_original=item.codigo_original,
            nome_original=item.nome_original,
            carga_horaria=item.carga_horaria,
            ano=item.ano,
            semestre=item.semestre,
            situacao=item.situacao,
            media=float(item.media) if item.media is not None else None,
            tipo_componente=component.tipo_componente,
            nome_componente=row.disciplina_nome or component.nome_no_ppc,
            disciplina_codigo=component.disciplina_codigo,
        )
