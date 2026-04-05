# from uuid import uuid4
# from datetime import datetime
# from typing import List, TYPE_CHECKING

# from sqlalchemy import func, text, String, DateTime, Boolean, Integer, ForeignKey
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import Mapped, mapped_column, relationship

# from .base import Base


# # if TYPE_CHECKING:
# #     from .task import Task


# class RefreshToken(Base):
#     __tablename__ = 'refresh_token'

#     id: Mapped[UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid4,
#         server_default=text('gen_random_uuid()'),
#     )
#     user_id: Mapped[UUID] = mapped_column(
#         UUID(as_uuid=True), 
#         ForeignKey('user.id', ondelete='CASCADE'),
#         nullable=False,
#         index=True
#     )
#     token: Mapped[str] = mapped_column(String, unique=True, index=True)
#     expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
#     created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())