from ...core import element as cel
import time

def wrapFlaskElement(element, ui):
    return globals().get(element.__class__.__name__, Element)(element, ui)

def reverseMap(d):
    return {v:k for k, v in d.items()}


class ElementMeta(type):
    def __new__(cls, name, bases, attr):
        # print(cls, name, bases, attr)
        attr['attr_map_r'] = reverseMap(attr['attr_map']) if 'attr_map' in attr else bases[0].attr_map_r
        # attr['event_map_r'] = reverseMap(attr['event_map']) if 'event_map' in attr else bases[0].event_map_r
        # attr['style_map_r'] = reverseMap(attr['style_map']) if 'style_map' in attr else bases[0].event_map_r
        return super().__new__(cls, name, bases, attr)


class Element(metaclass=ElementMeta):

    html_type = 'div'
    # origin_key: flask_key
    attr_map = {
        'tabindex': 'tabindex',
        'class': 'class',
        'tips': 'title'
        # 'width': 'clientWidth',
        # 'height': 'clientHeight',
        # 'text': 'textContent',
        }
    style_map = {
        'background_color': 'backgroundColor'
        }
    # event_map: {event_type: [html_event_type, {attr_name: html_event_attr_name}]}
    # event: timestamp
    # 特殊: 鼠标移动速度： vx, vy
    event_map = {
        'resize': ['custom', {}],
        'click': ['click', {}],
        'mousedown': ['mousedown', {'mx':'offsetX', 'my':'offsetY', 'button':'buttons'}],
        'mouseup': ['mouseup', {'mx':'offsetX', 'my':'offsetY', 'button':'buttons'}],
        'mousemove': ['mousemove', {'mx':'offsetX', 'my':'offsetY', 'button':'buttons', 'vx':'vx', 'vy':'vy'}],
        'keydown': ['keydown', {'keycode':'keyCode', 'char':'key', 'alt':'altKey', 'ctrl':'ctrlKey', 'shift':'shiftKey'}],
        'keyup': ['keyup', {'keycode':'keyCode', 'char':'key', 'alt':'altKey', 'ctrl':'ctrlKey', 'shift':'shiftKey'}],
        'keypress': ['keypress', {'keycode':'keyCode', 'char':'key', 'alt':'altKey', 'ctrl':'ctrlKey', 'shift':'shiftKey'}],
        }

    default_attr = {'class': 'no-drag'}
    default_event_list = ['resize']
    # default_observers = ['width', 'height']

    def __init__(self, origin, ui):
        self._origin: cel.Element = origin
        self.ui = ui
        self.initAttribute()
        self.initFinal()

    def initFinal(self):
        pass

    @property
    def target_id(self):
        return self._origin._name

    @property
    def text_id(self):
        return self.target_id + '__text'

    def initAttribute(self):
        pass

    @property
    def html_display(self): # TODO
        if self._origin.attr.hidden:
            return 'none'
        if 'display' in self._origin.style:
            return self._origin.style.display
        return None

    def genCreateUICMD(self):
        attrs = {'html_type': self.html_type}
        # 默认值
        attrs.update(self.default_attr)
        # attrs_map
        origin_attrs = {self.attr_map[k]:v for k, v in self._origin.attr._toDict().items() if k in self.attr_map}
        attrs.update(origin_attrs)
        # style_map
        styles = {self.style_map.get(k, k):v for k, v in self._origin.style._toDict().items()}
        attrs['setStyles'] = styles
        # childs
        childs = [wrapFlaskElement(child, self.ui).genCreateUICMD() for child in self._origin._childs]
        childs.append([self.text_id, 'any', {'html_type': 'a', 'textContent':self._origin.attr.get('text', '')}])
        attrs.update({'addChilds': childs})
        # event注册
        enames = list(set(self._origin.event_manager.all_types + self.default_event_list))
        event_map = {k:v for k, v in self.event_map.items() if k in enames}
        if len(event_map) > 0:
            attrs['setEvents'] = event_map
        if self._origin.attr.get('nofocus', False):
            attrs['onmousedown'] = 'event.preventDefault()'
        attrs['display'] = self.html_display
        return [self.target_id, 'any', attrs]

    def onCreate(self, ret):
        return ret

    def subscribeEvent(self, ret, event_type, callback, priority=0):
        if event_type in self.event_map:
            self.ui.cmdSend(self.target_id, 'setEvents', [self.event_map[event_type]])
        return ret

    def publishEvent(self, event_type, target_id, **event_data):
        if event_type == 'resize':
            self._origin.attr._update(event_data, 'sync')
        elif event_type in ['mousedown', 'mouseup', 'mousemove']:
            x = event_data['mx'] #- self._origin.attr.left
            y = event_data['my'] #- self._origin.attr.top
            new_data = {
                'x': x,
                'y': y,
                'vx': event_data.get('vx', 0),
                'vy': event_data.get('vy', 0),
                'pos': (int(x), int(y)),
                'ppos': (x/self._origin.attr.width, y/self._origin.attr.height),
                'button': event_data['button']
                }
            event_data.update(new_data)
            self._origin.publishEvent(event_type, event_data)
        elif event_type in self.event_map:
            self._origin.publishEvent(event_type, event_data)
        else:
            print(f'[error] undef flask event: {event_type} in {self._origin}')
        return self

    def setAttributes(self, ret, **kwargs):
        attrs = {self.attr_map[k]:v for k, v in kwargs.items() if k in self.attr_map}
        if len(attrs) > 0:
            self.ui.cmdSend(self.target_id, 'setAttributes', attrs)
        if 'text' in kwargs:
            self.ui.cmdSend(self.text_id, 'textContent', kwargs['text'])
        if 'nofocus' in kwargs:
            self.ui.cmdSend(self.target_id, 'onmousedown', 'event.preventDefault()')
        if 'hidden' in kwargs:
            self.ui.cmdSend(self.target_id, 'display', self.html_display)
        return ret

    def setStyles(self, ret, **kwargs):
        # print('fe', kwargs)
        styles = {self.style_map.get(k, k):v for k, v in kwargs.items()}
        self.ui.cmdSend(self.target_id, 'setStyles', styles)
        return ret

    def addChild(self, ret, child):
        self.ui.cmdSend(self.target_id, 'addChild', wrapFlaskElement(child, self.ui).genCreateUICMD())
        return ret

    def lockPointer(self, ret, mode=True):
        self.ui.cmdSend(self.target_id, 'lockpointer', mode)
        return ret

    def focus(self, ret):
        self.ui.cmdSend(self.target_id, 'focus', True)

    #def attrSync(self, **kwargs):  #
    #    # 排除不在 attr_map 中的内容
    #    attrs = {self.attr_map_r[k]: v for k, v in kwargs.items() if k in self.attr_map_r}
    #    self._origin.attr._update(attrs, attribute_type='sync')


class Root(Element):
    #event_map = {**Element.event_map, 'pointerlockchange': ['pointerlockchange', {'target_id':'target.pointerLockElement.id'}] }
    default_attr = {'class':'root_container ui_show'}

    #def publishEvent(self, event_type, target_id, **event_data):
    #    if event_type == 'pointerlockchange':
    #        self._origin.attr._setAttribute('pointerlockelement', event_data.get('target_id'), attribute_type='sync')
    #    return super().publishEvent(event_type, target_id, **event_data)


class Label(Element):
    html_type = 'label'


class Button(Label):
    html_type = 'button'
    default_attr = {'class': 'pure-button'}
    # event_map = {**Element.event_map, 'click': ['click', {}]}


class Input(Element):
    html_type = 'input'
    attr_map = {**Element.attr_map, 'placeholder':'placeholder', 'value': 'value' }
    event_map = {**Element.event_map, 'change': ['change', {'value':'target.value'}] }
    default_event_list = [*Element.default_event_list, 'change']

    def publishEvent(self, event_type, target_id, **event_data):
        if event_type == 'change':
            self._origin.attr._setAttribute('value', event_data.get('value'), attribute_type='sync')
        return super().publishEvent(event_type, target_id, **event_data)


class CheckBox(Label):
    # html_type = 'label'
    attr_map = {k: v for k, v in Element.attr_map.items() if k not in ['text', 'checked'] }
    default_attr = {**Element.default_attr, 'class': 'pure-checkbox'}
    event_map = {**Element.event_map, 'change': ['', {}] }
    default_event_list = [*Element.default_event_list, 'change']

    def publishEvent(self, event_type, target_id, **event_data):
        if event_type == 'change':
            self._origin.attr._setAttribute('checked', event_data.get('checked'), attribute_type='sync')
        return super().publishEvent(event_type, target_id, **event_data)

    @property
    def _checkbox_id(self):
        return self.target_id + '__ckb'

    #@property
    #def _text_id(self):
    #    return self.target_id + '__txt'

    def genCreateUICMD(self):
        target_id, method, attrs = super().genCreateUICMD()
        childs = attrs.get('addChilds', [])
        attrs['for'] = self._checkbox_id
        childs.insert(0, [self._checkbox_id, 'any', {
            'html_type':'input',
            'type':'checkbox',
            'checked': self._origin.attr.checked,
            'setEvents':{
                'change': ['change', {'checked':'target.checked', 'target_id':target_id}]  # 保留字：target_id
                }
            }])
        #childs.append([self._text_id, 'any', {
        #    'html_type':'a',
        #    'textContent': self._origin.attr.text
        #    }])
        attrs['addChilds'] = childs
        return [target_id, method, attrs]

    def setAttributes(self, ret, **kwargs):
        #if 'text' in kwargs:
        #    self.ui.cmdSend(self._text_id, 'setAttributes', {'textContent': kwargs['text']})
        if 'checked' in kwargs:
            self.ui.cmdSend(self._checkbox_id, 'setAttributes', {'checked': kwargs['checked']})
        return super().setAttributes(ret, **kwargs)

        attrs = {self.attr_map[k]:v for k, v in kwargs.items() if k in self.attr_map}
        if len(attrs) > 0:
            self.ui.cmdSend(self.target_id, 'setAttributes', attrs)
        return ret


class Image(Element):
    html_type = 'img'

    last_update_time_key = 'flaskui_last_update_time'
    mjpeg_key = 'flaskui_ismjpeg'

    def getImage(self, im_id=None):
        return self._origin.image

    def genCreateUICMD(self):
        target_id, method, attrs = super().genCreateUICMD()
        attrs['src'] = self._genImageSrc()
        return [target_id, method, attrs]

    def _genImageSrc(self):
        # if self.getImage().source_type == 'jpeg':
        if 'jpeg' in self.getImage():
            return f'/jpeg_blob?target_id={self.target_id}&t={time.time()}'
        else:
            return f'/png_blob?target_id={self.target_id}&t={time.time()}'

    def _updateImage(self, ret):
        time_delta = time.time() - self._origin._bkext.get(self.last_update_time_key, 0)
        if time_delta < 0.2 and not self._origin._bkext.get(self.mjpeg_key, False):
            self._origin._bkext[self.mjpeg_key] = True
            # self.ui.cmdSend(self.target_id, 'src', f'/video_feed?target_id={self.target_id}&attr=image')
            self.ui.cmdSend(self.target_id, 'any', {
                #'contextmenu': False,
                'src': f'/video_feed?target_id={self.target_id}'
                })
        elif time_delta > 60 and self._origin._bkext.get(self.mjpeg_key, False):
            self._origin._bkext[self.mjpeg_key] = False
        if not self._origin._bkext.get(self.mjpeg_key, False):
            # self.ui.cmdSend(self.target_id, 'src', f'/png_blob?target_id={self.target_id}&attr=image&time={time.time()}')
            self.ui.cmdSend(self.target_id, 'any', {
                #'contextmenu': True,
                'src': self._genImageSrc()
                })
        self._origin._bkext[self.last_update_time_key] = time.time()
        return ret


class FontAwesome(Element):
    html_type = 'i'


class Page(Element):
    html_type = 'ul'

    lines_offset_key = 'lines_offset'

    @property
    def lines_offset(self):
        return self._origin._bkext.get(self.lines_offset_key, 0)

    @lines_offset.setter
    def lines_offset(self, value):
        self._origin._bkext[self.lines_offset_key] = value

    def genLinesChildsCMD(self, l, c):
        from ...core import image as image_typing
        childs = []
        for i in range(l, l+c):
            it = self._origin._lines[i]
            im_id = self.lines_offset + i
            it_id = self.target_id + '__' + im_id
            if isinstance(it, image_typing._Image):
                cmd = [it_id, 'any', {'html_type':'li', 'addChilds':[[it_id+'__', 'any', {'html_type':'img', 'src': f'/png_blob?target_id={self.target_id}&im_id={im_id}&t={time.time()}'}]]}]
            else:
                cmd = [it_id, 'any', {'html_type':'li', 'textContent':str(it)}]
            childs.append(cmd)
        return childs

    def getImage(self, im_id):
        return self._origin._lines[im_id - self.lines_offset]

    def _trimLines(self, ret, n):
        n = ret
        if n > 0:
            offset = self.lines_offset
            offset += n
            self.lines_offset = offset
            self.cmdSend(self.target_id, 'removeChildsById', [[0, n]])
        return ret

    def _addLines(self, ret, *lines):
        c = len(lines)
        l = len(self._origin._lines) - c
        self.ui.cmdSend(self.target_id, 'addChilds', self.genLinesChildsCMD(l, c))
        return ret

class Selector(Element):
    html_type = 'select'
    attr_map = {**Element.attr_map, 'idx': 'value', 'size':'size' }
    default_attr = {'class': 'no-drag'}
    event_map = {**Element.event_map, 'change': ['change', {'value':'target.value'}] }
    default_event_list = [*Element.default_event_list, 'change']

    #@property
    #def ul_id(self):
    #    return self.target_id + '__ul'

    def publishEvent(self, event_type, target_id, **event_data):
        if event_type == 'change':
            self._origin.attr._setAttribute('idx', int(event_data.get('value')), attribute_type='sync')
        return super().publishEvent(event_type, target_id, **event_data)

    def setItems(self, ret, items):
        childs = [self.genItemCMD(item, idx) for idx, item in enumerate(items)]
        self.ui.cmdSend(self.target_id, 'innerHTML', '')
        self.ui.cmdSend(self.target_id, 'addChilds', childs)
        self.ui.cmdSend(self.target_id, 'value', self._origin.idx)
        return ret

    def genItemCMD(self, item, idx):
        # TODO <optgroup label="Flying pets">
        if isinstance(item, str):
            cmd = [f'{self.target_id}__it_{idx}_text', 'any', {'html_type':'a', 'textContent':item}]
        else:
            fit = wrapFlaskElement(item)
            cmd = fit.genCreateUICMD()
        return [f'{self.target_id}__it_{idx}', 'any', {'html_type':'option', 'addChilds':[cmd], 'value': idx}]

    def genCreateUICMD(self):
        ret = super().genCreateUICMD()
        if len(self._origin._items) > 0:
            childs = [self.genItemCMD(item, idx) for idx, item in enumerate(self._origin._items)]
            ret[2]['addChilds'] = childs
        return ret

    '''
    def genItemCMD(self, item, idx):
        if isinstance(item, str):
            cmd = [f'{self.target_id}__it_{idx}_text', 'any', {'html_type':'a', 'class':'pure-menu-link', 'textContent':item, 'href':"#"}]
        else:
            fit = wrapFlaskElement(item)
            cmd = fit.genCreateUICMD()
        return [f'{self.target_id}__it_{idx}', 'any', {'html_type':'li', 'class':'pure-menu-item', 'addChilds':[cmd]}]

    def genCreateUICMD(self):
        ret = super().genCreateUICMD()
        if len(self._origin._items) > 0:
            childs = [self.genItemCMD(item, idx) for idx, item in enumerate(self._origin._items)]
            ret[2]['addChilds'] = [[self.ul_id, 'any', {'html_type':'ul', 'class':'pure-menu-list', 'addChilds': childs} ]]
        return ret'''
