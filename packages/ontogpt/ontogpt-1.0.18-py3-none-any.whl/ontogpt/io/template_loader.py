"""Loader functions for extraction templates."""

import importlib
import logging
from pathlib import Path

from linkml.generators.pydanticgen import PydanticGenerator
from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import ClassDefinition

TEMPLATE_NAME = str

this_path = Path(__file__).parent
logger = logging.getLogger(__name__)


def get_template_details(template: TEMPLATE_NAME) -> tuple[ClassDefinition, object, object, SchemaView]:
    """
    Get the LinkML class, module, and schemaview for a template.

    This may be a template already known to ontogpt or the path
    to a custom template. It is assumed to be the latter if the
    template input is a path to a YAML file.
    :param template: template name of the form module.ClassName
    :return: tuple of (LinkML class definition, module, specific
    Python class, schemaview)
    """
    # Get the view of core classes first
    core_sv = SchemaView(get_template_path("core"))
    core_classes = [c.name for c in core_sv.all_classes().values()]

    # Check if template is a path to a YAML file
    # If so, this is a custom schema and needs python classes
    if template.endswith(".yaml"):
        logger.info(f"Loading custom schema from {template}")
        path_to_template = Path(template)

        # Check if file exists first
        if not path_to_template.exists():
            raise FileNotFoundError(f"Template file not found at {template}")

        # Copy the schema to the templates directory
        # So it will have access to imports like the core schema
        templates_path = this_path.parent / "templates"
        new_path_to_template = templates_path / path_to_template.name
        new_path_to_template.write_text(path_to_template.read_text())
        module_name = new_path_to_template.stem
        path_to_module = new_path_to_template.with_suffix(".py")

        sv = SchemaView(new_path_to_template)

        gen = PydanticGenerator(str(new_path_to_template))
        path_to_module.write_text(gen.serialize())

        try:
            importlib.invalidate_caches()
            mod = importlib.import_module(f"ontogpt.templates.{module_name}")
        except ImportError as e:
            logger.error(f"Failed to import module {module_name}: {e}")
            raise ImportError(f"Failed to import module {module_name}. "
                              f"Please check the generated version at {path_to_module}")

        class_name = None

    else:
        logger.info(f"Loading schema for {template}")
        if "." in template:
            module_name, class_name = template.split(".", 1)
        else:
            module_name = template
            class_name = None
        path_to_template = get_template_path(module_name)
        sv = SchemaView(path_to_template)
        mod = importlib.import_module(f"ontogpt.templates.{module_name}")

    if class_name is None:
        roots = [c.name for c in sv.all_classes().values() if c.tree_root]
        if len(roots) == 0:
            logger.warning(
                f"Template {template} has no root class. Consider defining one in the schema.")
            roots = [c.name for c in sv.all_classes().values() if c.name not in core_classes]
            # There's an edge case here if the core schema is passed.
            # So we check to see if we still have any roots
            if len(roots) == 0:
                raise ValueError(
                    f"Template {template} has no root class and all classes are in the core schema.")
        elif len(roots) > 1:
            raise ValueError(f"Template {template} has multiple root classes: {roots}")
        class_name = roots[0]

    pyclass = mod.__dict__[class_name]

    logger.info(f"Getting class for template {template}")
    cls = None
    for c in sv.all_classes().values():
        if c.name == class_name:
            cls = c
            break
    if not cls:
        raise ValueError(f"Template {template} not found")
    return (cls, mod, pyclass, sv)


def get_template_path(module_name: str) -> Path:
    """Get the path to the YAML file for the template."""
    templates_path = this_path.parent / "templates"
    return templates_path / f"{module_name}.yaml"
