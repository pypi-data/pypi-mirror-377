from functools import wraps
from flask import Flask, request, jsonify, redirect, session
from salutake import msg
import numpy as np
import pprint as pp

def validateParams(manditory,req):

    return all(k in req for k in manditory)


def Auth():

    if 'auth' in session:
        return int(session['auth'])
    return False


def requestVars( manditory=[], authLevel=1):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ath = Auth()
            if not ath or ath < authLevel:
                return redirect('/')
            if request.is_json:
                p = request.get_json(force=True)
            else:
                p = request.args.to_dict()
            if len(manditory):
                if not validateParams(manditory, p):
                    return jsonify(msg.Response().fail(202).data(np.setdiff1d(manditory, list(p.keys())).tolist()).msg())
            if 'symbol' in p:
                p['symbol'] = str(p['symbol']).lower()
            return f(p,)
        return wrapper
    return decorator


def apiAuth(db, manditory=[], authLevel=1):

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            if request.is_json:
                p = request.get_json()
            else:
                p = request.args.to_dict()

            if len(manditory):
                if not validateParams(manditory, p):
                    return jsonify(msg.Response().fail(202).data(np.setdiff1d(manditory, p).tolist()).msg())
            #if not choke.authenticate(db, p['username'], p['password']):
                #pass
                #return jsonify(msg.Response().fail(201).msg())

            return f(p,)
        return wrapper
    return decorator