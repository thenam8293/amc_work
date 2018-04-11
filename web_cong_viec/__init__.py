"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__,static_url_path='/static')

import web_cong_viec.views
