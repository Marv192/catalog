from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.crud.categories import category_crud
from app.models import Category, Product
from app.schemas.categories import CategoryCreate, CategoryUpdate


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
def mock_category():
    category = MagicMock(spec=Category)
    category.id = '123e4567-e89b-12d3-a456-426614174000'
    category.name = 'Test Category'
    category.created_at = datetime.now()
    return category

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
    product.price = '1.99'
    product.category_id = '123e4567-e89b-12d3-a456-426614174000'
    product.created_at = datetime.now()
    return product

class TestCategory:
    @pytest.mark.asyncio
    async def test_create_category_success(self, mock_db_session, mock_result):
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        category_data = CategoryCreate(name="Test Category")

        result = await category_crud.create(db=mock_db_session, obj_in=category_data)

        assert result.name == category_data.name
        mock_db_session.commit.assert_called_once()
        mock_db_session.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_category_exists(self, mock_db_session, mock_result, mock_category):
        mock_result.scalar_one_or_none.return_value = mock_category
        mock_db_session.execute.return_value = mock_result

        category_data = CategoryCreate(name="Existing Category")
        mock_db_session.commit.side_effect = IntegrityError(MagicMock(), MagicMock(), MagicMock())

        with pytest.raises(HTTPException) as exc_info:
            await category_crud.create(db=mock_db_session, obj_in=category_data)

        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "Category Existing Category already exists"
        mock_db_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_category_success(self, mock_db_session, mock_category, mock_result):
        mock_result.scalar_one_or_none.return_value = mock_category

        mock_db_session.execute.return_value = mock_result

        result = await category_crud.get(db=mock_db_session, category_id=mock_category.id)

        assert result.name == mock_category.name
        assert result.id == mock_category.id
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_category_not_found(self, mock_db_session, mock_category, mock_result):
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await category_crud.get(db=mock_db_session, category_id=mock_category.id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Category not found"
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_categories_cache_hit(self, mock_db_session, mock_category):
        cached_data = [mock_category]

        with patch("app.crud.categories.get_cached", AsyncMock(return_value=cached_data)) as mock_get:
            with patch("app.crud.categories.set_cache", AsyncMock()) as mock_set:
                result = await category_crud.get_all_categories(db=mock_db_session)

        assert result == cached_data
        mock_get.assert_called_once()
        mock_set.assert_not_called()
        mock_db_session.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_all_categories_cache_miss(self, mock_db_session, mock_category, mock_result):
        with patch("app.crud.categories.get_cached", AsyncMock(return_value=None)) as mock_get:
            with patch("app.crud.categories.set_cache", AsyncMock()) as mock_set:
                mock_result.scalars.return_value.all.return_value = [mock_category]
                mock_db_session.execute.return_value = mock_result

                result = await category_crud.get_all_categories(db=mock_db_session)

        assert result[0]["name"] == mock_category.name
        mock_get.assert_called_once()
        mock_set.assert_called_once()
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_category_products_success(self, mock_db_session, mock_category, mock_result, mock_product):
        category_result = MagicMock()
        category_result.scalar_one_or_none.return_value = mock_category
        scalars_result = MagicMock()
        scalars_result.all.return_value = [mock_product]
        mock_result.scalars.return_value = scalars_result

        mock_db_session.execute.side_effect = [category_result, mock_result]

        result = await category_crud.get_category_products(db=mock_db_session, category_id=mock_category.id)

        assert len(result) == 1
        assert result[0].name == mock_product.name
        assert mock_db_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_update_category_success(self, mock_db_session, mock_category, mock_result):
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        update_data = CategoryUpdate(name="Updated name")

        updated_category = await category_crud.update(db=mock_db_session, db_obj=mock_category, obj_in=update_data)

        assert updated_category.name == "Updated name"
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_category_name_exists(self, mock_db_session, mock_category, mock_result):
        mock_result.scalar_one_or_none.return_value = mock_category
        mock_db_session.execute.return_value = mock_result
        update_data = CategoryUpdate(name="Existing name")
        mock_db_session.commit.side_effect = IntegrityError(MagicMock(), MagicMock(), MagicMock())

        with pytest.raises(HTTPException) as exc_info:
            await category_crud.update(db=mock_db_session, db_obj=mock_category, obj_in=update_data)

        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "Category Existing name already exists"
        mock_db_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_category_success(self, mock_db_session, mock_category, mock_result):
        mock_result.scalar_one_or_none.return_value = mock_category
        mock_db_session.execute.return_value = mock_result

        result = await category_crud.delete(db=mock_db_session, category_id=mock_category.id)

        assert result == mock_category
        mock_db_session.delete.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_category_not_found(self, mock_db_session, mock_result, mock_category):
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await category_crud.delete(db=mock_db_session, category_id=mock_category.id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Category not found"
        mock_db_session.commit.assert_not_called()
        mock_db_session.rollback.assert_called_once()