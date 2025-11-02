import sqlalchemy as sa
import sqlalchemy.orm as so
from typing import Optional
from distance_app import db, login
from flask_login import UserMixin # For user session management
from werkzeug.security import generate_password_hash, check_password_hash

# Load user for Flask-Login session management
@login.user_loader
def load_user(id: int):
    return db.session.get(User, int(id))


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64), unique=True, index=True
    )  # index to speed up lookups
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))
    alerts: so.Mapped[list["Alert"]] = so.relationship(back_populates="user") # ORM relationship to get all Alerts for a User

    def __repr__(self) -> str:
        return f"<User: {self.username}>"

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class MeetDate(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    date: so.Mapped[str] = so.mapped_column(
        sa.String(10)
    )  # Format: 'YYYY-MM-DD' || stored as string for simplicity
    created_at = so.mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at = so.mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
    )

    def __repr__(self) -> str:
        return f"<MeetDate: {self.date}>"


class FridgeItem(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(256), index=True
    )  # index to speed up lookups
    type: so.Mapped[str] = so.mapped_column(sa.String(64), default="add")
    category: so.Mapped[str] = so.mapped_column(sa.String(128))
    quantity: so.Mapped[int] = so.mapped_column(sa.Integer)
    created_at = so.mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at = so.mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
    )

    def __repr__(self) -> str:
        return f"<FridgeItem: {self.name} ({self.quantity})>"


class Movie(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(256), index=True
    )  # index to speed up lookups
    created_at = so.mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at = so.mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
    )

    def __repr__(self) -> str:
        return f"<Movie: {self.name}>"


class Alert(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    task: so.Mapped[str] = so.mapped_column(sa.String(512))
    occurence: so.Mapped[str] = so.mapped_column(sa.String(256))
    status: so.Mapped[str] = so.mapped_column(sa.String(64), default="active")
    user_id: so.Mapped[int] = so.mapped_column(
        sa.Integer, sa.ForeignKey("user.id", name="fk_alert_user_id"), index=True
    )
    user: so.Mapped[User] = so.relationship(back_populates="alerts") # ORM relationship to acess User object from Alert
    created_at = so.mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    last_read: so.Mapped[Optional[sa.DateTime]] = so.mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<Alert: {self.task} - {self.status}>"
