# backend/app package
import sys

# Python 3.14+ compatibility monkeypatch for Pydantic v1
try:
    import pydantic.main
    original_new = pydantic.main.ModelMetaclass.__new__
    
    def patched_new(mcs, name, bases, namespace, **kwargs):
        if '__annotate_func__' in namespace and '__annotations__' not in namespace or namespace.get('__annotations__') is None:
            try:
                # Call PEP 649 __annotate_func__ with format=1 (Format.VALUE) to get evaluated annotations
                namespace['__annotations__'] = namespace['__annotate_func__'](1)
            except Exception:
                pass
        return original_new(mcs, name, bases, namespace, **kwargs)
        
    pydantic.main.ModelMetaclass.__new__ = patched_new
except Exception:
    pass
