import json
import copy
import logging
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

import requests
from chibi.atlas import Chibi_atlas, Chibi_atlas_default
from chibi.file import Chibi_path
from chibi.metaphors import Book
from requests import Session
from requests.auth import AuthBase

from chibi_requests.response import Response


logger = logging.getLogger( 'chibi_requests.chibi_url' )


class Chibi_url( str ):
    def __new__( cls, *args, headers=None, **kw ):
        obj = str.__new__( cls, *args )
        obj.response_class = kw.pop( 'response_class', Response )
        obj.kw = Chibi_atlas( kw )
        if headers is None:
            obj._headers = Chibi_atlas_default( str )
        else:
            obj._headers = Chibi_atlas_default( str, headers )
        return obj

    def __add__( self, other ):
        if isinstance( other, Chibi_url ):
            raise NotImplementedError
        elif isinstance( other, str ):
            return self.__add__str__( other )
        elif isinstance( other, dict ):
            return self.__add__dict__( other )
        elif isinstance( other, Book ):
            return self.__add__book__( other )
        elif isinstance( other, AuthBase ):
            return self.__add__auth__( other )
        elif isinstance( other, Session ):
            return self.__add__session__( other )
        elif isinstance( other, int ):
            return self.__add__str__( str( other ) )
        else:
            raise NotImplementedError(
                f"no esta implementada la suma con el tipo "
                f"'{type(other)}' de {other}" )

    def __iadd__( self, other ):
        if isinstance( other, AuthBase ):
            return self.__iadd__auth__( other )
        elif isinstance( other, Session ):
            return self.__iadd__session__( other )
        else:
            raise NotImplementedError(
                f"no esta implementada la suma con el tipo "
                f"'{type(other)}' de {other}" )

    def __eq__( self, other ):
        if isinstance( other, Chibi_url ):
            return str( self ) == str( other ) and self.kw == other.kw
        if isinstance( other, str ):
            return str( self ) == other
        return False

    def __hash__( self ):
        return hash( str( self ) )

    def __copy__( self ):
        kw = vars( self )
        v = kw[ 'kw' ]
        kw = dict( **kw, **v )
        del kw[ 'kw' ]
        return type( self )( self, **kw, headers=self.headers )

    @property
    def base_name( self ):
        if self.url[-1] == '/':
            return self.url.rsplit( '/', 2 )[-2]
        return self.url.rsplit( '/', 1 )[-1]

    @property
    def dir_name( self ):
        if self.url[-1] == '/':
            return self.url.rsplit( '/', 2 )[-3]
        return type( self )( self.url.rsplit( '/', 1 )[0] )

    @property
    def parts( self ):
        return list( urlparse( self ) )
        try:
            return self._parts
        except AttributeError:
            self._parts = list( urlparse( self ) )
            return self._parts

    @property
    def params( self ):
        current = parse_qs( self.parts[4], keep_blank_values=True )
        for k, v in current.items():
            if isinstance( v, list ) and len( v ) == 1:
                current[k] = v[0]
        return Chibi_atlas( current )

    @property
    def schema( self ):
        return self.parts[0]

    @property
    def host( self ):
        return self.parts[1]

    @property
    def path( self ):
        return self.parts[2]

    @property
    def url( self ):
        parts = self.parts
        parts[4] = ''
        return type( self )( urlunparse( parts ) )

    def format( self, *args, **kw ):
        result = super().format( *args, **kw )
        return type( self )(
            result, response_class=self.response_class, **kw, **self.kw )

    def get( self, *args, **kw ):
        logger.info( f'GET "{self}"' )
        args = self._parse_arguments( *args )
        kw.setdefault( 'verify', self.verify )
        response = self.requests.get(
            str( self ), *args, auth=self.auth, headers=self.headers, **kw )
        return self.response_class( response, self )

    def post( self, *args, **kw ):
        logger.info( f'POST "{self}"' )
        args = self._parse_arguments( *args )
        kw.setdefault( 'verify', self.verify )
        response = self.requests.post(
            str( self ), *args, auth=self.auth, headers=self.headers, **kw )
        return self.response_class( response, self )

    def put( self, *args, **kw ):
        logger.info( f'PUT "{self}"' )
        args = self._parse_arguments( *args )
        kw.setdefault( 'verify', self.verify )
        response = self.requests.put(
            str( self ), *args, auth=self.auth, headers=self.headers, **kw )
        return self.response_class( response, self )

    def delete( self, *args, **kw ):
        logger.info( f'DELETE "{self}"' )
        args = self._parse_arguments( *args )
        kw.setdefault( 'verify', self.verify )
        response = self.requests.delete(
            str( self ), *args, auth=self.auth, headers=self.headers,
            **kw )
        return self.response_class( response, self )

    def download( self, path, *args, chunk_size=8192, **kw ):
        """
        descarga archivos o lo que sea de una url

        Parameters
        ==========
        path: Chibi_path
            ruta donde se descargara el archivo
            si es in directorio usara genera el nombr edel archivo
            usando la url
        chunk_size: int ( optional )
            tamanno de los chunks

        Returns
        =======
        Chibi_path
            ruta del archivo descargado
        """
        path = Chibi_path( path )
        if path.is_a_folder:
            path += self.base_name

        logger.info( f'DOWNLOAD "{self}" into "{path}"' )
        kw.setdefault( 'verify', self.verify )
        response = self.requests.get(
            str( self ), *args, **kw, headers=self.headers,
            auth=self.auth, stream=True, )

        response.raise_for_status()

        f = path.open()
        for chunk in response.iter_content( chunk_size=chunk_size ):
            if chunk:
                f.append( chunk )
        return path

    @property
    def auth( self ):
        try:
            return self.kw.auth
        except AttributeError:
            return None

    @property
    def verify( self ):
        try:
            return self.kw.verify
        except AttributeError:
            return None

    @auth.setter
    def auth( self, value ):
        if isinstance( value, AuthBase ):
            self.kw.auth = value
        else:
            raise NotImplementedError

    @property
    def session( self ):
        try:
            return self.kw.session
        except AttributeError:
            return None

    @session.setter
    def session( self, value ):
        if isinstance( value, Session ):
            self.kw.session = value
        else:
            raise NotImplementedError

    def __add__str__( self, other ):
        if other.startswith( '?' ):
            parts = list( urlparse( self ) )
            current = parse_qs( parts[4], keep_blank_values=True )
            news = parse_qs( other[1:], keep_blank_values=True )
            current.update( news )
            parts[4] = urlencode( current, doseq=True )
            return type( self )(
                urlunparse( parts ),
                response_class=self.response_class, **self.kw )
        elif other.startswith( '/' ):
            parts = list( urlparse( self.url ) )
            parts[2] = other
            return type( self )(
                urlunparse( parts ),
                response_class=self.response_class, **self.kw )
            return type( self )(
                "/".join( self.split( '/' ) + [ other ] ),
                response_class=self.response_class, **self.kw )
        elif other.startswith( 'http' ):
            return type( self )(
                other, response_class=self.response_class, **self.kw )
        else:
            new_url = type( self )(
                "/".join( self.url.split( '/' ) + [ other ] ),
                response_class=self.response_class, **self.kw )
            return new_url + self.params

    def add_subfix( self, string ):
        """
        agrega subfijos a la url

        Parameters
        ----------
        string: str
            una cadena que se agregara al final

        Returns
        -------
        Chibi_url

        Examples
        --------
        >>>Chibi_url( "http://google.com" ).add_subfix( ".json" )
        "http://google.com.json"
        """
        if isinstance( string, str ):
            new_url = type( self )(
                f"{self.url}{string}",
                response_class=self.response_class, **self.kw )
            return new_url + self.params
        else:
            NotImplementedError(
                f"no implementado agregar subfijos de tipo '{type(string)}'" )

    def __add__dict__( self, other ):
        parts = list( urlparse( self ) )
        current = parse_qs( parts[4], keep_blank_values=True )
        current.update( other )
        parts[4] = urlencode( current, doseq=True )
        return type( self )(
            urlunparse( parts ),
            response_class=self.response_class, **self.kw )

    def __add__book__( self, other ):
        return self + other.offset

    def __add__session__( self, other ):
        url = copy.copy( self )
        url += other
        return url

    def __add__auth__( self, other ):
        url = copy.copy( self )
        url += other
        return url

    def __iadd__session__( self, other ):
        self.session = other
        return self

    def __iadd__auth__( self, other ):
        self.auth = other
        return self

    @property
    def requests( self ):
        if self.session:
            return self.session
        else:
            return requests

    @property
    def headers( self ):
        return self._headers

    def _parse_arguments( self, *args ):
        if not args:
            return args
        if self.headers.content_type == 'application/json':
            data = json.dumps( args[0] )
            return tuple( ( data, *args[1:] ) )
