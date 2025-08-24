"""
Base generator class for template-based code generation.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import shutil
from jinja2 import Environment, FileSystemLoader, Template


class BaseGenerator:
    """Base class for template-based generators."""
    
    def __init__(self, name: str, target_dir: Optional[str] = None):
        """
        Initialize the base generator.
        
        Args:
            name: Name of the item being generated
            target_dir: Target directory (defaults to current directory)
        """
        self.name = name
        self.target_dir = Path(target_dir) if target_dir else Path.cwd()
        self.output_path = self.target_dir / name
        
        # Set up Jinja2 environment
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Template context - override in subclasses
        self.context = self._build_context()
    
    def _build_context(self) -> Dict[str, Any]:
        """Build the template context. Override in subclasses."""
        return {
            "name": self.name,
        }
    
    def render_template(self, template_path: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_path: Path to the template file relative to templates directory
            context: Additional context to merge with self.context
            
        Returns:
            Rendered template content
        """
        if context is None:
            context = {}
        
        merged_context = {**self.context, **context}
        template = self.jinja_env.get_template(template_path)
        return template.render(**merged_context)
    
    def render_string_template(self, template_string: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Render a template string with the given context.
        
        Args:
            template_string: Template content as string
            context: Additional context to merge with self.context
            
        Returns:
            Rendered template content
        """
        if context is None:
            context = {}
        
        merged_context = {**self.context, **context}
        template = Template(template_string)
        return template.render(**merged_context)
    
    def write_file(self, relative_path: str, content: str):
        """
        Write content to a file relative to the output path.
        
        Args:
            relative_path: Path relative to the output directory
            content: Content to write
        """
        file_path = self.output_path / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📄 Created file: {relative_path}")
    
    def copy_template_file(self, template_path: str, output_path: str, context: Optional[Dict[str, Any]] = None):
        """
        Render a template file and write it to the output directory.
        
        Args:
            template_path: Path to template file (relative to templates directory)
            output_path: Output path (relative to output directory)
            context: Additional context for rendering
        """
        content = self.render_template(template_path, context)
        
        # Remove .j2 extension from output path if present
        if output_path.endswith('.j2'):
            output_path = output_path[:-3]
        
        self.write_file(output_path, content)
    
    def copy_template_directory(self, template_dir: str, output_dir: str = "", context: Optional[Dict[str, Any]] = None):
        """
        Copy and render all template files from a directory.
        
        Args:
            template_dir: Template directory path (relative to templates directory)
            output_dir: Output directory path (relative to output directory)
            context: Additional context for rendering
        """
        template_path = self.templates_dir / template_dir
        
        if not template_path.exists():
            raise ValueError(f"Template directory not found: {template_path}")
        
        for root, dirs, files in os.walk(template_path):
            root_path = Path(root)
            relative_root = root_path.relative_to(template_path)
            
            for file in files:
                if file.endswith('.j2'):
                    template_file_path = template_dir + "/" + str(relative_root / file).replace("\\", "/")
                    output_file_path = str(relative_root / file)
                    
                    # Remove .j2 extension from output path
                    if output_file_path.endswith('.j2'):
                        output_file_path = output_file_path[:-3]
                    
                    if output_dir:
                        output_file_path = output_dir + "/" + output_file_path
                    
                    self.copy_template_file(template_file_path, output_file_path, context)
    
    def create_directory(self, relative_path: str):
        """
        Create a directory relative to the output path.
        
        Args:
            relative_path: Directory path relative to output directory
        """
        dir_path = self.output_path / relative_path
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {relative_path}")
    
    def run_command(self, command: str, cwd: Optional[Path] = None, capture_output: bool = False) -> subprocess.CompletedProcess:
        """
        Run a shell command.
        
        Args:
            command: Command to run
            cwd: Working directory (defaults to output_path)
            capture_output: Whether to capture output
            
        Returns:
            CompletedProcess result
        """
        if cwd is None:
            cwd = self.output_path
        
        try:
            result = subprocess.run(
                command.split(),
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                check=True
            )
            return result
        except subprocess.CalledProcessError as e:
            if not capture_output:
                print(f"⚠️  Warning: Command failed: {command}")
                print(f"Error: {e}")
            raise
