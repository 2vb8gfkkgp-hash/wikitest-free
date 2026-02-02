from datetime import datetime
from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    topic = Column(String(255), nullable=False)
    audience = Column(String(255), nullable=True)
    deadline = Column(Date, nullable=True)
    owner_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    draft = relationship("Draft", back_populates="project", uselist=False, cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="project", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="project", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="project", cascade="all, delete-orphan")
    checklist = relationship("EthicsChecklist", back_populates="project", uselist=False, cascade="all, delete-orphan")


class Draft(Base):
    __tablename__ = "drafts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    content = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="draft")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    url = Column(String(500), nullable=False)
    title = Column(String(255), nullable=False)
    publisher = Column(String(255), nullable=True)
    author = Column(String(255), nullable=True)
    published_date = Column(Date, nullable=True)
    source_type = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    excerpts = Column(Text, nullable=True)
    is_primary = Column(Boolean, default=False)
    is_historical = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="sources")
    matches = relationship("ClaimSourceMatch", back_populates="source", cascade="all, delete-orphan")


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    person = Column(String(255), nullable=False)
    role = Column(String(255), nullable=True)
    interview_date = Column(Date, nullable=True)
    transcript = Column(Text, nullable=True)
    extracted_quotes = Column(Text, nullable=True)

    project = relationship("Project", back_populates="interviews")
    matches = relationship("ClaimSourceMatch", back_populates="interview", cascade="all, delete-orphan")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    text = Column(Text, nullable=False)
    category = Column(String(50), default="claim")
    claim_type = Column(String(50), nullable=True)
    status = Column(String(50), default="needs_review")
    confidence = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)

    project = relationship("Project", back_populates="claims")
    matches = relationship("ClaimSourceMatch", back_populates="claim", cascade="all, delete-orphan")


class ClaimSourceMatch(Base):
    __tablename__ = "claim_source_matches"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=True)
    match_score = Column(Float, default=0.0)
    overlap = Column(Text, nullable=True)
    needs_review = Column(Boolean, default=False)

    claim = relationship("Claim", back_populates="matches")
    source = relationship("Source", back_populates="matches")
    interview = relationship("Interview", back_populates="matches")


class EthicsChecklist(Base):
    __tablename__ = "ethics_checklists"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    right_of_reply = Column(Boolean, default=False)
    separate_fact_opinion = Column(Boolean, default=False)
    avoid_sensational = Column(Boolean, default=False)
    quote_integrity = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="checklist")
