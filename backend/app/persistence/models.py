"""Modelos SQLAlchemy: hierarquia Planta/Área/Máquina/Ponto e leituras (FR-011, FR-012, FR-013)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Planta(Base):
    __tablename__ = "plantas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String, nullable=False)

    areas: Mapped[list[Area]] = relationship(back_populates="planta")


class Area(Base):
    __tablename__ = "areas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    planta_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("plantas.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String, nullable=False)

    planta: Mapped[Planta] = relationship(back_populates="areas")
    maquinas: Mapped[list[Maquina]] = relationship(back_populates="area")


class Maquina(Base):
    __tablename__ = "maquinas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    area_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("areas.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String, nullable=False)

    area: Mapped[Area] = relationship(back_populates="maquinas")
    pontos: Mapped[list[Ponto]] = relationship(back_populates="maquina")


class Ponto(Base):
    __tablename__ = "pontos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    maquina_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("maquinas.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    # FK circular resolvida com use_alter (leituras_persistidas referencia pontos.id).
    ultima_leitura_persistida_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("leituras_persistidas.id", use_alter=True, name="fk_ponto_ultima_leitura"),
        nullable=True,
    )

    maquina: Mapped[Maquina] = relationship(back_populates="pontos")


class LeituraPersistida(Base):
    __tablename__ = "leituras_persistidas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ponto_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pontos.id"), nullable=False)
    timestamp_original: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    rotacao: Mapped[float] = mapped_column(Float, nullable=False)
    picos_r3: Mapped[list] = mapped_column(JSONB, nullable=False)
    rms_total: Mapped[float] = mapped_column(Float, nullable=False)
    rms_ruido: Mapped[float] = mapped_column(Float, nullable=False)
    rms_picos: Mapped[float] = mapped_column(Float, nullable=False)
    valor_dc: Mapped[float] = mapped_column(Float, nullable=False)
    nivel_alerta: Mapped[float | None] = mapped_column(Float, nullable=True)
    nivel_shutdown: Mapped[float | None] = mapped_column(Float, nullable=True)


class LeituraTrash(Base):
    __tablename__ = "leituras_trash"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ponto_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pontos.id"), nullable=False)
    timestamp_original: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    rotacao: Mapped[float] = mapped_column(Float, nullable=False)
    picos_r3: Mapped[list] = mapped_column(JSONB, nullable=False)
    rms_total: Mapped[float] = mapped_column(Float, nullable=False)
    rms_ruido: Mapped[float] = mapped_column(Float, nullable=False)
    rms_picos: Mapped[float] = mapped_column(Float, nullable=False)
    valor_dc: Mapped[float] = mapped_column(Float, nullable=False)
    motivo_descarte: Mapped[str] = mapped_column(String, nullable=False)


class SnapshotDefeito(Base):
    __tablename__ = "snapshots_defeito"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    leitura_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    leitura_tipo: Mapped[str] = mapped_column(String, nullable=False)  # 'persistida' | 'trash'
    sensor_id: Mapped[str] = mapped_column(String, nullable=False)
    tipo_defeito: Mapped[str] = mapped_column(String, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
