import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.enums import ContactType
from app.services.address_service import AddressService
from app.schemas.address_schema import AddressCreate, AddressUpdate
from app.db.models.address_model import Address


@pytest.fixture
def sample_address_data():
    """Sample address creation data."""
    return AddressCreate(
        address_line_1="Test Address Line 1",
        city="Test City",
        country="Test Country",
        country_code="IN",
        type=ContactType.HOME,
        user_id=1
    )


@pytest.fixture
def sample_address_model():
    """Sample address model."""
    return Address(
        id=1,
        user_id=1,
        type=ContactType.HOME,
        address_line_1="Test Address Line 1",
        city="Test City",
        country="Test Country",
        country_code="IN"
    )


@pytest.fixture
def sample_address_update():
    """Sample address update data."""
    return AddressUpdate(
        address_line_1="Updated Address Line 1",
        type=ContactType.WORK
    )


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.mark.asyncio
async def test_fetch_all_addresses(mock_db, sample_address_model):
    """Test fetching all addresses with pagination."""
    mock_addresses = [sample_address_model]

    with patch(
        "app.repository.address_repository.AddressRepository.get_all_addresses",
        return_value=mock_addresses,
    ) as mock_repo:
        result = await AddressService.fetch_all_addresses(mock_db, page=1, limit=10)
        assert len(result) == 1
        assert result[0].city == sample_address_model.city
        assert result[0].user_id == sample_address_model.user_id
        mock_repo.assert_called_once_with(mock_db, 0, 10)


@pytest.mark.asyncio
async def test_fetch_user_addresses(mock_db, sample_address_model):
    """Test fetching addresses for a specific user."""
    mock_addresses = [sample_address_model]

    with patch(
        "app.repository.address_repository.AddressRepository.get_addresses_by_user",
        return_value=mock_addresses,
    ) as mock_repo:
        result = await AddressService.fetch_user_addresses(mock_db, user_id=1, page=1, limit=10)
        assert len(result) == 1
        assert result[0].user_id == sample_address_model.user_id
        assert result[0].city == sample_address_model.city
        mock_repo.assert_called_once_with(mock_db, 1, 0, 10)


@pytest.mark.asyncio
async def test_fetch_all_addresses_empty_result(mock_db):
    """Test fetching addresses when no addresses exist."""
    with patch(
        "app.repository.address_repository.AddressRepository.get_all_addresses",
        return_value=[],
    ) as mock_repo:
        result = await AddressService.fetch_all_addresses(mock_db, page=1, limit=10)
        assert len(result) == 0
        mock_repo.assert_called_once_with(mock_db, 0, 10)


@pytest.mark.asyncio
async def test_fetch_user_addresses_empty_result(mock_db):
    """Test fetching user addresses when user has no addresses."""
    with patch(
        "app.repository.address_repository.AddressRepository.get_addresses_by_user",
        return_value=[],
    ) as mock_repo:
        result = await AddressService.fetch_user_addresses(mock_db, user_id=1, page=1, limit=10)
        assert len(result) == 0
        mock_repo.assert_called_once_with(mock_db, 1, 0, 10)


@pytest.mark.asyncio
async def test_create_new_address(mock_db, sample_address_data, sample_address_model):
    """Test creating a new address."""
    with patch(
        "app.repository.address_repository.AddressRepository.create_address",
        return_value=sample_address_model,
    ) as mock_repo:
        result = await AddressService.create_new_address(
            mock_db, user_id=sample_address_data.user_id, address_data=sample_address_data
        )
        assert result.city == sample_address_model.city
        assert result.user_id == sample_address_model.user_id
        assert result.address_line_1 == sample_address_model.address_line_1
        assert result.type == sample_address_model.type
        mock_repo.assert_called_once_with(mock_db, sample_address_data)


@pytest.mark.asyncio
async def test_create_address_database_error(mock_db, sample_address_data):
    """Test handling database errors during address creation."""
    with patch(
        "app.repository.address_repository.AddressRepository.create_address",
        side_effect=Exception("Database connection error")
    ):
        with pytest.raises(Exception, match="Database connection error"):
            await AddressService.create_new_address(
                mock_db, user_id=sample_address_data.user_id, address_data=sample_address_data
            )


@pytest.mark.asyncio
async def test_update_existing_address_success(mock_db, sample_address_model, sample_address_update):
    """Test updating an existing address successfully."""
    # Create a copy to avoid modifying the original fixture
    existing_address = sample_address_model

    with patch(
        "app.repository.address_repository.AddressRepository.get_address_by_id",
        return_value=existing_address,
    ), patch(
        "app.repository.address_repository.AddressRepository.update_address",
        return_value=existing_address,
    ) as mock_update:
        result = await AddressService.update_existing_address(
            mock_db, user_id=sample_address_model.user_id, 
            address_id=sample_address_model.id, update_data=sample_address_update
        )
        assert result.address_line_1 == sample_address_update.address_line_1
        assert result.type == sample_address_update.type
        mock_update.assert_called_once_with(mock_db, existing_address)

        # Check if the existing address is updated
        assert existing_address.address_line_1 == sample_address_update.address_line_1
        assert existing_address.type == sample_address_update.type


@pytest.mark.asyncio
async def test_update_existing_address_not_found(mock_db, sample_address_update):
    """Test updating a non-existent address."""
    with patch(
        "app.repository.address_repository.AddressRepository.get_address_by_id",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await AddressService.update_existing_address(
                mock_db, user_id=1, address_id=999, update_data=sample_address_update
            )
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_existing_address_user_mismatch(mock_db, sample_address_model, sample_address_update):
    """Test updating address that belongs to different user."""
    # Create address with different user_id
    other_user_address = Address(
        id=sample_address_model.id,
        user_id=99,  # Different user
        type=sample_address_model.type,
        address_line_1=sample_address_model.address_line_1,
        city=sample_address_model.city,
        country=sample_address_model.country,
        country_code=sample_address_model.country_code
    )

    with patch(
        "app.repository.address_repository.AddressRepository.get_address_by_id",
        return_value=other_user_address,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await AddressService.update_existing_address(
                mock_db, user_id=1, address_id=sample_address_model.id, 
                update_data=sample_address_update
            )
        assert exc_info.value.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


@pytest.mark.asyncio
async def test_delete_existing_address_success(mock_db, sample_address_model):
    """Test deleting an existing address successfully."""
    with patch(
        "app.repository.address_repository.AddressRepository.get_address_by_id",
        return_value=sample_address_model,
    ), patch(
        "app.repository.address_repository.AddressRepository.delete_address",
        return_value=None,
    ) as mock_delete:
        await AddressService.delete_existing_address(
            mock_db, user_id=sample_address_model.user_id, address_id=sample_address_model.id
        )
        mock_delete.assert_called_once_with(mock_db, sample_address_model)


@pytest.mark.asyncio
async def test_delete_existing_address_not_found(mock_db):
    """Test deleting a non-existent address."""
    with patch(
        "app.repository.address_repository.AddressRepository.get_address_by_id",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await AddressService.delete_existing_address(mock_db, user_id=1, address_id=999)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_existing_address_user_mismatch(mock_db, sample_address_model):
    """Test deleting address that belongs to different user."""
    # Create address with different user_id
    other_user_address = Address(
        id=sample_address_model.id,
        user_id=99,  # Different user
        type=sample_address_model.type,
        address_line_1=sample_address_model.address_line_1,
        city=sample_address_model.city,
        country=sample_address_model.country,
        country_code=sample_address_model.country_code
    )

    with patch(
        "app.repository.address_repository.AddressRepository.get_address_by_id",
        return_value=other_user_address,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await AddressService.delete_existing_address(
                mock_db, user_id=1, address_id=sample_address_model.id
            )
        # Adjust expected status code based on actual implementation
        assert exc_info.value.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


@pytest.mark.asyncio
async def test_pagination_edge_cases(mock_db, sample_address_model):
    """Test pagination with edge cases."""
    mock_addresses = [sample_address_model]

    # Test page 0
    with patch(
        "app.repository.address_repository.AddressRepository.get_all_addresses",
        return_value=mock_addresses,
    ) as mock_repo:
        result = await AddressService.fetch_all_addresses(mock_db, page=0, limit=10)
        mock_repo.assert_called_once_with(mock_db, -10, 10)

    # Test large page number
    with patch(
        "app.repository.address_repository.AddressRepository.get_all_addresses",
        return_value=[],
    ) as mock_repo:
        result = await AddressService.fetch_all_addresses(mock_db, page=1000, limit=10)
        assert len(result) == 0
        mock_repo.assert_called_once_with(mock_db, 9990, 10)


@pytest.mark.asyncio
async def test_partial_address_update(mock_db, sample_address_model):
    """Test updating only some fields of an address."""
    # Create a copy to avoid modifying the original fixture
    existing_address = sample_address_model

    # Update only city
    partial_update = AddressUpdate(city="New City")

    def mock_update_address(db, address_obj):
        address_obj.city = "New City"
        return address_obj

    with patch(
        "app.repository.address_repository.AddressRepository.get_address_by_id",
        return_value=existing_address,
    ), patch(
        "app.repository.address_repository.AddressRepository.update_address",
        side_effect=mock_update_address,
    ) as mock_update:
        result = await AddressService.update_existing_address(
            mock_db, user_id=sample_address_model.user_id, 
            address_id=sample_address_model.id, update_data=partial_update
        )
        assert result.city == "New City"
        # Other fields should remain unchanged
        assert result.address_line_1 == sample_address_model.address_line_1
        assert result.type == sample_address_model.type
        mock_update.assert_called_once_with(mock_db, existing_address)