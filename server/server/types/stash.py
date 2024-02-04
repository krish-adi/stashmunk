from typing import Optional
from pydantic import validator
from pydantic.main import BaseModel


class Stash(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = 'my_stash_one'

    @validator('id', always=True)
    def check_id_or_name(cls, id, values):
        if not id and not values.get('name'):
            raise ValueError(
                'Either id or name is required for identifying a stash.')
        return id
