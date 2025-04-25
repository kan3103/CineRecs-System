

from typing import Optional
from pydantic import BaseModel, ConfigDict


class PersonCreate(BaseModel):
  name: str
  stage_name: Optional[str]
  profile: Optional[str]
  gender: int
  known_for_dept: Optional[str]

class PersonUpdate(BaseModel):
  stage_name: Optional[str]
  profile: Optional[str]
  gender: int
  known_for_dept: Optional[str]

class PersonResponse(BaseModel):
  id: int
  name: str
  stage_name: Optional[str]
  profile: Optional[str]
  gender: int
  known_for_dept: Optional[str]
  
  model_config = ConfigDict(from_attributes=True)
  