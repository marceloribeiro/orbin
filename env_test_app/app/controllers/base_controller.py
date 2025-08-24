"""
Base controller class for all controllers.
"""

from typing import Any, Dict
from fastapi import HTTPException, status


class BaseController:
    """Base controller with common functionality."""
    
    def __init__(self):
        """Initialize the controller."""
        pass
    
    def render_json(self, data: Any, status_code: int = 200) -> Dict[str, Any]:
        """Render JSON response."""
        return {"data": data, "status": status_code}
    
    def render_error(self, message: str, status_code: int = 400) -> HTTPException:
        """Render error response."""
        raise HTTPException(status_code=status_code, detail=message)
    
    def not_found(self, message: str = "Resource not found") -> HTTPException:
        """Render 404 error."""
        return self.render_error(message, status.HTTP_404_NOT_FOUND)
    
    def unauthorized(self, message: str = "Unauthorized") -> HTTPException:
        """Render 401 error."""
        return self.render_error(message, status.HTTP_401_UNAUTHORIZED)
    
    def forbidden(self, message: str = "Forbidden") -> HTTPException:
        """Render 403 error."""
        return self.render_error(message, status.HTTP_403_FORBIDDEN)