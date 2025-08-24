"""
Controller Generator for Orbin framework.

Creates FastAPI controllers with specified actions and routes.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import inflect

from .base_generator import BaseGenerator


class ControllerGenerator(BaseGenerator):
    """Generator for creating FastAPI controllers with actions."""
    
    def __init__(self, controller_name: str, actions: List[str], target_dir: Optional[str] = None):
        """
        Initialize the controller generator.
        
        Args:
            controller_name: Name of the controller (e.g., "Users", "PostsController", "api/users")
            actions: List of action names (e.g., ["index", "show", "create", "update", "destroy"])
            target_dir: Target directory (defaults to current directory)
        """
        # Initialize inflect engine for pluralization
        self.inflect_engine = inflect.engine()
        
        # Process controller name
        self.controller_name = self._process_controller_name(controller_name)
        self.class_name = self._to_class_name(self.controller_name)
        self.route_prefix = self._to_route_prefix(self.controller_name)
        
        # Process actions
        self.actions = self._process_actions(actions)
        
        super().__init__(self.controller_name, target_dir)
    
    def _process_controller_name(self, name: str) -> str:
        """Process controller name to remove 'Controller' suffix and normalize."""
        # Remove 'Controller' suffix if present
        if name.lower().endswith('controller'):
            name = name[:-10]  # Remove 'controller'
        
        # Handle nested controllers (e.g., "api/users" -> "api_users")
        name = name.replace('/', '_').replace('\\', '_')
        
        # Clean and normalize
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
        return clean_name.strip('_')
    
    def _to_class_name(self, name: str) -> str:
        """Convert controller name to PascalCase class name."""
        # Split by underscore and capitalize each part
        parts = name.split('_')
        class_name = ''.join(word.capitalize() for word in parts)
        return f"{class_name}Controller"
    
    def _to_route_prefix(self, name: str) -> str:
        """Convert controller name to route prefix."""
        # For nested controllers, use the last part
        parts = name.split('_')
        if len(parts) > 1:
            # Handle nested like "api_users" -> "/api/users"
            return '/' + '/'.join(parts)
        else:
            # Simple controller name
            return f"/{name}"
    
    def _process_actions(self, actions: List[str]) -> List[Dict[str, Any]]:
        """Process action names into structured format with HTTP methods and paths."""
        processed = []
        
        for action in actions:
            if not action.strip():
                continue
                
            action_name = action.strip().lower()
            
            # Determine HTTP method and path based on RESTful conventions
            action_info = self._get_action_info(action_name)
            
            processed.append({
                'name': action_name,
                'method': action_info['method'],
                'path': action_info['path'],
                'function_name': self._to_function_name(action_name),
                'description': action_info['description']
            })
        
        return processed
    
    def _get_action_info(self, action_name: str) -> Dict[str, str]:
        """Get HTTP method and path for an action based on RESTful conventions."""
        # Standard RESTful actions
        rest_actions = {
            'index': {
                'method': 'GET',
                'path': '',
                'description': f'Get all {self.controller_name}'
            },
            'show': {
                'method': 'GET', 
                'path': '/{id}',
                'description': f'Get a specific {self.controller_name[:-1] if self.controller_name.endswith("s") else self.controller_name}'
            },
            'create': {
                'method': 'POST',
                'path': '',
                'description': f'Create a new {self.controller_name[:-1] if self.controller_name.endswith("s") else self.controller_name}'
            },
            'update': {
                'method': 'PUT',
                'path': '/{id}',
                'description': f'Update a specific {self.controller_name[:-1] if self.controller_name.endswith("s") else self.controller_name}'
            },
            'destroy': {
                'method': 'DELETE',
                'path': '/{id}',
                'description': f'Delete a specific {self.controller_name[:-1] if self.controller_name.endswith("s") else self.controller_name}'
            },
            'delete': {
                'method': 'DELETE',
                'path': '/{id}',
                'description': f'Delete a specific {self.controller_name[:-1] if self.controller_name.endswith("s") else self.controller_name}'
            }
        }
        
        if action_name in rest_actions:
            return rest_actions[action_name]
        else:
            # Default to GET for custom actions
            return {
                'method': 'GET',
                'path': f'/{action_name}',
                'description': f'{action_name.replace("_", " ").title()} action'
            }
    
    def _to_function_name(self, action_name: str) -> str:
        """Convert action name to valid Python function name."""
        # Replace hyphens with underscores
        function_name = action_name.replace('-', '_')
        
        # Ensure it starts with a letter or underscore
        if function_name and function_name[0].isdigit():
            function_name = f"action_{function_name}"
        
        return function_name
    
    def _build_context(self) -> Dict[str, Any]:
        """Build the template context for controller generation."""
        return {
            "controller_name": self.controller_name,
            "class_name": self.class_name,
            "route_prefix": self.route_prefix,
            "actions": self.actions,
            "timestamp": datetime.now().isoformat(),
            "year": datetime.now().year,
        }
    
    def generate(self):
        """Generate the controller file."""
        print(f"Generating controller '{self.class_name}' with {len(self.actions)} actions...")
        
        try:
            # Generate controller file
            self._generate_controller()
            
            # Update controllers __init__.py
            self._update_controllers_init()
            
            # Show success message with next steps
            self._show_success_message()
            
        except Exception as e:
            print(f"❌ Error generating controller: {e}")
            raise
    
    def _generate_controller(self):
        """Generate the controller file."""
        # Set the output path to current directory since we're inside an app
        self.output_path = Path.cwd()
        
        self.copy_template_file(
            "controller/controller.py.j2",
            f"app/controllers/{self.controller_name}_controller.py"
        )
    
    def _update_controllers_init(self):
        """Update the controllers __init__.py file to include the new controller."""
        controllers_init_path = Path.cwd() / "app" / "controllers" / "__init__.py"
        
        if not controllers_init_path.exists():
            # Create basic __init__.py if it doesn't exist
            content = f'"""Controllers package."""\n\nfrom .{self.controller_name}_controller import {self.class_name}\n\n__all__ = [\'{self.class_name}\']\n'
        else:
            content = controllers_init_path.read_text()
        
        # Check if import already exists
        import_line = f"from .{self.controller_name}_controller import {self.class_name}"
        if import_line not in content:
            # Add import
            if '"""Controllers package."""' in content:
                # Insert after the docstring
                content = content.replace(
                    '"""Controllers package."""',
                    f'"""Controllers package."""\n\n{import_line}'
                )
            else:
                content = f"{import_line}\n{content}"
            
            # Update __all__ list
            if "__all__" in content:
                # Extract current __all__ list and add new controller
                import_match = re.search(r"__all__ = \[(.*?)\]", content, re.DOTALL)
                if import_match:
                    current_controllers = import_match.group(1)
                    if f"'{self.class_name}'" not in current_controllers:
                        # Add to existing __all__ list
                        if current_controllers.strip():
                            new_all = f"__all__ = [{current_controllers}, '{self.class_name}']"
                        else:
                            new_all = f"__all__ = ['{self.class_name}']"
                        content = re.sub(r"__all__ = \[.*?\]", new_all, content, flags=re.DOTALL)
            else:
                # Add __all__ list
                content += f"\n__all__ = ['{self.class_name}']\n"
            
            # Write updated content
            controllers_init_path.write_text(content)
            print(f"📄 Updated: app/controllers/__init__.py")
    
    def _show_success_message(self):
        """Show success message with routes and next steps."""
        print(f"✅ Successfully generated controller '{self.class_name}'!")
        print(f"📄 Controller file: app/controllers/{self.controller_name}_controller.py")
        print()
        print("🛣️  Generated routes:")
        for action in self.actions:
            route_path = f"{self.route_prefix}{action['path']}"
            print(f"   {action['method']:<6} {route_path:<30} → {action['function_name']}()")
        print()
        
        # Automatically add routes to the app
        self.add_route_to_app(self.controller_name, self.controller_name)
        
        print("🚀 Next steps:")
        print("   1. Implement the action logic in the controller")
        print("   2. Customize Pydantic schemas as needed")
        print("   3. Start the server: orbin server")
