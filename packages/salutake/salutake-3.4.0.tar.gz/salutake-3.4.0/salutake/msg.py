codes ={
    200: 'success',
    201: 'Auth failed',
    202: 'Missing Manditory Params. See data object for missing params in "records"',
    203: 'Controller disabled',
    204: 'Scheduling failed',
    205: 'Password Mismatch',
    206: 'Oops Something Went Wrong. Try a new user name.',
    207: 'Username does not exist.',
    208: 'Invalid Param Type Cast',
    209: 'Values in submission must be unique',
    210: 'Invalid identifiers',
    290: 'Api Error',
    291: 'Api server message format error : missing param method',
    292: 'Api server message format error : unregistered method',
    293: 'Api server method error',
}


class Response:
    def __init__(self, res =None):
        self.res = dict({'success': True, 'data': {}, 'response_code': 200, 'msg': 'success'})

        if isinstance(res, Response):
            self.data(Response.msg['data'])
            tmp = Response
            tmp.pop('data')
            self.res = dict(**self.res, **tmp)

    # def __repr__(self):
    #     return repr(self.res)

    def fail(self, err_code):
        self.res['success'] = False
        self.res['response_code'] = err_code
        self.res['msg'] = codes[err_code]
        return self
    def success(self):
        return self.res['success']
    def data(self, data):
        if isinstance(data, list):
            self.res['data'] = dict(**self.res['data'], **{'records': data})
            return self

        if not isinstance(data, dict):
            raise TypeError('data object must be of type dict or list')
            return

        self.res['data'] = dict(**self.res['data'], **data)
        return self

    def msg(self):
        return self.res



