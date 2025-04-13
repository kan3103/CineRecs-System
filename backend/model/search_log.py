
import datetime
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from model.user import User


class SearchLog(SQLModel, table=True):
  
  __tablename__ = 'dim_search_log'
  
  id: int = Field(default=None, primary_key=True)
  user_id: int = Field(nullable=False, foreign_key="dim_user.id")
  searched_content: str = Field(nullable=False, default='', min_length=1, max_length=1022)
  date: datetime = Field(nullable=True, default=datetime.now())
  
  user: "User" = Relationship(back_populates='search_logs')