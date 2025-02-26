GET_ALL_ADDRESSES_DESCRIPTION = """
Retrieves all addresses stored in the system.

### Parameters:
- **page (int):** The page number for pagination.
- **limit (int, optional, default=10):** The number of addresses per page.
- **db (AsyncSession):** Database session for fetching addresses.
- **auth_obj (Optional[Dict[str, Any]]):** The authenticated user object.

### Returns:
- **List[AddressResponse]:** A list of address records.

### Raises:
- `HTTPException(401)`: If the user is not authenticated.
- `HTTPException(403)`: If the user does not have permission.

### Flow:
1. Checks authentication status.
2. Fetches paginated addresses from the database.
3. Returns the address list.

### Example Success Response:
```json
[
    {
        "id": 1,
        "user_id": 10,
        "street": "123 Main St",
        "city": "Springfield",
        "state": "IL",
        "country": "USA",
        "zip_code": "62704"
    }
]
```

### Example Error Response:
```json
{
    "detail": "Unauthorized"
}
```
"""

GET_USER_ADDRESSES_DESCRIPTION = """
Retrieves all addresses associated with a specific user.

### Parameters:
- **user_id (int):** The ID of the user whose addresses are to be retrieved.
- **page (int):** The page number for pagination.
- **limit (int, optional, default=10):** The number of addresses per page.
- **db (AsyncSession):** Database session for fetching addresses.
- **auth_obj (Optional[Dict[str, Any]]):** The authenticated user object.

### Returns:
- **List[AddressResponse]:** A list of addresses belonging to the specified user.

### Raises:
- `HTTPException(401)`: If the user is not authenticated.
- `HTTPException(404)`: If the user has no addresses.

### Flow:
1. Verifies authentication.
2. Retrieves paginated addresses for the specified user.
3. Returns the user’s address list.

### Example Success Response:
```json
[
    {
        "id": 2,
        "user_id": 5,
        "street": "456 Elm St",
        "city": "New York",
        "state": "NY",
        "country": "USA",
        "zip_code": "10001"
    }
]
```

### Example Error Response:
```json
{
    "detail": "No addresses found for this user"
}
```
"""

CREATE_ADDRESS_DESCRIPTION = """
Creates a new address for the authenticated user.

### Parameters:
- **address_body (AddressCreate):** Address details including street, city, state, country, and zip code.
- **db (AsyncSession):** Database session for creating an address.
- **auth_obj (Optional[Dict[str, Any]]):** The authenticated user object.

### Returns:
- **AddressResponse:** The created address.

### Raises:
- `HTTPException(401)`: If the user is not authenticated.
- `HTTPException(400)`: If address data is invalid.

### Flow:
1. Validates authentication.
2. Saves the new address in the database.
3. Returns the created address.

### Example Success Response:
```json
{
    "id": 3,
    "user_id": 7,
    "street": "789 Pine St",
    "city": "Los Angeles",
    "state": "CA",
    "country": "USA",
    "zip_code": "90001"
}
```

### Example Error Response:
```json
{
    "detail": "Invalid address data"
}
```
"""

UPDATE_ADDRESS_DESCRIPTION = """
Updates an existing address for the authenticated user.

### Parameters:
- **address_id (int):** The ID of the address to update.
- **address_body (AddressUpdate):** The updated address details.
- **db (AsyncSession):** Database session for updating the address.
- **auth_obj (Optional[Dict[str, Any]]):** The authenticated user object.

### Returns:
- **AddressResponse:** The updated address.

### Raises:
- `HTTPException(401)`: If the user is not authenticated.
- `HTTPException(404)`: If the address does not exist or does not belong to the user.

### Flow:
1. Checks authentication.
2. Finds the address by `address_id`.
3. Updates and returns the address.

### Example Success Response:
```json
{
    "id": 3,
    "user_id": 7,
    "street": "Updated Pine St",
    "city": "Los Angeles",
    "state": "CA",
    "country": "USA",
    "zip_code": "90002"
}
```

### Example Error Response:
```json
{
    "detail": "Address not found"
}
```
"""

DELETE_ADDRESS_DESCRIPTION = """
Deletes an existing address for the authenticated user.

### Parameters:
- **address_id (int):** The ID of the address to delete.
- **db (AsyncSession):** Database session for deleting the address.
- **auth_obj (Optional[Dict[str, Any]]):** The authenticated user object.

### Returns:
- **Message:** Confirmation of deletion.

### Raises:
- `HTTPException(401)`: If the user is not authenticated.
- `HTTPException(404)`: If the address does not exist or does not belong to the user.

### Flow:
1. Checks authentication.
2. Validates the address ownership.
3. Deletes the address from the database.
4. Returns a confirmation message.

### Example Success Response:
```json
{
    "detail": "Address deleted successfully"
}
```

### Example Error Response:
```json
{
    "detail": "Address not found"
}
```
"""

