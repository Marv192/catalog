from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.categories import category_crud
from app.models import get_async_session
from app.routers.dependencies import permission_required
from app.schemas.categories import CategoryDB, CategoryCreate, CategoryUpdate
from app.schemas.products import ProductDB

categories = APIRouter()

@categories.post('/', status_code=status.HTTP_201_CREATED, response_model=CategoryDB)
async def create_category(category_in: CategoryCreate, session: AsyncSession = Depends(get_async_session),
                          _ = Depends(permission_required('category.create'))):
    return await category_crud.create(db=session, obj_in=category_in)

@categories.get('/{category_id}', response_model=CategoryDB)
async def get_category(category_id: UUID, session: AsyncSession = Depends(get_async_session),
                       _ = Depends(permission_required('category.read'))):
    return await category_crud.get(db=session, category_id=category_id)

@categories.get('/', response_model=list[CategoryDB])
async def get_all_categories(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_async_session),
                             _ = Depends(permission_required('category.read'))):
    return await category_crud.get_all_categories(db=session, skip=skip, limit=limit)

@categories.get('/{category_id}/products', response_model=list[ProductDB])
async def get_category_products(category_id: UUID, skip: int = 0, limit: int = 100,
                                session: AsyncSession = Depends(get_async_session),
                                _ = Depends(permission_required('category.read'))):
    products = await category_crud.get_category_products(db=session, category_id=category_id, skip=skip, limit=limit)
    return products

@categories.put('/{category_id}', response_model=CategoryDB)
async def update_category(category_id: UUID, category_in: CategoryUpdate,
                          session: AsyncSession = Depends(get_async_session),
                          _ = Depends(permission_required('category.update'))):
    db_category = await category_crud.get(db=session, category_id=category_id)
    return await category_crud.update(db=session, db_obj=db_category, obj_in=category_in)

@categories.delete('/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: UUID, session: AsyncSession = Depends(get_async_session),
                          _ = Depends(permission_required('category.delete'))):
    await category_crud.delete(db=session, category_id=category_id)
    return None


