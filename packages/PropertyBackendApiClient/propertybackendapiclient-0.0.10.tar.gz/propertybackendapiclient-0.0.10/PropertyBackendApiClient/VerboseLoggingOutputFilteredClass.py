from PythonAPIClientBase import VerboseLoggingOutputAllClass

class VerboseLoggingOutputFilteredClass(VerboseLoggingOutputAllClass):
    surpress_payload_urlending_list = None

    def __init__(self, call=True, include_data=True, result=True, surpress_payload_urlending_list=[]):
        super().__init__(call=call, include_data=include_data, result=result)
        self.surpress_payload_urlending_list = surpress_payload_urlending_list

    def log_call(
        self,
        reqFn,
        url,
        params,
        data,
        headers,
        postRefreshCall
    ):
        for urlending in self.surpress_payload_urlending_list:
            if urlending == url[-len(urlending):]:
                return
        super().log_call(reqFn=reqFn, url=url, params=params, data=data, headers=headers, postRefreshCall=postRefreshCall)