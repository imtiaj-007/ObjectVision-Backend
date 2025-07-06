import sys
import pytest
from pathlib import Path


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


app_path = project_root / "app"
if app_path.exists():
    sys.path.insert(0, str(app_path))


@pytest.fixture
def app():
    """Create application fixture for testing."""
    # Import here to avoid circular imports
    from app.main import create_app
    
    app = create_app(testing=True)
    return app