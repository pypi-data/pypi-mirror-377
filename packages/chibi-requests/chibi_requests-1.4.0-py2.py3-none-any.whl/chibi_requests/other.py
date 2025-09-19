from .response import Response


class Force_json( Response ):
    @property
    def is_json( self ):
        return True
