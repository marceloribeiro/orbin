"""
Resource Generator for Orbin framework.

Creates RESTful controllers for existing models with standard CRUD operations.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import inflect

from .base_generator import BaseGenerator
from .controller_generator import ControllerGenerator


class ResourceGenerator(BaseGenerator):
    """Generator for creating RESTful controllers for existing models."""
    
    def __init__(self, model_name: str, target_dir: Optional[str] = None):
        """
        Initialize the resource generator.
        
        Args:
            model_name: Name of the existing model (e.g., "User", "Post")
            target_dir: Target directory (defaults to current directory)
        """
        # Initialize inflect engine for pluralization
        self.inflect_engine = inflect.engine()
        
        # Process model name
        self.model_name = self._singularize_model_name(model_name)
        self.class_name = self._to_class_name(self.model_name)
        self.controller_name = self._pluralize_model_name(self.model_name)
        
        # Standard RESTful actions
        self.actions = ["index", "show", "create", "update", "destroy"]
        
        super().__init__(self.model_name, target_dir)
    
    def _singularize_model_name(self, name: str) -> str:
        """Convert model name to singular form."""
        # Remove non-alphanumeric characters except underscores
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '', name.lower())
        
        # Singularize using inflect
        singular = self.inflect_engine.singular_noun(clean_name)
        return singular if singular else clean_name
    
    def _pluralize_model_name(self, name: str) -> str:
        """Convert model name to plural form for controller name."""
        return self.inflect_engine.plural(name)
    
    def _to_class_name(self, name: str) -> str:
        """Convert model name to PascalCase class name."""
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def _check_model_exists(self) -> bool:
        """Check if the model file exists."""
        model_file = Path.cwd() / "app" / "models" / f"{self.model_name}.py"
        return model_file.exists()
    
    def _build_context(self) -> Dict[str, Any]:
        """Build the template context for resource generation."""
        return {
            "model_name": self.model_name,
            "class_name": self.class_name,
            "controller_name": self.controller_name,
            "actions": self.actions,
            "timestamp": datetime.now().isoformat(),
            "year": datetime.now().year,
        }
    
    def generate(self):
        """Generate the RESTful controller for the existing model."""
        print(f"Generating RESTful controller for '{self.class_name}' model...")
        
        # Check if model exists
        if not self._check_model_exists():
            print(f"❌ Error: Model '{self.class_name}' not found at app/models/{self.model_name}.py")
            print(f"💡 Tip: Use 'orbin g scaffold {self.class_name}' to create both model and controller")
            return False
        
        try:
            # Extract model attributes for better test generation
            model_attributes = self._extract_model_attributes()
            
            # Use the controller generator to create the RESTful controller
            controller_generator = ControllerGenerator(
                controller_name=self.controller_name,
                actions=self.actions,
                target_dir=self.target_dir
            )
            
            # Update context with model attributes for test generation
            controller_generator.context["model_attributes"] = model_attributes
            
            # Generate the controller using the existing generator
            controller_generator.generate()
            
            # Update the generated controller to be model-aware
            self._update_controller_for_model()
            
            print(f"✅ Successfully generated RESTful controller for '{self.class_name}' model!")
            print()
            print("🚀 Next steps:")
            print("   1. Implement business logic in the controller")
            print("   2. Customize Pydantic schemas as needed")
            print("   3. Run tests: orbin test")
            print("   4. Start the server: orbin server")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating resource: {e}")
            raise
    
    def _update_controller_for_model(self):
        """Update the generated controller to include model-specific imports and schemas."""
        controller_file = Path.cwd() / "app" / "controllers" / f"{self.controller_name}_controller.py"
        
        if not controller_file.exists():
            return
        
        content = controller_file.read_text()
        
        # Add model import
        model_import = f"from app.models.{self.model_name} import {self.class_name}"
        
        # Find the config.database import line and add model import after it
        if "from config.database import get_db" in content and model_import not in content:
            content = content.replace(
                "from config.database import get_db",
                f"from config.database import get_db\n{model_import}"
            )
        
        # Update schema class names to match the model
        content = content.replace(
            f"class {self.controller_name.title()}Base(BaseModel):",
            f"class {self.class_name}Base(BaseModel):"
        )
        content = content.replace(
            f"class {self.controller_name.title()}Create({self.controller_name.title()}Base):",
            f"class {self.class_name}Create({self.class_name}Base):"
        )
        content = content.replace(
            f"class {self.controller_name.title()}Update({self.controller_name.title()}Base):",
            f"class {self.class_name}Update({self.class_name}Base):"
        )
        content = content.replace(
            f"class {self.controller_name.title()}Response({self.controller_name.title()}Base):",
            f"class {self.class_name}Response({self.class_name}Base):"
        )
        
        # Update TODO comments with actual model references
        content = content.replace(
            f"# TODO: Implement logic to fetch all {self.controller_name}",
            f"# TODO: Implement logic to fetch all {self.controller_name}\n        # Example:\n        # {self.controller_name} = db.query({self.class_name}).all()\n        # return {self.controller_name}"
        )
        
        content = content.replace(
            f"# TODO: Implement logic to fetch {self.controller_name[:-1] if self.controller_name.endswith('s') else self.controller_name} by ID",
            f"# TODO: Implement logic to fetch {self.model_name} by ID\n        # Example:\n        # {self.model_name} = db.query({self.class_name}).filter({self.class_name}.id == id).first()\n        # if not {self.model_name}:\n        #     raise HTTPException(status_code=404, detail=\"{self.class_name} not found\")\n        # return {self.model_name}"
        )
        
        content = content.replace(
            f"# TODO: Implement logic to create new {self.controller_name[:-1] if self.controller_name.endswith('s') else self.controller_name}",
            f"# TODO: Implement logic to create new {self.model_name}\n        # Example:\n        # {self.model_name} = {self.class_name}(**{self.model_name}_data.dict())\n        # db.add({self.model_name})\n        # db.commit()\n        # db.refresh({self.model_name})\n        # return {self.model_name}"
        )
        
        content = content.replace(
            f"# TODO: Implement logic to update {self.controller_name[:-1] if self.controller_name.endswith('s') else self.controller_name}",
            f"# TODO: Implement logic to update {self.model_name}\n        # Example:\n        # {self.model_name} = db.query({self.class_name}).filter({self.class_name}.id == id).first()\n        # if not {self.model_name}:\n        #     raise HTTPException(status_code=404, detail=\"{self.class_name} not found\")\n        # for key, value in {self.model_name}_data.dict(exclude_unset=True).items():\n        #     setattr({self.model_name}, key, value)\n        # db.commit()\n        # return {self.model_name}"
        )
        
        content = content.replace(
            f"# TODO: Implement logic to delete {self.controller_name[:-1] if self.controller_name.endswith('s') else self.controller_name}",
            f"# TODO: Implement logic to delete {self.model_name}\n        # Example:\n        # {self.model_name} = db.query({self.class_name}).filter({self.class_name}.id == id).first()\n        # if not {self.model_name}:\n        #     raise HTTPException(status_code=404, detail=\"{self.class_name} not found\")\n        # db.delete({self.model_name})\n        # db.commit()\n        # return {{\"message\": \"{self.class_name} deleted successfully\"}}"
        )
        
        # Update parameter names in function signatures
        content = content.replace(
            f"{self.controller_name[:-1] if self.controller_name.endswith('s') else self.controller_name}_data: {self.class_name}Create",
            f"{self.model_name}_data: {self.class_name}Create"
        )
        content = content.replace(
            f"{self.controller_name[:-1] if self.controller_name.endswith('s') else self.controller_name}_data: {self.class_name}Update",
            f"{self.model_name}_data: {self.class_name}Update"
        )
        
        # Fix return type annotations to use correct schema names
        old_response_name = self.controller_name.title().replace('s', '') + 'Response'  # ProductsResponse
        new_response_name = f"{self.class_name}Response"  # ProductResponse
        
        content = content.replace(f"-> List[{old_response_name}]:", f"-> List[{new_response_name}]:")
        content = content.replace(f"-> {old_response_name}:", f"-> {new_response_name}:")
        
        # Fix parameter type annotations
        old_create_name = self.controller_name.title().replace('s', '') + 'Create'
        old_update_name = self.controller_name.title().replace('s', '') + 'Update'
        
        content = content.replace(f": {old_create_name},", f": {self.class_name}Create,")
        content = content.replace(f": {old_update_name},", f": {self.class_name}Update,")
        
        # Write the updated content
        controller_file.write_text(content)
        print(f"📄 Updated controller with {self.class_name} model integration")
    
    def _extract_model_attributes(self):
        """Extract attributes from the existing model file for test generation."""
        model_file = Path.cwd() / "app" / "models" / f"{self.model_name}.py"
        
        if not model_file.exists():
            return []
        
        try:
            content = model_file.read_text()
            attributes = []
            
            # Simple regex to find Column definitions
            import re
            column_pattern = r'(\w+)\s*=\s*Column\((\w+)(?:\([^)]*\))?\)'
            matches = re.findall(column_pattern, content)
            
            for match in matches:
                attr_name, attr_type = match
                # Skip standard fields
                if attr_name in ['id', 'created_at', 'updated_at']:
                    continue
                
                # Generate test values based on type
                test_value = self._get_test_value_for_type(attr_type)
                
                attributes.append({
                    'name': attr_name,
                    'type': attr_type,
                    'test_value': test_value
                })
            
            return attributes
        except Exception as e:
            print(f"⚠️  Warning: Could not extract model attributes: {e}")
            return []
    
    def _get_test_value_for_type(self, attr_type: str) -> str:
        """Get appropriate test value for attribute type."""
        type_mapping = {
            'String': '"test_string"',
            'Integer': '123',
            'Float': '12.34',
            'Boolean': 'True',
            'Text': '"test_text_content"',
            'DateTime': '"2023-01-01T00:00:00"',
            'Date': '"2023-01-01"',
            'Time': '"12:00:00"',
            'JSON': '{"key": "value"}',
            'Numeric': '99.99',
        }
        
        return type_mapping.get(attr_type, '"test_value"')
