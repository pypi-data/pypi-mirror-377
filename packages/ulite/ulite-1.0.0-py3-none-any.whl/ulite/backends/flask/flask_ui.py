import os
import time
from threading import Condition
from zlutils.v1.typing import image as zlimage
from ...core.ui import BaseUI
from ...core import element as cel
from . import flask_element as fel


PACKAGEDIR = os.path.dirname(os.path.abspath(__file__))
HTMLDIR = os.path.join(PACKAGEDIR, 'templates/')
HOMEPAGENAME = 'flask_index.html'
HOMEPAGEPATH = os.path.join(HTMLDIR, HOMEPAGENAME)
STATICPATH = os.path.join(PACKAGEDIR, 'static')
STATICURLPATH = '/static'


def wrapFlaskElement(element, ui):
    return getattr(fel, element.__class__.__name__, fel.Element)(element, ui)


class FlaskUI(BaseUI):
    UITAG = '_flask_ui'
    event_map = {'pointerlockchange': ['pointerlockchange', {'value':'target.pointerLockElement.id'}] }
    default_event_list = ['pointerlockchange']

    def _initVar(self):
        self.attr._update(
            {
                'host': '0.0.0.0',
                'port': 5000
                },
            'default'
            )
        # cmd_list: [[target_id, method, args], ...]
        self._cmd_list = []

        self._cmd_condition = Condition()
        self._ui_heart_beat = 0

    def cmdNotify(self):
        with self._cmd_condition:
            self._cmd_condition.notify_all()
        return self

    def cmdSend(self, *cmd):
        self._cmd_list.append(cmd)
        self.cmdNotify()

    def elementCall(self, element, mname, ret, *arg, **kwarg):
        felement = wrapFlaskElement(element, self)
        if hasattr(felement, mname):
            fmethod = getattr(felement, mname)
            return fmethod(ret, *arg, **kwarg)
        return ret

    def genCreateUICMDList(self):
        cmd_list = []
        enames = list(set(self.event_manager.all_types + self.default_event_list))
        event_map = {k:v for k, v in self.event_map.items() if k in enames}
        if len(event_map) > 0:
            cmd_list.append([self.UITAG, 'setEvents', event_map])
        cmd_list.append(wrapFlaskElement(self.root, self).genCreateUICMD())
        return cmd_list

    def subscribeEvent(self, event_type, callback, priority=None):
        if priority is None and '.' not in event_type:
            priority = 0
            self.cmdSend(self.UITAG, 'setEvents', [self.event_map[event_type]])
        self._event_manager.subscribe(event_type, callback, priority)

    def publishEvent(self, event_type, target=None, **event_data ):
        target = self if target is None else target
        if target == self:
            # print(event_type, event_data)
            if event_type == 'pointerlockchange':
                self.attr._setAttribute('pointerlockelement', event_data.get('value'), attribute_type='sync')
        self._event_manager.publish(event_type, event_data, source=target)

    def createApp(self):

        from flask import Flask, render_template, Response, request, jsonify, send_file, send_from_directory, session
        from io import BytesIO

        app = Flask(
            # __name__,
            self.attr.title,
            template_folder=HTMLDIR,
            static_folder=STATICPATH,
            static_url_path=STATICURLPATH,
            )

        app.secret_key = str(hash(str(time.time())))  # 设置秘密密钥

        @app.route('/favicon.ico')
        def favicon():
            return send_from_directory(STATICPATH, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

        @app.route('/')
        def homepage():
            if time.time() - self._ui_heart_beat < 2:
                return '同时只允许一个ui, 请稍后再试'
            if 'session_id' not in session:
                session['session_id'] = f'{request.remote_addr}|{time.time()}'  # 使用IP地址作为会话ID
            webvars = {
                'title': self.attr.title,
                'version':  '1.0',
                'root_id': self.ROOTID,
                'ui_tag': self.UITAG,
                }
            print(webvars)
            return render_template(HOMEPAGENAME, **webvars)

        @app.route('/cmd', methods=['GET', 'POST'])
        def cmd():
            while (len(self._cmd_list) == 0):
                with self._cmd_condition:
                    self._cmd_condition.wait(timeout=1)
            cmd_list = self._cmd_list
            self._cmd_list = []
            # print(cmd_list)
            return jsonify(cmd_list)

        @app.route('/api', methods=['GET', 'POST'])
        def api():
            method, kwargs = request.get_json()
            if method == 'event':
                target = self.getElement(kwargs.get('target_id'))
                if target is self:
                    self.publishEvent(**kwargs)
                else:
                    wrapFlaskElement(target, self).publishEvent(**kwargs)
                # self.progressUIEvent(args)
            elif method == 'handshake':
                self._cmd_list = []
                self._cmd_list.append(['system', 'handshake', time.time()])
                self.cmdNotify()
            elif method == 'newpage':
                self._cmd_list = self.genCreateUICMDList()
                self.cmdNotify()
            elif method == 'heartbeat':
                self._ui_heart_beat = time.time()
            else:
                print('[undef] ', method, kwargs)
            return jsonify({'status': 'ok'})

        @app.route('/png_blob', methods=['GET'])
        def png_blob():
            # print('[png_blob] ', request.get_json())
            png = b''
            # params = request.get_json()
            params = request.args
            element = self.getElement(params.get('target_id'))
            assert element is not None, f'[error] png_blob undef target_id: {params.get("target_id")}'
            im_id = int(params.get('im_id', -1))
            # attr = params.get('attr')
            # assert attr in ['image', 'content'], f'[error] undef attr {attr}'
            # if attr == 'image':
            img = wrapFlaskElement(element, self).getImage(im_id)

            return send_file(
                BytesIO(img.png),
                mimetype='image/png'
                )

        @app.route('/jpeg_blob', methods=['GET'])
        def jpeg_blob():
            # print('[png_blob] ', request.get_json())
            jpeg = b''
            params = request.args
            element = self.getElement(params.get('target_id'))
            assert element is not None, f'[error] png_blob undef target_id: {params.get("target_id")}'
            im_id = int(params.get('im_id', -1))
            img = wrapFlaskElement(element, self).getImage(im_id)

            return send_file(
                BytesIO(img.jpeg),
                mimetype='image/jpeg'
                )

        @app.route('/video_feed', methods=['GET'])
        def video_feed():
            params = request.args
            element = self.getElement(params.get('target_id'))
            assert element is not None, f'[error] png_blob undef target_id: {params.get("target_id")}'
            # attr = params.get('attr')
            # assert attr in ['image', 'contents'], f'[error] undef attr {attr}'
            im_id = int(params.get('im_id', -1))
            image = wrapFlaskElement(element, self).getImage(im_id)

            def generateVideoFrame(image: zlimage):
                condition_new = image.getCondition('new_image')
                # yield b'--frame\r\n'
                while (True):
                    if image is None:
                        break
                    else:
                        # print(video.video_frame.jpeg)
                        yield (
                             b'--zlooo\r\n' + b'Content-Type: image/jpeg\r\n\r\n' + image.jpeg + b'\r\n'
                            )
                    with condition_new:
                        condition_new.wait()

            return Response(
                generateVideoFrame(image),
                mimetype='multipart/x-mixed-replace; boundary=zlooo'
                )

        @app.errorhandler
        def handle_timeout(e):
            print(e)
        # 排除日志
        import logging

        class RouteFilter(logging.Filter):
            def filter(self, record):
                # 检查日志消息中是否包含 /mjpeg 路径
                blocks = ['/cmd', '/api', '/png_blob', '/jpeg_blob']
                msgs = record.getMessage()
                for block in blocks:
                    if block in msgs:
                        return False
                return True
                # return '/png_blob' not in record.getMessage()

        werkzeug_log = logging.getLogger('werkzeug')
        werkzeug_log.addFilter(RouteFilter())
        return app

    def show(self, openbrowser=True, **kwargs):
        from werkzeug.serving import make_server
        self.attr._update(kwargs)
        self.app = self.createApp()
        self.server = make_server(
            host=self.attr.host,
            port=self.attr.port,
            app=self.app,
            threaded=True
            )
        # self.cmd_cache = OrderedDict()
        print(f'host: {self.attr.host}:{self.attr.port}')
        # print(f'local: {self.webui_local_url}')
        # self.printUITree()
        # debug
        local_url = f'http://127.0.0.1:{self.attr.port}'
        if openbrowser:
            import webbrowser
            webbrowser.open(local_url, new=0, autoraise=True)
        self.server.serve_forever()
        return self
