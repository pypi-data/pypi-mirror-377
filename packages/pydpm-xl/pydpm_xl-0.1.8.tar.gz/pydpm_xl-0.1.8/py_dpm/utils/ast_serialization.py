"""
AST Serialization Utils
======================

Utilities for serializing and deserializing AST objects to/from JSON.
"""

import json
from py_dpm.AST import ASTObjects


def expand_with_expression(node):
    """
    Recursively expand WithExpression nodes by merging partial selections into cell references.

    Args:
        node: AST node to process

    Returns:
        Expanded AST node
    """
    if node is None:
        return None

    if isinstance(node, list):
        return [expand_with_expression(item) for item in node]

    if isinstance(node, dict):
        return {key: expand_with_expression(value) for key, value in node.items()}

    # Handle WithExpression expansion
    if isinstance(node, ASTObjects.WithExpression):
        partial_selection = node.partial_selection
        expression = expand_with_expression(node.expression)

        # Apply partial selection to all VarID nodes in the expression
        return apply_partial_selection(expression, partial_selection)

    # Handle Start node - check if it contains WithExpression
    if isinstance(node, ASTObjects.Start):
        expanded_children = []
        for child in node.children:
            if isinstance(child, ASTObjects.WithExpression):
                # Expand the WithExpression and return just the expanded expression
                expanded = expand_with_expression(child)
                expanded_children.append(expanded)
            else:
                expanded_children.append(expand_with_expression(child))

        # If we have a single expanded child that came from a WithExpression,
        # return the expanded expression directly (no Start wrapper)
        if len(expanded_children) == 1:
            return expanded_children[0]
        else:
            return ASTObjects.Start(children=expanded_children)

    # For other node types, recursively expand children
    if hasattr(node, '__dict__'):
        expanded_node = type(node).__new__(type(node))
        for attr_name, attr_value in node.__dict__.items():
            setattr(expanded_node, attr_name, expand_with_expression(attr_value))
        return expanded_node

    return node


def apply_partial_selection(expression, partial_selection):
    """
    Apply partial selection to VarID nodes in the expression.

    Args:
        expression: Expression AST node
        partial_selection: Partial selection VarID node

    Returns:
        Modified expression with partial selection applied
    """
    if expression is None:
        return None

    if isinstance(expression, list):
        return [apply_partial_selection(item, partial_selection) for item in expression]

    if isinstance(expression, dict):
        return {key: apply_partial_selection(value, partial_selection) for key, value in expression.items()}

    # Apply partial selection to VarID nodes
    if isinstance(expression, ASTObjects.VarID):
        # Create a new VarID with merged properties
        new_varid = ASTObjects.VarID(
            table=partial_selection.table if expression.table is None else expression.table,
            rows=partial_selection.rows if expression.rows is None else expression.rows,
            cols=expression.cols,  # Keep the original cols from the expression
            sheets=partial_selection.sheets if expression.sheets is None else expression.sheets,
            interval=partial_selection.interval if expression.interval is None else expression.interval,
            default=partial_selection.default if expression.default is None else expression.default,
            is_table_group=partial_selection.is_table_group if hasattr(partial_selection, 'is_table_group') else False
        )
        return new_varid

    # For other node types, recursively apply to children
    if hasattr(expression, '__dict__'):
        modified_expr = type(expression).__new__(type(expression))
        for attr_name, attr_value in expression.__dict__.items():
            setattr(modified_expr, attr_name, apply_partial_selection(attr_value, partial_selection))
        return modified_expr

    return expression


def serialize_ast(ast_obj):
    """
    Serialize an AST object to a JSON-serializable dictionary.
    Expands WithExpression nodes before serialization.

    Args:
        ast_obj: An AST object instance

    Returns:
        dict: JSON-serializable dictionary representation
    """
    if ast_obj is None:
        return None

    # First expand any WithExpression nodes
    expanded_obj = expand_with_expression(ast_obj)

    if isinstance(expanded_obj, list):
        return [serialize_ast(item) for item in expanded_obj]

    if isinstance(expanded_obj, dict):
        return {key: serialize_ast(value) for key, value in expanded_obj.items()}

    if hasattr(expanded_obj, 'toJSON'):
        serialized = expanded_obj.toJSON()
        # Recursively serialize nested AST objects
        for key, value in serialized.items():
            if key != 'class_name':
                serialized[key] = serialize_ast(value)
        return serialized

    # For basic types (str, int, float, bool)
    if isinstance(expanded_obj, (str, int, float, bool, type(None))):
        return expanded_obj

    # Fallback: serialize as dict for objects without toJSON
    return expanded_obj.__dict__


def deserialize_ast(data):
    """
    Deserialize a JSON dictionary back to an AST object.

    Args:
        data: Dictionary or list from JSON

    Returns:
        AST object instance
    """
    if data is None:
        return None

    if isinstance(data, list):
        return [deserialize_ast(item) for item in data]

    if isinstance(data, dict):
        if 'class_name' in data:
            # This is an AST object
            class_name = data['class_name']

            # Get the class from ASTObjects module
            if hasattr(ASTObjects, class_name):
                cls = getattr(ASTObjects, class_name)

                # Create a new instance
                obj = object.__new__(cls)

                # Initialize the base AST attributes
                obj.num = None
                obj.prev = None

                # Set all the attributes from the serialized data
                for key, value in data.items():
                    if key != 'class_name':
                        setattr(obj, key, deserialize_ast(value))

                return obj
            else:
                raise ValueError(f"Unknown AST class: {class_name}")
        else:
            # Regular dictionary, deserialize values
            return {key: deserialize_ast(value) for key, value in data.items()}

    # For basic types
    return data


def ast_to_json_string(ast_obj, indent=None):
    """
    Convert AST object to JSON string.

    Args:
        ast_obj: AST object to serialize
        indent: JSON indentation (optional)

    Returns:
        str: JSON string representation
    """
    return json.dumps(serialize_ast(ast_obj), indent=indent)


def ast_from_json_string(json_str):
    """
    Create AST object from JSON string.

    Args:
        json_str: JSON string representation

    Returns:
        AST object instance
    """
    data = json.loads(json_str)
    return deserialize_ast(data)