from .core.element import *

def createUI(backends='flask', **kwargs):

    from .backends.flask import FlaskUI

    backends_map = {
        'flask': FlaskUI
        }

    if backends in backends_map:
        return backends_map[backends](**kwargs)

    raise RuntimeError(f'[error] undef backends {backends} of {list(backends_map.keys())}')
