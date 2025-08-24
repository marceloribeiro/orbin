"""
Scaffold Generator for Orbin framework.

Creates complete CRUD scaffolding: model + migration + RESTful controller for new resources.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import inflect

from .base_generator import BaseGenerator
from .model_generator import ModelGenerator
from .resource_generator import ResourceGenerator


class ScaffoldGenerator(BaseGenerator):
    """Generator for creating complete CRUD scaffolding (model + controller)."""
    
    def __init__(self, model_name: str, attributes: List[str], target_dir: Optional[str] = None):
        """
        Initialize the scaffold generator.
        
        Args:
            model_name: Name of the model to create (e.g., "User", "Post")
            attributes: List of attribute definitions (e.g., ["name:string", "email:string"])
            target_dir: Target directory (defaults to current directory)
        """
        # Initialize inflect engine for pluralization
        self.inflect_engine = inflect.engine()
        
        # Process model name
        self.model_name = self._singularize_model_name(model_name)
        self.class_name = self._to_class_name(self.model_name)
        self.controller_name = self._pluralize_model_name(self.model_name)
        
        # Store attributes for model generation
        self.attributes = attributes
        
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
        """Check if the model file already exists."""
        model_file = Path.cwd() / "app" / "models" / f"{self.model_name}.py"
        return model_file.exists()
    
    def _build_context(self) -> Dict[str, Any]:
        """Build the template context for scaffold generation."""
        return {
            "model_name": self.model_name,
            "class_name": self.class_name,
            "controller_name": self.controller_name,
            "attributes": self.attributes,
            "timestamp": datetime.now().isoformat(),
            "year": datetime.now().year,
        }
    
    def generate(self):
        """Generate the complete scaffold (model + migration + controller)."""
        print(f"Generating scaffold for '{self.class_name}' with {len(self.attributes)} attributes...")
        
        # Check if model already exists
        if self._check_model_exists():
            print(f"❌ Error: Model '{self.class_name}' already exists at app/models/{self.model_name}.py")
            print(f"💡 Tip: Use 'orbin g resource {self.class_name}' to create controller for existing model")
            return False
        
        try:
            # Step 1: Generate the model and migration
            print("📊 Generating model and migration...")
            model_generator = ModelGenerator(
                model_name=self.model_name,
                attributes=self.attributes,
                target_dir=self.target_dir
            )
            model_generator.generate()
            
            # Step 2: Generate the RESTful controller
            print("🎮 Generating RESTful controller...")
            resource_generator = ResourceGenerator(
                model_name=self.model_name,
                target_dir=self.target_dir
            )
            resource_generator.generate()
            
            print(f"✅ Successfully generated complete scaffold for '{self.class_name}'!")
            print()
            print("📁 Generated files:")
            print(f"   📊 Model: app/models/{self.model_name}.py")
            print(f"   🗄️  Migration: db/migrations/versions/[timestamp]_create_{self.controller_name}.py")
            print(f"   🎮 Controller: app/controllers/{self.controller_name}_controller.py")
            print()
            print("🛣️  Generated API endpoints:")
            print(f"   GET    /{self.controller_name}        → List all {self.controller_name}")
            print(f"   GET    /{self.controller_name}/{{id}}   → Get specific {self.model_name}")
            print(f"   POST   /{self.controller_name}        → Create new {self.model_name}")
            print(f"   PUT    /{self.controller_name}/{{id}}   → Update specific {self.model_name}")
            print(f"   DELETE /{self.controller_name}/{{id}}   → Delete specific {self.model_name}")
            print()
            print("🚀 Next steps:")
            print("   1. Run migration: orbin db-migrate")
            print("   2. Implement business logic in the controller")
            print("   3. Customize Pydantic schemas as needed")
            print("   4. Run tests: orbin test")
            print("   5. Start the server: orbin server")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating scaffold: {e}")
            raise
