
from os import environ
from web_cong_viec import app
from gevent.pywsgi import WSGIServer
from gevent import monkey
monkey.patch_all()
from gevent import wsgi

print 'WEB AMC'

if __name__ == '__main__':
    app.debug = True
    http = WSGIServer(('10.62.24.161', 6868), app.wsgi_app)
    http.serve_forever()
    
# from os import environ
# from web_cong_viec import app

# if __name__ == '__main__':
#     app.debug = True
#     HOST = environ.get('server_host', '10.62.24.161')
# ##    NAME = environ.get('server_name','phu.co.tcb.vn:5555')
# ##    HOST = environ.get('server_host', 'localhost')
#     try:
#         PORT = int(environ.get('8080', '6868'))
# ##        PORT = int(environ.get('server_port', '5555'))
#     except ValueError:
#         PORT = 6868
#     app.run(HOST, PORT, threaded = True)