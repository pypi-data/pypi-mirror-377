# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Hammerheads Engineers Sp. z o.o.
# See the accompanying LICENSE file for terms.

from spx_sdk.registry import register_class, load_module_from_path
from spx_sdk.components import SpxComponent
from spx_sdk.attributes import SpxAttribute


@register_class(name="python_file")
@register_class(name="import")
class PythonFile(SpxComponent):
    """
    PythonFile component for dynamic loading and lifecycle management of Python classes from files.

    Extended definition schema supports an optional "methods" mapping per class, allowing you to bind
    lifecycle events ("start", "run", "stop") to arbitrary class methods, with optional arguments/kwargs.

    Example definition:
    {
        "path/to/file.py": {
            "class": "MyClass",
            "init": { ... },
            "methods": {
                "start": "custom_start",              # Shorthand: just method name
                "run": { "method": "custom_run", "args": [1], "kwargs": {"foo": "bar"} },   # Verbose form
                "stop": { "method": "cleanup" }
            },
            ...
        }
    }

    Supported lifecycle names: "start", "run", "stop"
    - Each can be mapped to a method on the class, with optional "args" (list) and "kwargs" (dict).
    - If not specified, lifecycle methods fallback to calling instance.start(), instance.run(), etc. if present.
    - The binding is normalized so all entries have: "method" (str), "args" (list), "kwargs" (dict).
    """

    def _populate(self, definition: dict) -> None:
        # Holds class_name: instance
        self.class_instances = {}
        # Holds lifecycle: list of binding dicts
        self._method_bindings = {"start": [], "run": [], "stop": []}
        for module_path, params in definition.items():
            params["path"] = module_path
            class_instance = self.create_instance_from_module(params)
            class_name = params["class"]
            self.class_instances[class_name] = class_instance

            # Parse optional "methods" mapping for lifecycle bindings
            methods_map = params.get("methods", {})
            for lifecycle in ("start", "run", "stop"):
                binding_entry = methods_map.get(lifecycle, None)
                if binding_entry is None:
                    continue
                # Normalize to dict form
                if isinstance(binding_entry, str):
                    binding = {"method": binding_entry}
                elif isinstance(binding_entry, dict):
                    binding = dict(binding_entry)  # shallow copy
                else:
                    continue  # skip invalid
                # Ensure keys: method (str), args (list), kwargs (dict)
                binding["method"] = binding.get("method") or ""
                binding["args"] = list(binding.get("args", []))
                binding["kwargs"] = dict(binding.get("kwargs", {}))
                self._method_bindings[lifecycle].append({
                    "instance_key": class_name,
                    "instance": class_instance,
                    "method": binding["method"],
                    "args": binding["args"],
                    "kwargs": binding["kwargs"],
                })

    def _invoke_bound(self, lifecycle: str, *extra_args, **extra_kwargs):
        """
        Invoke all methods bound to the given lifecycle, passing extra_args/kwargs after binding's own.
        Returns a list of results or error dicts.
        """
        results = []
        bindings = self._method_bindings.get(lifecycle, [])
        for binding in bindings:
            method_name = binding["method"]
            instance = binding["instance"]
            args = list(binding["args"]) + list(extra_args)
            kwargs = {**binding["kwargs"], **extra_kwargs}
            func = getattr(instance, method_name, None)
            if not callable(func):
                continue
            try:
                res = func(*args, **kwargs)
                results.append(res)
            except Exception as e:
                results.append({"error": str(e), "method": method_name})
        return results

    def _fallback_invoke(self, lifecycle: str, *extra_args, **extra_kwargs):
        """
        If no bound methods are configured, call <lifecycle>() directly on each instance if present.
        Returns a list of results.
        """
        results = []
        for instance in self.class_instances.values():
            func = getattr(instance, lifecycle, None)
            if callable(func):
                try:
                    res = func(*extra_args, **extra_kwargs)
                    results.append(res)
                except Exception as e:
                    results.append({"error": str(e), "method": lifecycle})
        return results

    def start(self, *args, **kwargs):
        """
        Call all configured start methods (or fallback to instance.start()).
        Returns list of results.
        """
        results = self._invoke_bound("start", *args, **kwargs)
        if not results:
            results = self._fallback_invoke("start", *args, **kwargs)
        return results

    def run(self, *args, **kwargs):
        """
        Call all configured run methods (or fallback to instance.run()).
        Returns list of results.
        """
        results = self._invoke_bound("run", *args, **kwargs)
        if not results:
            results = self._fallback_invoke("run", *args, **kwargs)
        return results

    def stop(self, *args, **kwargs):
        """
        Call all configured stop methods (or fallback to instance.stop()).
        Returns list of results.
        """
        results = self._invoke_bound("stop", *args, **kwargs)
        if not results:
            results = self._fallback_invoke("stop", *args, **kwargs)
        return results

    def create_instance_from_module(self, module_info: dict):
        file_path = module_info["path"]
        class_name = module_info["class"]
        module = load_module_from_path(file_path)
        cls = getattr(module, class_name)

        # Extract custom init parameters if provided
        init_info = module_info.get("init", {})
        init_args = init_info.get("args", [])
        init_kwargs = init_info.get("kwargs", {})

        if SpxComponent in cls.__bases__:
            # Prepend root and definition for Item subclasses
            args = [self.get_root(), self.definition] + init_args
            class_instance = cls(*args, **init_kwargs)
        else:
            # Instantiate plain classes with provided args/kwargs
            class_instance = cls(*init_args, **init_kwargs)
        return class_instance

    def prepare(self):
        # Attribute linking logic remains unchanged
        if isinstance(self.definition, dict):
            for module_path, params in self.definition.items():
                for attr, methods in params["attributes"].items():
                    class_name = params["class"]
                    attribute: SpxAttribute = self.get_root().get("attributes").get(attr)
                    if "property" in methods:
                        attribute.link_to_internal_property(self.class_instances[class_name], methods["property"])
                    elif "getter" in methods:
                        getter_name = methods["getter"]
                        setter_name = methods.get("setter", None)
                        attribute.link_to_internal_func(self.class_instances[class_name], getter_name, setter_name)

    def reset(self):
        # Attribute unlinking logic remains unchanged
        for module_path, params in self.definition.items():
            for attr, methods in params["attributes"].items():
                attribute: SpxAttribute = self.get_root().get("attributes").get(attr)
                attribute.unlink_internal_property()
