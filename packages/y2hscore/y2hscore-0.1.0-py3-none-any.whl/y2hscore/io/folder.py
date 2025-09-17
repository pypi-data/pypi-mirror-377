import numpy
import os

from ..io.file      import File

class Folder( ):
    
    def __init__( self, path, image_extensions, data_extension, grid_size ):
        
        self.path       =   path
        self.ext_img    =   image_extensions
        self.ext_data   =   data_extension
        self.grid_size  =   grid_size
        
        self.files      =   [ path + "/" + file for file in os.listdir( self.path ) if file.lower( ).endswith( self.ext_img ) ]
        self.index      =   -1
        
        self.length     =   len( self.files )
        
        return
    
    def export( self, path ):
        
        data            =   self.load_data( )
        
        header          =   numpy.asarray( [ chr( y + 65 ) + str( x + 1 ) for x in range( self.grid_size[ 0 ] ) for y in range( self.grid_size[ 1 ] ) ] )
        index           =   numpy.asarray( [ ".".join( file.split( "/" )[ -1 ].split( "." )[ 0 : -1 ] ) for file in self.files ] )
        
        table           =   numpy.empty( ( data.shape[ 0 ] + 1, data.shape[ 1 ] + 1 ), dtype = object )
        
        table[     0,     0 ]    =   ""
        table[     0, 1 :   ]    =   header
        table[ 1 :  ,     0 ]    =   index
        table[ 1 :  , 1 :   ]    =   data.astype( str )
        
        _               =   numpy.savetxt( fname = path, X = table, fmt = "%s", delimiter = "," )
        
        return
    
    def load( self ):
        
        return File( path = self.files[ self.index ], data_extension = self.ext_data, grid_size = self.grid_size )
    
    def load_data( self ):
        
        data            =   numpy.zeros( shape = ( self.length, self.grid_size[ 0 ] * self.grid_size[ 1 ], 3 ), dtype = int )
        
        for i, file in enumerate( self.files ):
            
            datafile        =   ".".join( file.split( "." )[ 0 : -1 ] ) + self.ext_data
            
            try:
                
                data[ i ]       =   numpy.loadtxt( fname = datafile, dtype = int, delimiter = "," )
            
            except:
                
                pass
        
        return data[ :, :, 2 ]
    
    def next( self ):
        
        self.index      =   ( self.index + 1 ) % len( self.files )
        
        return self.load( )
    
    def previous( self ):
        
        self.index      =   ( self.index - 1 ) % len( self.files )
        
        return  self.load( )