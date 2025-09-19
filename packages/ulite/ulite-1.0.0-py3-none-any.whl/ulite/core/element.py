# from .attribute import Attribute
from .event import EventManager
# from zlutils.v1.typing import image as zlimage
from zlutils.v2.typing import image as zlimage
from zlutils.v1.typing.attribute import Attribute

_created_element_count = 0


def autoName(target=None):
    global _created_element_count
    name = f'{target.__class__.__name__}_{_created_element_count}'
    _created_element_count += 1
    return name


def uimethod(cm):
    # wrapper功能， 调用ui（backends）中对应界面元素的特殊功能
    def uimWrapper(element, *arg, **kwarg):
        ename = element.__class__.__name__
        mname = cm.__name__
        ret = cm(element, *arg, **kwarg)
        # print(ename, mname, ret)
        if  element.ui is not None:
            ret =  element.ui.elementCall(element, mname, ret, *arg, **kwarg)
        return ret
    return uimWrapper


class Element:

    def __init__(
        self,
        name=None,
        manager=None,
        *args,
        **kwargs
    ):
        self._name = autoName(self) if name is None else str(name)
        self._ui = None
        self._attributes = Attribute(default_attribute_type='custom')
        self._style = Attribute(default_attribute_type='custom')
        self._bkext = {}
        self._childs = []
        self._parent = None
        self._event_manager = EventManager()
        self._attributes._setDefault('tabindex', _created_element_count)
        self._attributes._setDefault('hidden', False)
        self._style._setDefault('margin', '1px')
        self._initElement()
        self.setAttributes(**kwargs)


    @property
    def ui(self):
        if self._parent is not None:
            return self._parent.ui
        return self._ui

    @property
    def attr(self):
        return self._attributes

    @property
    def event_manager(self):
        return self._event_manager

    @property
    def style(self):
        return self._style

    def _initElement(self):
        pass

    @uimethod
    def onCreate(self):
        pass

    def setHidden(self, mode=True):
        self.setAttributes(hidden=mode)

    def publishEvent(self, event_type, event_data=None):
        self.event_manager.publish(event_type, event_data, self)
        return self

    @uimethod
    def subscribeEvent(self, event_type, callback, priority=0):
        self.event_manager.subscribe(event_type, callback, priority)
        return self

    @uimethod
    def setAttributes(self, **kwargs):
        # TODO style => dict
        self._attributes._update(kwargs)
        return self

    def setAttribute(self, key, value):
        # 兼容方案
        return self.setAttributes(**{key:value})


    @uimethod
    def setStyles(self, **kwargs):
        # print('oe', kwargs, self.ui, self._ui, self._parent)
        self._style._update(kwargs)
        return self

    def findChild(self, name):
        if self._name == name:
            return self
        for c in self._childs:
            ret = c.findChild(name)
            if ret is not None:
                return ret
        return None

    @uimethod
    def addChild(self, child):
        child._parent = self
        self._childs.append(child)
        return self

    @uimethod
    def lockPointer(self, mode=True):
        pass

    @uimethod
    def focus(self):
        pass


# 基本元素

class Root(Element):
    pass


class Label(Element):
    def _initElement(self):
        self.attr._setDefault('text', self._name)


class Button(Label):
    def setCallback(self, callback):
        self.subscribeEvent('click', callback)
        return self


class Input(Element):
    def _initElement(self):
        self.attr._setDefault('placeholder', self._name)
        self.attr._setDefault('value', '')

    @property
    def value(self):
        return self.attr['value']


class CheckBox(Label):
    def _initElement(self):
        super()._initElement()
        self.attr._setDefault('checked', False)

    @property
    def checked(self):
        return self.attr['checked']


class Image(Element):
    def _initElement(self):
        # from . import image as image_typing

        self.__image = zlimage.Image(size_limit=2560*1440)

    def setImage(self, source):
        ret = self.__image.setImage(source)
        if ret:
            self._updateImage()
            self.publishEvent('new_image', self.__image)
        return self

    @uimethod
    def _updateImage(self):
        # print('_updateImage')
        return self

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, source):
        self.setImage(source)


class FontAwesome(Element):
    # TODO
    pass


class Page(Element):
    def _initElement(self):
        self._lines = []
        self._max_lines = 255
        self.style._update({'width': '200px', 'height': '200px'}, 'default')
        self.attr._setDefault('scroll_bottom', True)

    @uimethod
    def _trimLines(self, n):
        n = min(len(self._lines), n)
        self._lines = self._lines[n:]
        return n

    @uimethod
    def _addLines(self, *lines):
        nl = len(lines)
        l = len(self._lines)
        if l+nl > self._max_lines:
            offset = l+nl -self._max_lines + 1
            self._trimLines(offset)
        self._lines += lines
        return self

    def print(self, *lines, end='\n'):  # TODO
        return self._addLines(lines)

    def display(self, image):
        # from . import image as image_typing
        return self._addLines(zlimage.Image(image))


class Selector(Element):
    def _initElement(self):
        self._items = []
        self.attr._setDefault('idx', -1)
        self.attr._setDefault('size', 1)
        # self.style._update({'width': '200px', 'height': '200px'}, 'default')

    @property
    def idx(self):
        return self.attr['idx']

    @property
    def items(self):
        return self._items

    @property
    def selected(self):
        if self.idx >= 0:
            return self._items[self.idx]
        return None

    @uimethod
    def setItems(self, items):
        if self._items != items:
            self.setAttribute('idx', -1)
            self._items = items
        return self

# 布局

class Column(Element):
    def _initElement(self):
        self.attr._setDefault('tabindex', -1)  # 禁止焦点
        self.style._update({'display':'flex', 'flex-direction':'column'})


class Row(Element):
    def _initElement(self):
        self.attr._setDefault('tabindex', -1)
        self.style._update({'display':'flex', 'flex-direction':'row'})


