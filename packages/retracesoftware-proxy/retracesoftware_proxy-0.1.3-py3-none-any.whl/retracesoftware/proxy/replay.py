import retracesoftware.functional as functional
import retracesoftware_utils as utils
import retracesoftware.stream as stream

from retracesoftware.install.tracer import Tracer
from retracesoftware.proxy.thread import per_thread_messages
from retracesoftware.proxy.proxytype import *
# from retracesoftware.proxy.gateway import gateway_pair
from retracesoftware.proxy.record import StubRef, Placeholder
from retracesoftware.proxy.proxysystem import ProxySystem, RetraceError
from retracesoftware.proxy.stubfactory import StubFactory, StubFunction

import os
import weakref
import traceback
# we can have a dummy method descriptor, its has a __name__ and when called, returns the next element

# for types, we can patch the __new__ method
# do it from C and immutable types can be patched too
# patch the tp_new pointer?

class ReplayError(RetraceError):
    pass

class ReplayProxySystem(ProxySystem):
    
    def stubtype(self, cls):
        assert not issubclass(cls, Proxy)

        return dynamic_proxytype(handler = self.ext_handler, cls = cls)

    def create_stub(self): return True

    # def stubtype_from_spec(self, spec):
    #     print (f'FOOO!!! {spec}')
    #     return stubtype_from_spec(
    #         handler = self.ext_handler,
    #         module = spec.module, 
    #         name = spec.name,
    #         methods = spec.methods,
    #         members = spec.members)

    @utils.striptraceback
    def next_result(self):
        while True:
            next = self.messages()

            if next == 'CALL':
                func = self.messages()
                args = self.messages()
                kwargs = self.messages()

                try:
                    func(*args, **kwargs)
                except:
                    pass

            elif next == 'RESULT':
                return self.messages()
            elif next == 'ERROR':
                err_type = self.messages()
                err_value = self.messages()
                utils.raise_exception(err_type, err_value)
            else:
                assert type(next) is not str
                return next

    def bind(self, obj):
        read = self.messages()
        
        assert isinstance(read, Placeholder)

        self.bindings[read] = obj

    # def dynamic_path(self):
    #     if self.getpid() != self.pid:
    #         self.pid = self.getpid()
    #         # ok we are in child, calculate new path
    #         self.path = self.path / f'fork-{self.fork_counter}'
    #         self.fork_counter = 0
        
    #     return self.path

    def after_fork_in_child(self):
        self.reader.path = self.new_child_path(self.reader.path)
        super().after_fork_in_child()

    # def dynamic_ext_proxytype(self, cls):
    #     raise Exception('dynamic_ext_proxytype should not be called in replay')

    def proxy_function(self, obj):
        func = functional.repeatedly(self.next_result)
        func.__name__ = obj.__name__

        return super().proxy_function(func)

    def __init__(self, 
                 thread_state,
                 immutable_types,
                 tracing_config,
                 path,
                 fork_path = []):
        
        # self.writer = writer
        # super().__init__(thread_state = thread_state)
        reader = stream.reader(path)

        self.bindings = utils.id_dict()
        self.set_thread_id = utils.set_thread_id
        self.fork_path = fork_path
        deserialize = functional.walker(self.bindings.get_else_key)

        self.messages = functional.sequence(per_thread_messages(reader), deserialize)

        self.stub_factory = StubFactory(thread_state = thread_state, next_result = self.next_result)

        # messages = reader

        def readnext():
            with thread_state.select('disabled'):
                try:
                    return self.messages()
                except Exception as error:
                    # print(f'Error reading stream: {error}')
                    traceback.print_exc()

                    os._exit(1)

            # print(f'read: {obj}')
            # return obj


        # lookup = weakref.WeakKeyDictionary()
        
        # debug = debug_level(config)

        # int_refs = {}
            
        def read_required(required):
            obj = readnext()
            if obj != required:
                print(f'Replay: {required} Record: {obj}')
                for i in range(5):
                    print(readnext())

                utils.sigtrap(None)
                os._exit(1)
                raise Exception(f'Expected: {required} but got: {obj}')

        def trace_writer(name, *args):
            with thread_state.select('disabled'):
                print(f'Trace: {name} {args}')
                
                read_required('TRACE')
                read_required(name)

                for arg in args:
                    read_required(arg)

        # self.tracer = Tracer(tracing_config, writer = trace_writer)
        # self.immutable_types = immutable_types

        self.reader = reader

        # def foo(cls):
        #     print(cls)
        #     assert isinstance(cls, type)
        #     immutable_types.add(cls)

        # add_stubtype = functional.side_effect(foo)
        # add_stubtype = functional.side_effect(immutable_types.add)

        # reader.type_deserializer[ProxyRef] = functional.sequence(lambda ref: ref.resolve(), self.stubtype, add_stubtype)

        reader.type_deserializer[StubRef] = self.stub_factory
        # reader.type_deserializer[ProxySpec] = functional.sequence(self.stubtype_from_spec, add_stubtype)

        # on_ext_result = functional.if_then_else(
        #     functional.is_instanceof(str), writer.handle('RESULT'), writer)

        # def int_proxytype(gateway):
        #     return lambda cls: dynamic_int_proxytype(handler = gateway, cls = cls, bind = self.bind)

        # create_stubs = functional.walker(functional.when(is_stub_ref, lambda stub: stub.create()))
        # create_stubs = functional.walker(functional.when(is_stub_type, lambda cls: cls()))

        # self.ext_apply = functional.repeatedly(functional.sequence(self.next_result, create_stubs))
        # self.ext_apply = functional.repeatedly(self.next_result)
        
        def read_sync(): read_required('SYNC')

        self.sync = lambda function: utils.observer(on_call = functional.always(read_sync), function = function)
    
        super().__init__(thread_state = thread_state, 
                         tracer = Tracer(tracing_config, writer = trace_writer), 
                         immutable_types = immutable_types)

        # super().__init__(
        #     thread_state=thread_state, 
        #     immutable_types= immutable_types,
        #     tracer=self.tracer,
        #     ext_apply = ext_apply)
        
        # self.ext_handler, self.int_handler = gateway_pair(
        #     thread_state,
        #     self.tracer,
        #     immutable_types = immutable_types,
        #     ext_apply = ext_apply,
        #     int_proxytype = int_proxytype,
        #     ext_proxytype = functional.identity)

    # def extend_type(self, base):
        
    #     # ok, how to provide __getattr__ style access, 

    #     extended = extending_proxytype(
    #         cls = base,
    #         thread_state = self.thread_state, 
    #         int_handler = self.int_handler,
    #         ext_handler = self.ext_handler,
    #         on_subclass_new = self.bind,
    #         is_stub = True)

    #     self.immutable_types.add(extended)
    #     # proxytype = extending_proxytype(base)

    #     # make_extensible(cls = extended, 
    #     #                 int_handler = self.int_handler, 
    #     #                 ext_handler = self.ext_handler,
    #     #                 on_new = self.reader.supply)

    #     return extended
