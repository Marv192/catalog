from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

from app.crud.products import product_crud
from app.models import Product
from app.schemas.products import ProductCreate, ProductUpdate


@pytest.fixture()
def mock_db_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.scalar = AsyncMock()
    return session

@pytest.fixture()
def mock_result():
    result = MagicMock()

    return result

@pytest.fixture()
def mock_product():
    product = MagicMock(spec=Product)
    product.id = '123e4567-e89b-12d3-a456-426614174001'
    product.name = 'Test Product Name'
    product.description = 'Test Description'
    product.price = Decimal('1.99')
    product.category_id = UUID('123e4567-e89b-12d3-a456-426614174000')
    product.created_at = datetime.now()
    return product

class TestProduct:
    @pytest.mark.asyncio
    async def test_create_product_success(self, mock_db_session, mock_product, mock_result):
        product_data = ProductCreate(name=mock_product.name, description=mock_product.description,
                                     price=mock_product.price, category_id=mock_product.category_id)
        mock_result.scalar_one_or_none.return_value = True
        mock_db_session.execute.return_value = mock_result

        result = await product_crud.create(db=mock_db_session, obj_in=product_data)

        assert result.name == mock_product.name
        assert result.description == mock_product.description
        assert result.price == mock_product.price
        assert result.category_id == mock_product.category_id
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_product_category_not_found(self, mock_db_session, mock_product, mock_result):
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        product_data = ProductCreate(name=mock_product.name, description=mock_product.description,
                                     price=mock_product.price, category_id=mock_product.category_id)

        with pytest.raises(HTTPException) as exc_info:
            await product_crud.create(db=mock_db_session, obj_in=product_data)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == f"Category 123e4567-e89b-12d3-a456-426614174000 does not exist"
        mock_db_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_product_success(self, mock_db_session, mock_product, mock_result):
        mock_result.scalar_one_or_none.return_value = mock_product
        mock_db_session.execute.return_value = mock_result

        result = await product_crud.get(db=mock_db_session, product_id=mock_product.id)

        assert result.id == mock_product.id
        assert result.name == mock_product.name
        assert result.description == mock_product.description
        assert result.price == mock_product.price
        assert result.category_id == mock_product.category_id
        assert result.created_at == mock_product.created_at
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_product_not_found(self, mock_db_session, mock_product, mock_result):
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await product_crud.get(db=mock_db_session, product_id=mock_product.id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == f"Product not found"
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_products_success(self, mock_db_session, mock_product, mock_result):
        mock_result.scalars.return_value.all.return_value = [mock_product]
        mock_db_session.execute.return_value = mock_result

        result = await product_crud.get_all_products(db=mock_db_session)

        assert len(result) == 1
        assert result[0].id == mock_product.id
        assert result[0].name == mock_product.name
        assert result[0].description == mock_product.description
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_product_success(self, mock_db_session, mock_product, mock_result):
        update_data = ProductUpdate(name="New name", description="New description")

        updated_product = await product_crud.update(db=mock_db_session, db_obj=mock_product, obj_in=update_data)

        assert updated_product.name == "New name"
        assert updated_product.description == "New description"
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_product_wrong_category_id(self, mock_db_session, mock_product, mock_result):
        new_category_id = uuid4()
        update_data = ProductUpdate(category_id=new_category_id)
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await product_crud.update(db=mock_db_session, db_obj=mock_product, obj_in=update_data)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == f"Category {new_category_id} does not exist"
        mock_db_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_product_event_payload(self, mock_db_session, mock_product, mock_result):
        update_data = ProductUpdate(name="New name", description="New description")

        with patch("app.crud.products.send_product_updated_event") as mock_send_event:
            await product_crud.update(db=mock_db_session, db_obj=mock_product, obj_in=update_data)

        call_args = mock_send_event.call_args
        assert call_args.kwargs["old_values"]["name"] == 'Test Product Name'
        assert call_args.kwargs["old_values"]["description"] == "Test Description"
        assert call_args.kwargs["new_values"]["name"] == "New name"
        assert call_args.kwargs["new_values"]["description"] == "New description"

    @pytest.mark.asyncio
    async def test_delete_product_success(self, mock_db_session, mock_product, mock_result):
        mock_result.scalar_one_or_none.return_value = mock_product
        mock_db_session.execute.return_value = mock_result

        result = await product_crud.delete(db=mock_db_session, product_id=mock_product.id)

        assert result == mock_product
        mock_db_session.delete.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_product_not_found(self, mock_db_session, mock_product, mock_result):
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await product_crud.delete(db=mock_db_session, product_id=mock_product.id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Product not found"
        mock_db_session.commit.assert_not_called()

