import retracesoftware.functional as functional
import retracesoftware.utils as utils
import retracesoftware.stream as stream

from retracesoftware.proxy.proxytype import *
# from retracesoftware.proxy.gateway import gateway_pair
from retracesoftware.proxy.proxysystem import ProxySystem
from retracesoftware.proxy.thread import write_thread_switch
from retracesoftware.install.tracer import Tracer
from retracesoftware.proxy.stubfactory import StubRef, ExtendedRef

import sys
import os
import types
import gc

class Placeholder:
    __slots__ = ['id', '__weakref__']

    def __init__(self, id):
        self.id = id
    
def keys_where_value(pred, dict):
    for key,value in dict.items():
        if pred(value): yield key

types_lookup = {v:k for k,v in types.__dict__.items() if isinstance(v, type)}

def resolve(obj):
    try:
        return getattr(sys.modules[obj.__module__], obj.__name__)
    except:
        return None
    
def resolveable(obj):
    try:
        return getattr(sys.modules[obj.__module__], obj.__name__) is obj
    except:
        return False

def resolveable_name(obj):
    if obj in types_lookup:
        return ('types', types_lookup[obj])
    elif resolve(obj) is obj:
        return (obj.__module__, obj.__name__)
    else:
        return None

# when 
class RecordProxySystem(ProxySystem):
    
    def bind(self, obj):
        self.bindings[obj] = self.writer.handle(Placeholder(self.next_placeholder_id))
        self.writer(self.bindings[obj])
        self.next_placeholder_id += 1

    def before_fork(self):
        self.writer.close()
        super().before_fork()
        # self.writer.path = self.dynamic_path

    def after_fork_in_child(self):
        new_path = self.new_child_path(self.writer.path)
        new_path.parent.mkdir()
        self.writer.path = new_path
        super().after_fork_in_child()

    def after_fork_in_parent(self):
        super().after_fork_in_parent()
        self.thread_state.value = self.saved_thread_state
        self.writer.reopen()

    def __init__(self, thread_state, 
                 immutable_types, 
                 tracing_config,
                 path):
        
        self.fork_counter = 0

        self.getpid = thread_state.wrap(
            desired_state = 'disabled', function = os.getpid)
        
        self.pid = self.getpid()

        self.writer = stream.writer(path)
        
        # w = self.writer.handle('TRACE')
        # def trace_writer(*args):
        #     print(f'Trace: {args}')
        #     w(*args)

        self.extended_types = {}
        self.bindings = utils.id_dict()
        self.next_placeholder_id = 0

        serialize = functional.walker(self.bindings.get_else_key)
        
        thread_switch_monitor = \
            utils.thread_switch_monitor(
                functional.repeatedly(functional.sequence(utils.thread_id, self.writer)))

        self.sync = lambda function: functional.firstof(thread_switch_monitor, functional.always(self.writer.handle('SYNC')), function)
            
        error = self.writer.handle('ERROR')

        def write_error(cls, val, traceback):
            error(cls, val)
        
        self.set_thread_id = functional.partial(utils.set_thread_id, self.writer)

        def watch(f): return functional.either(thread_switch_monitor, f)

        tracer = Tracer(tracing_config, writer = self.writer.handle('TRACE'))

        self.wrap_int_to_ext = watch
        
        self.on_int_call = functional.mapargs(transform = serialize, function = self.writer.handle('CALL'))
        
        self.on_ext_result = functional.if_then_else(
                                functional.isinstanceof(str), 
                                self.writer.handle('RESULT'), 
                                functional.sequence(serialize, self.writer))
        
        self.on_ext_error = write_error

        self.ext_apply = self.int_apply = functional.apply

        super().__init__(thread_state = thread_state, tracer = tracer, immutable_types = immutable_types)

    def dynamic_ext_proxytype(self, cls):
        
        proxytype = super().dynamic_ext_proxytype(cls)

        blacklist = ['__class__', '__dict__', '__module__', '__doc__']

        methods = []
        members = []

        for key,value in proxytype.__dict__.items():
            if key not in blacklist:
                if utils.is_method_descriptor(value):
                    methods.append(key)
                elif not key.startswith("__retrace"):
                    members.append(key)

        ref = self.writer.handle(StubRef(
            name = cls.__name__,
            module = cls.__module__,
            methods = methods,
            members = members))
        
        # list(proxytype.__dict__.keys())

        # if resolveable_name(cls):
        #     module, name = resolveable_name(cls)
        #     ref = self.writer.handle(StubRef(type = 'dynamic', name = name, module = module))
        # else:
        #     blacklist = ['__getattribute__']
        #     descriptors = {k: v for k,v in superdict(cls).items() if k not in blacklist and is_descriptor(v) }

        #     methods = [k for k, v in descriptors.items() if utils.is_method_descriptor(v)]
        #     members = [k for k, v in descriptors.items() if not utils.is_method_descriptor(v)]

        #     ref = self.writer.handle(ProxySpec(name = cls.__name__, 
        #                                     module = cls.__module__,
        #                                     methods = methods,
        #                                     members = members))
  
        self.writer.type_serializer[proxytype] = functional.constantly(ref)

        return proxytype

    def ext_proxytype(self, cls):
        assert isinstance(cls, type), f"record.proxytype requires a type but was passed: {cls}"

        # resolved = resolve(cls)

        proxytype = super().ext_proxytype(cls)

        assert resolve(cls) is cls

        # ref = self.writer.handle(StubRef(name = cls.__name__,
        #                                  module = cls.__module__))

        # if resolveable_name(cls):
        #     module, name = resolveable_name(cls)
        #     ref = self.writer.handle(StubRef(name = cls.__name__, module = cls.__module__))
        # else:
        #     blacklist = ['__getattribute__']
        #     descriptors = {k: v for k,v in superdict(cls).items() if k not in blacklist and is_descriptor(v) }

        #     methods = [k for k, v in descriptors.items() if utils.is_method_descriptor(v)]
        #     members = [k for k, v in descriptors.items() if not utils.is_method_descriptor(v)]

        #     ref = self.writer.handle(ProxySpec(name = cls.__name__, 
        #                                     module = cls.__module__,
        #                                     methods = methods,
        #                                     members = members))
  
        # self.writer.type_serializer[proxytype] = functional.constantly(ref)
        return proxytype


    def extend_type(self, cls):

        if cls in self.extended_types:
            return self.extended_types[cls]

        extended = super().extend_type(cls)
        
        self.extended_types[cls] = extended 

        ref = self.writer.handle(ExtendedRef(name = cls.__name__,
                                             module = cls.__module__))

        # for binding?
        # self.writer(ref)

        self.writer.type_serializer[extended] = functional.constantly(ref)

        return extended
