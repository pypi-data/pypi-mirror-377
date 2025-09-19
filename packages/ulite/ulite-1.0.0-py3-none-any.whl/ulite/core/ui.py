# import time

# from threading import Condition
from collections import OrderedDict
from .element import Element, Root
from .event import EventManager
from zlutils.v1.typing.attribute import Attribute
# from .attribute import Attribute
# from .const import BASECONST


class BaseUI:

    UITAG = 'UI'
    ROOTID = 'root'

    def __init__(self, **kwargs):
        self._init0()
        self.elements = OrderedDict()
        self._attributes = Attribute(default_attribute_type='custom')\
            ._update({'title':'Ulite', 'pointerlockelement': False})._update(kwargs)
        self._event_manager = EventManager()
        self.__root = Root(name=self.ROOTID, manager=self)
        self.__root._ui = self
        # self.__root._event_manager = self._event_manager.sub(self.__root._name)
        self._initVar()

    @property
    def attr(self):
        return self._attributes

    def _init0(self):
        pass

    def _initVar(self):
        pass

    @property
    def root(self):
        return self.__root

    @property
    def event_manager(self):
        return self._event_manager

    # --------------- element
    def elementCall(self, element, mname, ret, *arg, **kwarg):
        return ret

    # ------------------------------------------

    def getElement(self, name):
        if name == self.UITAG:
            return self
        if name in self.elements:
            return self.elements[name]
        ret = self.__root.findChild(name)
        if ret is None:
            return None
        self.regElement(ret)
        return ret

    def regElement(self, element: Element):
        if element._name in self.elements:
            raise RuntimeError(f'重复注册组件: {element.name}')
        self.elements[element._name] = element

    def progressUIEvent(self, hevent):
        # ename = hevent['name']
        # etarget_id = hevent['target_id']
        # epath = f'{etarget_id}.{ename}'
        # target = self.getElement(etarget_id)
        # hevent['event_path'] = epath
        # hevent['target'] = target
        # self.publishEvent(epath, hevent, target=target)
        # self._event_manager.publish(epath, hevent, source=self.getElement(etarget_id))
        pass

    def publishEvent(self, event_type, target=None, **event_data):
        source = self if target is None else target
        self._event_manager.publish(event_path, event_data, source=source)

    def subscribeEvent(self, event_path, callback, priority=None):
        if priority is None and '.' not in event_path:
            priority = 0
        self._event_manager.subscribe(event_path, callback, priority)

    def show(self, *args, **kwargs):
        # TODO
        pass

    def join(self):
        pass

    pass
