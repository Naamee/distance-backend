import sqlalchemy as sa
import sqlalchemy.orm as so
from typing import Optional
from distance_app import db
from flask_login import UserMixin  # For user session management
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64), unique=True, index=True
    )  # index to speed up lookups
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))
    alerts: so.Mapped[list["Alert"]] = so.relationship(
        back_populates="user"
    )  # ORM relationship to get all Alerts for a User

    def __repr__(self) -> str:
        return f"<User: {self.username}>"

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class MeetDate(db.Model):
    __tablename__ = "meet_date"
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
    __tablename__ = "fridge_item"
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(256), index=True
    )  # index to speed up lookups
    category: so.Mapped[str] = so.mapped_column(sa.String(128))
    entries: so.Mapped[list["FridgeEntry"]] = so.relationship(
        back_populates="item"
    )  # ORM relationship to get all FridgeEntries for a FridgeItem
    created_at = so.mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at = so.mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
    )

    def __repr__(self) -> str:
        return f"<FridgeItem: {self.name}>"


class FridgeEntry(db.Model):
    __tablename__ = "fridge_entry"
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    item_id: so.Mapped[int] = so.mapped_column(
        sa.Integer,
        sa.ForeignKey("fridge_item.id", name="fk_fridge_item_id"),
        index=True,
    )
    item: so.Mapped[FridgeItem] = so.relationship(FridgeItem, back_populates="entries")
    type: so.Mapped[str] = so.mapped_column(sa.String(16))  # 'add' or 'remove'
    quantity: so.Mapped[int] = so.mapped_column(sa.Integer)
    created_at = so.mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at = so.mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
    )

    def __repr__(self) -> str:
        return f"<FridgeEntry: {self.type} {self.quantity} of Item ID {self.item_id}>"


class Movie(db.Model):
    __tablename__ = "movie"
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
    __tablename__ = "alert"
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    task: so.Mapped[str] = so.mapped_column(sa.String(512))
    occurence: so.Mapped[str] = so.mapped_column(sa.String(256))
    status: so.Mapped[str] = so.mapped_column(sa.String(64), default="active")
    user_id: so.Mapped[int] = so.mapped_column(
        sa.Integer, sa.ForeignKey("user.id", name="fk_alert_user_id"), index=True
    )
    user: so.Mapped[User] = so.relationship(
        back_populates="alerts"
    )  # ORM relationship to acess User object from Alert
    created_at = so.mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    last_read: so.Mapped[Optional[sa.DateTime]] = so.mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<Alert: {self.task} - {self.status}>"
