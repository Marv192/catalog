from uuid import UUID

from fastapi import APIRouter, status
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.products import product_crud
from app.models import get_async_session
from app.routers.dependencies import permission_required
from app.schemas.products import ProductDB, ProductCreate, ProductUpdate, ProductInfo

products = APIRouter()


@products.post('/', status_code=status.HTTP_201_CREATED, response_model=ProductDB)
async def create_product(product_in: ProductCreate, session: AsyncSession = Depends(get_async_session),
                         _ = Depends(permission_required('product.create'))):
    return await product_crud.create(db=session, obj_in=product_in)

@products.get('/{product_id}', response_model=ProductInfo)
async def get_product(product_id: UUID, session: AsyncSession = Depends(get_async_session),
                      _ = Depends(permission_required('product.read'))):
    return await product_crud.get(db=session, product_id=product_id)

@products.get('/', response_model=list[ProductDB])
async def get_products(session: AsyncSession = Depends(get_async_session),
                       _ = Depends(permission_required('product.read'))):
    return await product_crud.get_all_products(db=session)

@products.put('/{product_id}', response_model=ProductDB)
async def update_product(product_id: UUID, product_in: ProductUpdate,
                         session: AsyncSession = Depends(get_async_session),
                         _ = Depends(permission_required('product.update'))):
    db_product = await product_crud.get(db=session, product_id=product_id)
    return await product_crud.update(db=session, db_obj=db_product, obj_in=product_in)

@products.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: UUID, session: AsyncSession = Depends(get_async_session),
                         _ = Depends(permission_required('product.delete'))):
    await product_crud.delete(db=session, product_id=product_id)
    return None