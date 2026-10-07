"""SQLAlchemy models. Secret values are never stored; connections hold an env var name only."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32))  # admin | operator | approver
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    business_model: Mapped[str] = mapped_column(String(255), default="")
    geographies: Mapped[str] = mapped_column(Text, default="")  # comma separated
    retention_days: Mapped[int] = mapped_column(Integer, default=90)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    connections: Mapped[list["PlatformConnection"]] = relationship(back_populates="client")


class PlatformConnection(Base):
    __tablename__ = "platform_connections"
    __table_args__ = (UniqueConstraint("client_id", "platform", "account_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    platform: Mapped[str] = mapped_column(String(32))
    account_id: Mapped[str] = mapped_column(String(128))
    secret_ref: Mapped[str] = mapped_column(String(128))  # env var name only
    api_version: Mapped[str] = mapped_column(String(16), default="")
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    status: Mapped[str] = mapped_column(String(32), default="unverified")  # unverified | verified | failed
    last_tested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_test_detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    client: Mapped[Client] = relationship(back_populates="connections")


class Run(Base):
    __tablename__ = "runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    connection_id: Mapped[int | None] = mapped_column(ForeignKey("platform_connections.id"), nullable=True)
    platform: Mapped[str] = mapped_column(String(32))
    source_kind: Mapped[str] = mapped_column(String(32))  # csv | native_csv | api
    window_start: Mapped[str] = mapped_column(String(10))
    window_end: Mapped[str] = mapped_column(String(10))
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    locale: Mapped[str] = mapped_column(String(16), default="zh-CN")
    objective: Mapped[str] = mapped_column(Text, default="")
    cold_start_json: Mapped[str] = mapped_column(Text, default="{}")
    use_worker: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(32), default="queued")  # queued | running | completed | partial | failed
    completeness: Mapped[str] = mapped_column(String(16), default="partial")
    gate_decision: Mapped[str] = mapped_column(String(8), default="")
    error_detail: Mapped[str] = mapped_column(Text, default="")
    tokens_in: Mapped[int] = mapped_column(Integer, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    artifacts: Mapped[list["Artifact"]] = relationship(back_populates="run")


class Artifact(Base):
    __tablename__ = "artifacts"
    __table_args__ = (UniqueConstraint("run_id", "relative_path"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.run_id"), index=True)
    relative_path: Mapped[str] = mapped_column(String(255))
    kind: Mapped[str] = mapped_column(String(32))  # report | bundle | packet | input | summary | lifecycle
    sha256: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    run: Mapped[Run] = relationship(back_populates="artifacts")


class MutationPlan(Base):
    __tablename__ = "mutation_plans"
    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.run_id"), index=True)
    platform: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), default="draft")  # draft | approved
    payload_json: Mapped[str] = mapped_column(Text)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Approval(Base):
    __tablename__ = "approvals"
    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[str] = mapped_column(ForeignKey("mutation_plans.plan_id"), index=True)
    approver_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    decision: Mapped[str] = mapped_column(String(16))  # approved | rejected
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    target_type: Mapped[str] = mapped_column(String(32), default="")
    target_id: Mapped[str] = mapped_column(String(128), default="")
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class DeletionJob(Base):
    __tablename__ = "deletion_jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.run_id"), unique=True)
    delete_after: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(16), default="scheduled")  # scheduled | verified | exception
    verification_detail: Mapped[str] = mapped_column(Text, default="")
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
