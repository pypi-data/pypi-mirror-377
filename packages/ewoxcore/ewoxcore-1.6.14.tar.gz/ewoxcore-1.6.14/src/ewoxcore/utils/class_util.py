from typing import Any, List, Set, Optional, Dict, Tuple, get_args, get_origin, get_type_hints, Union, ForwardRef
import sys

_PRIMITIVES = {str, int, float, bool, bytes}


class ClassUtil:
    @staticmethod
    def merge(class_a:Any, class_b:Any) -> Any:
        class_a.__dict__.update(class_b.__dict__)
        return class_a
    

    @staticmethod
    def get_class_name(cls:Any) -> str:
       return cls.__name__ if cls is not None else ""


    @staticmethod
    def get_class_instance_name(cls:Any) -> str:
       return cls.__class__.__name__ if cls is not None else ""


    # @staticmethod
    # def get_class_names(model: Any) -> List[str]:
    #     class_names = set()

    #     # Add class name of the model itself
    #     class_names.add(type(model).__name__)

    #     # Get attributes of the model
    #     try:
    #         attributes = vars(model)
    #     except TypeError:
    #         # model has no __dict__ (e.g. primitive)
    #         return List(class_names)

    #     for attr_name, attr_value in attributes.items():
    #         if attr_value is None:
    #             continue

    #         # Check if it's a list and has elements
    #         if isinstance(attr_value, list) and len(attr_value) > 0:
    #             first_elem = attr_value[0]
    #             elem_class_name = type(first_elem).__name__
    #             if elem_class_name not in ["dict", "list", "str", "int", "float", "bool"]:
    #                 class_names.add(elem_class_name)

    #         # Check if it's another object (not primitive, not list)
    #         elif hasattr(attr_value, "__dict__"):
    #             value_class_name = type(attr_value).__name__
    #             if value_class_name not in ["dict", "list", "str", "int", "float", "bool"]:
    #                 class_names.add(value_class_name)

    #     return list(class_names)


    @staticmethod
    def get_class_names(model: Any) -> List[str]:
        names: Set[str] = set()
        seen: Set[type] = set()

        def add_type(tp: Any):
            if isinstance(tp, type) and tp not in _PRIMITIVES and tp not in {list, dict, tuple, set}:
                names.add(tp.__name__)
                return True
            return False

        def walk_type(tp: Any, queue: List[type]):
            origin = get_origin(tp)
            if origin is None:
                if add_type(tp):
                    queue.append(tp)
                return
            if origin is Union:
                for arg in get_args(tp):
                    if arg is type(None):
                        continue
                    walk_type(arg, queue)
                return
            for arg in get_args(tp):  # List[T], Dict[K,V], etc.
                walk_type(arg, queue)

        def inspect_class(cls: type, queue: List[type]):
            if cls in seen:
                return
            seen.add(cls)
            mod_globals = vars(sys.modules.get(cls.__module__, object()))
            hints = {}
            try:
                hints = get_type_hints(cls, globalns=mod_globals, localns=vars(cls))
            except Exception:
                hints = getattr(cls, "__annotations__", {}) or {}
            for tp in hints.values():
                walk_type(tp, queue)

        # seed with the model’s own type
        names.add(type(model).__name__)
        queue: List[type] = [type(model)]

        # also peek at instance values to recover types from populated lists/objects
        try:
            for val in vars(model).values():
                if val is None:
                    continue
                if isinstance(val, list) and val:
                    if add_type(type(val[0])): queue.append(type(val[0]))
                elif not isinstance(val, (str, int, float, bool, bytes, list, dict, tuple, set)):
                    if add_type(type(val)): queue.append(type(val))
        except TypeError:
            pass

        while queue:
            inspect_class(queue.pop(), queue)

        return sorted(names)
