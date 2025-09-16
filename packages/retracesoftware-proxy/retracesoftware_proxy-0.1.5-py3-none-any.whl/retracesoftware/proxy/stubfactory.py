import sys
import os

import retracesoftware.functional as functional
import retracesoftware.utils as utils

class Stub:
    __slots__ = []

class ExtendedRef:
    def __init__(self, module, name):
        self.type = type
        self.module = module

class StubRef:
    def __init__(self, module, name, methods, members):
        self.name = name
        self.module = module
        self.methods = methods
        self.members = members

    def __str__(self):
        return f'StubRef(module = {self.module}, name = {self.name}, methods = {self.methods}, members = {self.members})'

def resolve(module, name):
    try:
        return getattr(sys.modules[module], name)
    except:
        return None

class StubMethodDescriptor(functional.repeatedly):
    def __init__(self, name, next_result):
        super().__init__(next_result)
        self.__name__ = name

    def __str__(self):
        return f"stub - {__name__}"
    
class StubMemberDescriptor:
    def __init__(self, name, next_result):
        self.next_result = next_result
        self.__name__ = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        return self.next_result()

    def __set__(self, instance, value):
        return self.next_result()

    def __delete__(self, instance):
        return self.next_result()

    def __str__(self):
        return f"stub member - {__name__}"

class StubFunction(functional.repeatedly):
    def __init__(self, name, next_result):
        super().__init__(next_result)
        self.__name__ = name

    def __str__(self):
        return f"stub function - {__name__}"

class StubFactory:

    __slots__ = ['next_result', 'thread_state', 'cache']

    def __init__(self, thread_state, next_result):
        self.next_result = next_result
        self.thread_state = thread_state
        self.cache = {}

    def create_member(self, name):
        def disabled(*args, **kwargs):
            if self.thread_state.value == 'disabled' and name == '__repr__':
                return f"stub member - {name}"
            else:
                print(f'Error trying to call member descriptor: {name} {args} {kwargs}, retrace mode: {self.thread_state.value}')
                utils.sigtrap(None)
                os._exit(1)
            
        next_result = self.thread_state.dispatch(disabled, external = self.next_result)

        return StubMemberDescriptor(name = name, next_result = next_result)

    def create_method(self, name):

        def disabled(*args, **kwargs):
            if self.thread_state.value == 'disabled' and name == '__repr__':
                return f"stub - {name}"
            else:
                print(f'Error trying to call descriptor: {name} {args} {kwargs}, retrace mode: {self.thread_state.value}')
                utils.sigtrap(None)
                os._exit(1)
            
        next_result = self.thread_state.dispatch(disabled, external = self.next_result)

        func = functional.repeatedly(next_result)
        func.__name__ = name

        return func

    def create_stubtype(self, spec):

        slots = {
            '__module__': spec.module,
            '__qualname__': spec.name,
        }

        for method in spec.methods:
            slots[method] = self.create_method(method)
            assert utils.is_method_descriptor(slots[method])

        for member in spec.members:
            slots[member] = self.create_member(member)

        resolved = resolve(spec.module, spec.name)

        if isinstance(resolved, type):
            slots['__class__'] = property(functional.repeatedly(resolved))

        stubtype = type(spec.name, (Stub, ), slots)

        for method in spec.methods:
            slots[method].__objclass__ = stubtype

        return stubtype

    def __call__(self, spec):
        print(f'In stubFactory.__call__ {spec}')
        if spec not in self.cache:
            self.cache[spec] = self.create_stubtype(spec)
        
        stubtype = self.cache[spec]
        stub = stubtype.__new__(stubtype)
        print(f'In stubFactory created new')
        return stub
