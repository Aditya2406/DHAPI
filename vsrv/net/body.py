'''
    vsrv - HTTP - Base Response Body
'''
class HTTPBody():
    '''
        vSys - Base Class for Response
    '''

    def __init__(self,status_code_:int=200, status_message_:str = '', data:dict|str|None = None ) -> None:
        '''
            Constructor
        '''
        self.StatusCode = status_code_
        self.StatusMessage = status_message_
        self.Data = data

    def body(self):
        '''
            Dictionary Representation
        '''
        return {
            "statusCode" : self.StatusCode,
            "statusMessage" : self.StatusMessage,
            "data" : self.Data
        }
        