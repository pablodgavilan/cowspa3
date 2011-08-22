import os
import sys
from jsonrpc2 import JsonRpc
import simplejson

path = os.path.abspath(os.getcwd())
sys.path.insert(0, '.')
sys.path.insert(0, '..')

from flask import Flask, jsonify, url_for, session, redirect, request
app = Flask(__name__)
app.secret_key = os.urandom(24)

static_root = 'pub'
import be.apis.user as userlib
import be.bootstrap
be.bootstrap.start('conf_test')
import be.apps
cowspa = be.apps.cowspa

@app.route('/search_members', methods=['GET', 'POST'])
def search_members():
    auth_token = request.cookies.get('authcookie')
    cowspa.tr_start()
    if auth_token:
        userlib.set_context(auth_token)
    params = {"jsonrpc": "2.0", "method": "member.search", "params": {'q':request.args['q']}, "id": 1}
    data = cowspa.mapper(params)
    cowspa.tr_complete()
    if 'result' in data:
        return simplejson.dumps(data['result'])
    else:
        return jsonify(data)

@app.route('/app', methods=['GET', 'POST'])
def api_dispatch():
    params = request.json
    auth_token = request.cookies.get('authcookie')
    cowspa.tr_start()
    if auth_token:
        userlib.set_context(auth_token)
    #params = rpc({"jsonrpc": "2.0", "method": methodname, "params": params, "id": 1})
    data = cowspa.mapper(params)
    cowspa.tr_complete()
    if params['method'] == 'login' and 'result' in data:
        auth_token = data['result']
        resp = jsonify(data)
        resp.set_cookie('authcookie',value=auth_token)
        resp.set_cookie('user_id',value=env.context.user_id)
        resp.set_cookie('roles',value=env.context.roles)
        return resp
    return jsonify(data)

@app.route('/<path:path>', methods=['GET'])
def static(path):
    fspath = os.path.join(static_root, path)
    filename = os.path.basename(path)
    if '.' in path:
        content_type = "text/" + path.split('.')[-1]
    else:
        content_type = "text/html"
    return file(fspath).read(), 200, {'Content-Type': content_type +'; charset=utf-8'}

if __name__ == '__main__':
    app.run('0.0.0.0',debug=True) # Threaded
    from gevent.wsgi import WSGIServer

    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()