"""
Model Generator for Orbin framework.

Creates SQLAlchemy models and associated migrations.
"""

import re
import uuid
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import inflect

from .base_generator import BaseGenerator


class ModelGenerator(BaseGenerator):
    """Generator for creating SQLAlchemy models and migrations."""
    
    def __init__(self, model_name: str, attributes: List[str], target_dir: Optional[str] = None):
        """
        Initialize the model generator.
        
        Args:
            model_name: Name of the model (singular or plural)
            attributes: List of attribute definitions (e.g., ["name:string", "age:integer"])
            target_dir: Target directory (defaults to current directory)
        """
        # Initialize inflect engine for pluralization
        self.inflect_engine = inflect.engine()
        
        # Process model name to ensure singular form
        self.model_name = self._singularize_model_name(model_name)
        self.table_name = self._pluralize_model_name(self.model_name)
        self.class_name = self._to_class_name(self.model_name)
        
        # Parse attributes
        self.attributes = self._parse_attributes(attributes)
        
        # Generate timestamp for migration
        self.migration_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.migration_name = f"create_{self.table_name}"
        
        super().__init__(self.model_name, target_dir)
    
    def _singularize_model_name(self, name: str) -> str:
        """Convert model name to singular form."""
        # Remove non-alphanumeric characters except underscores
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '', name.lower())
        
        # Singularize using inflect
        singular = self.inflect_engine.singular_noun(clean_name)
        return singular if singular else clean_name
    
    def _pluralize_model_name(self, name: str) -> str:
        """Convert model name to plural form for table name."""
        return self.inflect_engine.plural(name)
    
    def _to_class_name(self, name: str) -> str:
        """Convert model name to PascalCase class name."""
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def _parse_attributes(self, attributes: List[str]) -> List[Dict[str, str]]:
        """Parse attribute definitions into structured format."""
        parsed = []
        
        for attr in attributes:
            if ':' not in attr:
                continue
                
            parts = attr.split(':')
            if len(parts) != 2:
                continue
                
            attr_name, attr_type = parts[0].strip(), parts[1].strip()
            
            # Map common types to SQLAlchemy types
            sqlalchemy_type = self._map_attribute_type(attr_type)
            
            parsed.append({
                'name': attr_name,
                'type': attr_type,
                'sqlalchemy_type': sqlalchemy_type,
                'nullable': True  # Default to nullable, can be extended later
            })
        
        return parsed
    
    def _map_attribute_type(self, attr_type: str) -> str:
        """Map attribute type to SQLAlchemy type."""
        type_mapping = {
            'string': 'String(255)',
            'str': 'String(255)',
            'text': 'Text',
            'integer': 'Integer',
            'int': 'Integer',
            'float': 'Float',
            'decimal': 'Numeric(10, 2)',
            'boolean': 'Boolean',
            'bool': 'Boolean',
            'datetime': 'DateTime(timezone=True)',
            'date': 'Date',
            'time': 'Time',
            'uuid': 'UUID(as_uuid=True)',
            'json': 'JSON',
        }
        
        return type_mapping.get(attr_type.lower(), 'String(255)')
    
    def _get_migration_head(self) -> Optional[str]:
        """Get the current migration head revision ID."""
        try:
            # Check if alembic is available and properly configured
            result = subprocess.run(
                ["alembic", "current"],
                cwd=Path.cwd(),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Extract revision ID from output like "20250824120512 (head)"
                output = result.stdout.strip()
                if output and output != "":
                    # Handle case where there's a revision
                    revision_match = re.search(r'^([a-f0-9]+)', output)
                    if revision_match:
                        return revision_match.group(1)
            
            # If no current revision, check for existing migration files
            migrations_dir = Path.cwd() / "db" / "migrations" / "versions"
            if migrations_dir.exists():
                migration_files = sorted([f for f in migrations_dir.glob("*.py") if f.name != "__init__.py"])
                if migration_files:
                    # Get the latest migration file and extract its revision ID
                    latest_file = migration_files[-1]
                    content = latest_file.read_text()
                    revision_match = re.search(r"revision = ['\"]([^'\"]+)['\"]", content)
                    if revision_match:
                        return revision_match.group(1)
            
            return None
            
        except Exception as e:
            print(f"Warning: Could not determine migration head: {e}")
            return None

    def _build_context(self) -> Dict[str, Any]:
        """Build the template context for model generation."""
        # Get the current migration head
        migration_head = self._get_migration_head()
        
        return {
            "model_name": self.model_name,
            "table_name": self.table_name,
            "class_name": self.class_name,
            "attributes": self.attributes,
            "migration_timestamp": self.migration_timestamp,
            "migration_name": self.migration_name,
            "down_revision": migration_head,
            "timestamp": datetime.now().isoformat(),
            "year": datetime.now().year,
        }
    
    def generate(self):
        """Generate the model and migration files."""
        print(f"Generating model '{self.class_name}' (table: {self.table_name})...")
        
        try:
            # Generate model file
            self._generate_model()
            
            # Generate migration file
            self._generate_migration()
            
            # Update models __init__.py
            self._update_models_init()
            
            print(f"✅ Successfully generated model '{self.class_name}'!")
            print(f"📄 Model file: app/models/{self.model_name}.py")
            print(f"📄 Migration file: db/migrations/versions/{self.migration_timestamp}_{self.migration_name}.py")
            print()
            print("🚀 Next steps:")
            print("   orbin db-migrate  # Run the migration")
            
        except Exception as e:
            print(f"❌ Error generating model: {e}")
            raise
    
    def _generate_model(self):
        """Generate the model file."""
        # Set the output path to current directory since we're inside an app
        self.output_path = Path.cwd()
        
        self.copy_template_file(
            "model/model.py.j2",
            f"app/models/{self.model_name}.py"
        )
    
    def _generate_migration(self):
        """Generate the migration file."""
        # Set the output path to current directory since we're inside an app
        self.output_path = Path.cwd()
        
        # Ensure migrations directory exists
        migrations_dir = self.output_path / "db" / "migrations" / "versions"
        migrations_dir.mkdir(parents=True, exist_ok=True)
        
        self.copy_template_file(
            "model/migration.py.j2",
            f"db/migrations/versions/{self.migration_timestamp}_{self.migration_name}.py"
        )
    
    def _update_models_init(self):
        """Update the models __init__.py file to include the new model."""
        models_init_path = Path.cwd() / "app" / "models" / "__init__.py"
        
        if not models_init_path.exists():
            # Create basic __init__.py if it doesn't exist
            content = f'"""Models package."""\n\nfrom .{self.model_name} import {self.class_name}\n\n__all__ = [\'{self.class_name}\']\n'
        else:
            content = models_init_path.read_text()
        
        # Check if import already exists
        import_line = f"from .{self.model_name} import {self.class_name}"
        if import_line not in content:
            # Add import
            if '"""Models package."""' in content:
                # Insert after the docstring
                content = content.replace(
                    '"""Models package."""',
                    f'"""Models package."""\n\n{import_line}'
                )
            else:
                content = f"{import_line}\n{content}"
            
            # Update __all__ list
            if "__all__" in content:
                # Extract current __all__ list and add new model
                import_match = re.search(r"__all__ = \[(.*?)\]", content, re.DOTALL)
                if import_match:
                    current_models = import_match.group(1)
                    if f"'{self.class_name}'" not in current_models:
                        # Add to existing __all__ list
                        if current_models.strip():
                            new_all = f"__all__ = [{current_models}, '{self.class_name}']"
                        else:
                            new_all = f"__all__ = ['{self.class_name}']"
                        content = re.sub(r"__all__ = \[.*?\]", new_all, content, flags=re.DOTALL)
            else:
                # Add __all__ list
                content += f"\n__all__ = ['{self.class_name}']\n"
            
            # Write updated content
            models_init_path.write_text(content)
            print(f"📄 Updated: app/models/__init__.py")
