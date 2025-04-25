
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
  from model.credit import Credit



class Person(SQLModel, table=True):
  
  __tablename__ = 'dim_person' # type: ignore
  
  id: int = Field(nullable=False, primary_key=True)
  name: str = Field(nullable=False, min_length=1, max_length=255)
  stage_name: Optional[str] = Field(nullable=True, min_length=1, max_length=255)
  profile: Optional[str] = Field(nullable=True, min_length=1, max_length=1022, default='')
  gender: int = Field(nullable=False, ge=1, le=2)
  known_for_dept: Optional[str] = Field(nullable=True, min_length=1, max_length=255)
  
  credits: list["Credit"] = Relationship(back_populates='person')

  