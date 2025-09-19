from requests.auth import AuthBase


class Token( AuthBase ):
    def __init__( self, *, token, name='Token' ):
        self._name = name
        self._token = token

    def __call__( self, request ):
        request.headers[ 'Authorization' ] = f'{self._name} {self._token}'
        return request

    def __str__( self ):
        return f"{self._name} {self._token}"


class Bearer( Token ):
    def __init__( self, *, token, name='Bearer' ):
        super().__init__( token=token, name=name )
