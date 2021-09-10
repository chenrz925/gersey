from typing import Text

import uvicorn
from fastapi import FastAPI

from . import __version__


class Guard(object):
    api = FastAPI(title='geyser-guard', version=__version__)

    @api.post('/gush/{id}')
    def gush(self, id: Text):
        pass

    @classmethod
    def entry(cls):
        return uvicorn.run('geyser.guard:Guard.api', host="0.0.0.0", port=9999)
