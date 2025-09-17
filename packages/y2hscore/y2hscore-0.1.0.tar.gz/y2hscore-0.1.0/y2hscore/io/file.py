import cv2
import numpy

from ..processing   import draw
from ..processing   import grid

class File( ):
    
    def __init__( self, path, data_extension, grid_size ):
        
        self.path       =   path
        self.ext_data   =   data_extension
        self.grid_size  =   grid_size
        
        self.filename   =   ".".join( self.path.split( "/" )[ -1 ].split( "." )[ 0 : -1 ] )
        
        _               =   self.load_data( )
        _               =   self.load_image( )
        
        self.select     =   -1
        self.points     =   [ ]
        
        return
    
    def draw( self, mode, preferred_width, preferred_height ):
        
        if ( mode == 0 ):
            
            elements        =   draw.scores( positions = self.grid, values = self.scores, highlight = -1 )
            
            label           =   ""
        
        elif ( mode == 1 ):
            
            elements        =   draw.scores( positions = self.grid, values = self.scores, highlight = self.select )
            
            labels          =   [ "Select value " + chr( y + 65 ) + str( x + 1 ) for x in range( self.grid_size[ 0 ] ) for y in range( self.grid_size[ 1 ] ) ] + [ "" ]
            label           =   labels[ self.select ]
        
        elif ( mode == 2 ):
            
            elements        =   draw.grid( positions = self.points, grid_size = self.grid_size  )
            
            labels          =   [ "Select top left", "Select top right", "Select bottom right", "Select bottom left" ] + [ "" ]
            label           =   labels[ len( self.points ) ]
        
        return draw.draw( image = self.image, preferred_width = preferred_width, preferred_height = preferred_height, elements = elements, left_label = self.filename, right_label = label )
    
    def draw_ppm( self, mode, preferred_width, preferred_height ):
        
        data, scale, offset =   self.draw( mode, preferred_width, preferred_height )
        
        return draw.ppm( data ), scale, offset
    
    def load_data( self ):
        
        datafile        =   ".".join( self.path.split( "." )[ 0 : -1 ] ) + self.ext_data
        
        try:
            
            data            =   numpy.loadtxt( fname = datafile, dtype = int, delimiter = "," )
            self.grid       =   data[ :, 0 : 2 ]
            self.scores     =   data[ :,     2 ]
        
        except:
            
            self.grid       =   numpy.zeros( shape = ( self.grid_size[ 0 ] * self.grid_size[ 1 ], 2 ), dtype = int ) - 10
            self.scores     =   numpy.zeros( shape = ( self.grid_size[ 0 ] * self.grid_size[ 1 ]    ), dtype = int )
        
        return
    
    def load_image( self ):
        
        data            =   numpy.fromfile( file = self.path, dtype = numpy.uint8 )
        self.image      =   cv2.imdecode( buf = data, flags = cv2.IMREAD_COLOR_BGR )
        
        return
    
    def grid_detect( self ):
        
        self.grid       =   grid.detect( image = self.image, grid_x = self.grid_size[ 0 ], grid_y = self.grid_size[ 1 ] )
        
        return
    
    def grid_select( self ):
        
        self.grid       =   grid.match( edgepoints = self.points, grid_x = self.grid_size[ 0 ], grid_y = self.grid_size[ 1 ] )
        
        return
    
    def nearest_point( self, point ):
        
        tolerance       =   ( self.grid[ 1, 1 ] - self.grid[ 0, 1 ] ) / 2
        
        distances       =   numpy.linalg.norm( self.grid - point, axis = 1 )
        
        index           =   int( numpy.argmin( distances ) )
        distance        =   numpy.amin( distances )
        
        if ( distance > tolerance ):
            index           =   -1
        
        return index
    
    def save_data( self ):
        
        datafile        =   ".".join( self.path.split( "." )[ 0 : -1 ] ) + self.ext_data
        
        data            =   numpy.concatenate( ( self.grid, self.scores[ :, numpy.newaxis ] ), axis = 1 )
        _               =   numpy.savetxt( fname = datafile, X = data, fmt = "%d", delimiter = "," )
        
        return
    
    def save_image( self, preferred_width, preferred_height, filetype ):
        
        imagefile       =   ".".join( self.path.split( "." )[ 0 : -1 ] ) + filetype
        
        data, scale, offset =   self.draw( mode = 0, preferred_width = preferred_width, preferred_height = preferred_height )
        retval, buf         =   cv2.imencode( ext = filetype, img = data )
        _                   =   buf.tofile( file = imagefile )
        
        return
    
    def scores_detect( self, model ):
        
        self.scores    =   model.predict( image = self.image, positions = self.grid )
        
        return
    
    def scores_next( self ):
        
        self.select     =   ( self.select + 1 ) % ( self.grid_size[ 0 ] * self.grid_size[ 1 ] )
        
        return
    
    def scores_reset( self ):
        
        self.scores    =   numpy.zeros( shape = ( len( self.scores ), ), dtype = int )
        
        return
    
    def scores_select( self, index, score ):
        
        self.scores[ index ]    =   score
        
        return