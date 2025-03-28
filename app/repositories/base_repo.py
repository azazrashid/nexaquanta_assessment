import logging
from typing import TypeVar, Generic, Type, List, Any, Dict

from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException

T = TypeVar('T')
PydanticT = TypeVar('PydanticT', bound=BaseModel)

logger = logging.getLogger(__name__)


class BaseRepo(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
    
    async def get_by_id(self, db: AsyncSession, id_: int) -> T:
        result = await db.execute(select(self.model).where(self.model.id == id_))
        instance = result.scalar_one_or_none()
        if not instance:
            raise NotFoundException(f"{self.model.__name__} with id {id_} not found")
        return instance

    
    async def get_all(self, db: AsyncSession) -> List[T]:
        result = await db.execute(select(self.model))
        return result.scalars().all()

    
    async def create(self, db: AsyncSession, **kwargs) -> T:
        obj = self.model(**kwargs)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    
    async def update(self, db: AsyncSession, id_: int,
                     update_data: Dict[str, Any]) -> T:
        instance = await self.get_by_id(db, id_)
        for key, value in update_data.items():
            setattr(instance, key, value)
        await db.flush()
        await db.refresh(instance)
        return instance

    
    async def delete(self, db: AsyncSession, **kwargs) -> None:
        if 'id' in kwargs:
            obj = await self.get_by_id(db, kwargs['id'])
            await db.delete(obj)
        else:
            stmt = delete(self.model)
            for key, value in kwargs.items():
                stmt = stmt.filter(getattr(self.model, key) == value)
            await db.execute(stmt)
        await db.flush()