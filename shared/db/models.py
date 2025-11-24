# models.py
from __future__ import annotations

import datetime
from datetime import datetime
from typing import List, Optional

from .base import Base

from sqlalchemy import (
    BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func, text
)
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import (
    Mapped, mapped_column, relationship
)

# ---------- СПРАВОЧНИКИ ----------

class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    users: Mapped[List["User"]] = relationship(back_populates="role", cascade="all,delete-orphan")


# ---------- ПОЛЬЗОВАТЕЛИ, ПРОФИЛИ, НАВЫКИ ----------

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("status IN ('active','blocked')", name="users_status_check"),
        UniqueConstraint("email", name="uq_users_email"),
    )

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    # 👇 ИЗМЕНЕНО: password → password_hash
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.role_id", ondelete="NO ACTION"), nullable=False
    )
    created_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status: Mapped[str] = mapped_column(Text, server_default=text("'active'"), nullable=False)
    city: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    role: Mapped["Role"] = relationship(back_populates="users")
    profile: Mapped[Optional["Profile"]] = relationship(back_populates="user", uselist=False, cascade="all,delete-orphan")
    skills: Mapped[List["Skill"]] = relationship(
        secondary="user_skills",
        back_populates="users",
        viewonly=False,
    )
    user_skills: Mapped[List["UserSkill"]] = relationship(back_populates="user", cascade="all,delete-orphan")

    # 👇 ДОБАВЛЕНО: связь с токенами
    tokens: Mapped[List["Token"]] = relationship(back_populates="user", cascade="all,delete-orphan")

    hr_vacancies: Mapped[List["Vacancy"]] = relationship(
        back_populates="hr", foreign_keys="Vacancy.hr_id", cascade="all,delete"
    )
    candidate_resumes: Mapped[List["Resume"]] = relationship(
        back_populates="candidate", foreign_keys="Resume.candidate_id", cascade="all,delete"
    )
    candidate_interviews: Mapped[List["Interview"]] = relationship(
        back_populates="candidate", foreign_keys="Interview.candidate_id", cascade="all,delete"
    )
    feedbacks_given: Mapped[List["Feedback"]] = relationship(
        back_populates="hr", foreign_keys="Feedback.hr_id", cascade="all,delete"
    )
    feedbacks_received: Mapped[List["Feedback"]] = relationship(
        back_populates="candidate", foreign_keys="Feedback.candidate_id", cascade="all,delete"
    )


# 👇 НОВАЯ МОДЕЛЬ: Token для хранения refresh токенов
class Token(Base):
    """Таблица для хранения refresh токенов пользователей"""
    __tablename__ = "tokens"
    __table_args__ = (
        Index("idx_tokens_user", "user_id"),
    )

    token_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    refresh_token: Mapped[str] = mapped_column(String(1500), unique=True, nullable=False)
    expires_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="tokens")


class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = (UniqueConstraint("user_id", name="uq_profiles_user"),)

    profile_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True
    )
    full_name: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(Text)
    photo: Mapped[Optional[str]] = mapped_column(Text)
    position: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="profile")


class Skill(Base):
    __tablename__ = "skills"

    skill_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    users: Mapped[List["User"]] = relationship(
        secondary="user_skills", back_populates="skills", viewonly=True
    )
    user_skills: Mapped[List["UserSkill"]] = relationship(back_populates="skill", cascade="all,delete-orphan")


class UserSkill(Base):
    __tablename__ = "user_skills"
    __table_args__ = (
        CheckConstraint("level BETWEEN 0 AND 10", name="user_skills_level_check"),
        UniqueConstraint("user_id", "skill_id", name="pk_user_skill"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.skill_id", ondelete="CASCADE"), primary_key=True
    )
    level: Mapped[Optional[int]] = mapped_column(Integer)

    user: Mapped["User"] = relationship(back_populates="user_skills")
    skill: Mapped["Skill"] = relationship(back_populates="user_skills")


# ---------- ВАКАНСИИ, РЕЗЮМЕ ----------

class Vacancy(Base):
    __tablename__ = "vacancies"
    __table_args__ = (
        CheckConstraint("status IN ('active','closed')", name="vacancies_status_check"),
        Index("idx_vacancies_hr", "hr_id"),
    )

    vacancy_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    hr_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    requirements: Mapped[Optional[str]] = mapped_column(Text)
    level: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status: Mapped[str] = mapped_column(Text, server_default=text("'active'"), nullable=False)

    hr: Mapped["User"] = relationship(back_populates="hr_vacancies")
    resumes: Mapped[List["Resume"]] = relationship(back_populates="vacancy")
    interviews: Mapped[List["Interview"]] = relationship(back_populates="vacancy")
    questions: Mapped[List["Question"]] = relationship(back_populates="vacancy")


class Resume(Base):
    __tablename__ = "resumes"
    __table_args__ = (
        Index("idx_resumes_metadata", "metadata_json", postgresql_using="gin"),
        Index(
            "idx_resumes_fts",
            text("to_tsvector('simple', coalesce(parsed_text, ''))"),
            postgresql_using="gin",
        ),
    )

    resume_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    vacancy_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("vacancies.vacancy_id", ondelete="SET NULL")
    )
    file_path: Mapped[Optional[str]] = mapped_column(Text)
    parsed_text: Mapped[Optional[str]] = mapped_column(Text)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    upload_date: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    candidate: Mapped["User"] = relationship(back_populates="candidate_resumes")
    vacancy: Mapped[Optional["Vacancy"]] = relationship(back_populates="resumes")


# ---------- ИНТЕРВЬЮ, ВОПРОСЫ, ОТВЕТЫ, ИТОГ ----------

class Interview(Base):
    __tablename__ = "interviews"
    __table_args__ = (
        CheckConstraint("status IN ('active','completed','error','cancelled')", name="interviews_status_check"),
        Index("idx_interviews_candidate", "candidate_id"),
        Index("idx_interviews_vacancy", "vacancy_id"),
    )

    interview_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    vacancy_id: Mapped[int] = mapped_column(
        ForeignKey("vacancies.vacancy_id", ondelete="CASCADE"), nullable=False
    )
    start_time: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_time: Mapped[Optional["datetime"]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(Text, server_default=text("'active'"), nullable=False)

    candidate: Mapped["User"] = relationship(back_populates="candidate_interviews")
    vacancy: Mapped["Vacancy"] = relationship(back_populates="interviews")
    answers: Mapped[List["Answer"]] = relationship(back_populates="interview", cascade="all,delete-orphan")
    evaluation: Mapped[Optional["Evaluation"]] = relationship(
        back_populates="interview", uselist=False, cascade="all,delete-orphan"
    )


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (
        CheckConstraint("difficulty BETWEEN 1 AND 5", name="questions_difficulty_check"),
        Index("idx_questions_vacancy", "vacancy_id"),
    )

    question_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    vacancy_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("vacancies.vacancy_id", ondelete="CASCADE")
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[Optional[int]] = mapped_column(Integer)
    topic: Mapped[Optional[str]] = mapped_column(Text)

    vacancy: Mapped[Optional["Vacancy"]] = relationship(back_populates="questions")
    answers: Mapped[List["Answer"]] = relationship(back_populates="question")


class Answer(Base):
    __tablename__ = "answers"
    __table_args__ = (
        CheckConstraint("ai_score BETWEEN 0 AND 100", name="answers_ai_score_check"),
        Index("idx_answers_interview", "interview_id"),
    )

    answer_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    interview_id: Mapped[int] = mapped_column(
        ForeignKey("interviews.interview_id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("questions.question_id", ondelete="SET NULL")
    )
    answer_text: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ai_score: Mapped[Optional[int]] = mapped_column(Integer)
    ai_comment: Mapped[Optional[str]] = mapped_column(Text)

    interview: Mapped["Interview"] = relationship(back_populates="answers")
    question: Mapped[Optional["Question"]] = relationship(back_populates="answers")


class Evaluation(Base):
    __tablename__ = "evaluations"
    __table_args__ = (
        UniqueConstraint("interview_id", name="uq_evaluations_interview"),
        CheckConstraint("total_score BETWEEN 0 AND 100", name="evaluations_total_score_check"),
    )

    evaluation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    interview_id: Mapped[int] = mapped_column(
        ForeignKey("interviews.interview_id", ondelete="CASCADE"), nullable=False, unique=True
    )
    total_score: Mapped[Optional[int]] = mapped_column(Integer)
    recommendation: Mapped[Optional[str]] = mapped_column(Text)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    interview: Mapped["Interview"] = relationship(back_populates="evaluation")


# ---------- ОТЗЫВЫ HR ----------

class Feedback(Base):
    __tablename__ = "feedbacks"
    __table_args__ = (
        CheckConstraint("result IN ('invited','rejected','on_hold')", name="feedbacks_result_check"),
    )

    feedback_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    hr_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    vacancy_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("vacancies.vacancy_id", ondelete="SET NULL")
    )
    feedback_text: Mapped[Optional[str]] = mapped_column(Text)
    result: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    candidate: Mapped["User"] = relationship(back_populates="feedbacks_received", foreign_keys=[candidate_id])
    hr: Mapped["User"] = relationship(back_populates="feedbacks_given", foreign_keys=[hr_id])
    vacancy: Mapped[Optional["Vacancy"]] = relationship()