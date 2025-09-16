import retracesoftware.functional as functional
import retracesoftware_utils as utils
import types
from retracesoftware.proxy.gateway import adapter_pair
from types import SimpleNamespace
from retracesoftware.proxy.proxytype import *
from retracesoftware.proxy.stubfactory import Stub
import sys
import gc

class RetraceError(Exception):
    pass

def proxy(proxytype):
    return functional.spread(
        utils.create_wrapped,
        functional.sequence(functional.typeof, proxytype),
        None)

def maybe_proxy(proxytype):
    return functional.if_then_else(
            functional.isinstanceof(utils.Wrapped),
            utils.unwrap,
            proxy(functional.memoize_one_arg(proxytype)))

unproxy_execute = functional.mapargs(starting = 1, 
                                     transform = functional.walker(utils.try_unwrap), 
                                     function = functional.apply)

def resolve(obj):
    try:
        return getattr(sys.modules[obj.__module__], obj.__name__)
    except:
        return None

def is_function_type(cls):
    return cls in [types.BuiltinFunctionType, types.FunctionType]

class ProxySystem:
    
    def bind(self, obj): pass

    def wrap_int_to_ext(self, obj): 
        return obj
        # return functional.sequence(functional.side_effect(functional.repeatedly(gc.collect)), obj)
    
    def wrap_ext_to_int(self, obj): return obj
    
    def on_int_call(self, func, *args, **kwargs):
        pass

    def on_ext_result(self, result):
        pass

    def on_ext_error(self, err_type, err_value, err_traceback):
        pass

    def __init__(self, thread_state, immutable_types, tracer):
        
        self.thread_state = thread_state
        self.fork_counter = 0
        self.tracer = tracer
        self.immutable_types = immutable_types
        self.on_proxytype = None
        
        def is_immutable_type(cls):
            return issubclass(cls, tuple(immutable_types))

        is_immutable = functional.sequence(functional.typeof, functional.memoize_one_arg(is_immutable_type))

        def proxyfactory(proxytype):
            return functional.walker(functional.when_not(is_immutable, maybe_proxy(proxytype)))

        int_spec = SimpleNamespace(
            apply = thread_state.wrap('internal', functional.apply),
            proxy = proxyfactory(thread_state.wrap('disabled', self.int_proxytype)),
            on_call = tracer('proxy.int.call', self.on_int_call),
            on_result = tracer('proxy.int.result'),
            on_error = tracer('proxy.int.error'),
        )

        ext_spec = SimpleNamespace(
            apply = thread_state.wrap('external', functional.apply),
            proxy = proxyfactory(thread_state.wrap('disabled', self.dynamic_ext_proxytype)),
            on_call = tracer('proxy.ext.call'),
            on_result = self.on_ext_result,
            on_error = self.on_ext_error,
        )

        int2ext, ext2int = adapter_pair(int_spec, ext_spec)

        def gateway(name, internal = functional.apply, external = functional.apply):
            default = tracer(name, unproxy_execute)
            return thread_state.dispatch(default, internal = internal, external = external)
    
        self.ext_handler =  self.wrap_int_to_ext(int2ext)
        self.int_handler =  self.wrap_ext_to_int(ext2int)

        self.ext_dispatch = gateway('proxy.int.disabled.event', internal = self.ext_handler)
        self.int_dispatch = gateway('proxy.ext.disabled.event', external = self.int_handler)

    def new_child_path(self, path):
        return path.parent / f'fork-{self.fork_counter}' / path.name

    def before_fork(self):
        self.saved_thread_state = self.thread_state.value
        self.thread_state.value = 'disabled'

    def after_fork_in_child(self):
        self.thread_state.value = self.saved_thread_state
        self.fork_counter = 0

    def after_fork_in_parent(self):
        self.thread_state.value = self.saved_thread_state
        self.fork_counter += 1

    def create_stub(self): return False
        
    def int_proxytype(self, cls):
        return dynamic_int_proxytype(
                handler = self.int_dispatch,
                cls = cls,
                bind = self.bind)

    def dynamic_ext_proxytype(self, cls):

        proxytype = dynamic_proxytype(
            handler = self.ext_dispatch,
            cls = cls)
        if self.on_proxytype:
            self.on_proxytype(proxytype)
        
        return proxytype
        
        # resolved = resolve(cls)
        # if isinstance(resolved, ExtendingProxy):
        #     return dynamic_from_extended(resolved)
        # elif isinstance(resolved, DynamicProxy):
        #     return resolved
        # else:
        #     return dynamic_proxytype(handler = self.ext_dispatch, cls = cls)

    def ext_proxytype(self, cls):
        assert isinstance(cls, type)
        if utils.is_extendable(cls):
            return self.extend_type(cls)
        else:    
            return instantiable_dynamic_proxytype(
                    handler = self.ext_dispatch, 
                    cls = cls,
                    thread_state = self.thread_state,
                    create_stub = self.create_stub())

    def extend_type(self, cls):

        extended = extending_proxytype(
            cls = cls,
            base = Stub if self.create_stub() else cls,
            thread_state = self.thread_state, 
            ext_handler = self.ext_dispatch,
            int_handler = self.int_dispatch,
            on_subclass_new = self.bind)
        
        self.immutable_types.add(extended)

        return extended

    def function_target(self, obj): return obj

    def proxy_function(self, obj):
        return utils.wrapped_function(handler = self.ext_handler,  target = obj)
        
    def __call__(self, obj):
        assert not isinstance(obj, BaseException)
        assert not isinstance(obj, Proxy)
        assert not isinstance(obj, utils.wrapped_function)
            
        if type(obj) == type:
            if obj in self.immutable_types or issubclass(obj, tuple):
                return obj
            
            return self.ext_proxytype(obj)
            
        elif type(obj) in self.immutable_types:
            return obj
        
        elif is_function_type(type(obj)):

            return self.thread_state.dispatch(
                obj, 
                internal = self.proxy_function(obj))
        
        else:
            proxytype = dynamic_proxytype(handler = self.ext_dispatch, cls = type(obj))

            return utils.create_wrapped(proxytype, obj)
            # raise Exception(f'object {obj} was not proxied as its not a extensible type and is not callable')
