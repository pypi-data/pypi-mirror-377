import cv2

red             =   (  66,  13, 210 )
green           =   (  70, 189, 138 )
blue            =   ( 133,  85,  19 )

def draw( image, preferred_width, preferred_height, elements, left_label, right_label ):
    
    scale           =   1 / max( image.shape[ 1 ] / preferred_width, image.shape[ 0 ] / preferred_height )
    image           =   cv2.resize( src = image, dsize = ( 0, 0 ), fx = scale, fy = scale )
    offset          =   [ ( preferred_width - image.shape[ 1 ] ) // 2, ( preferred_height - image.shape[ 0 ] ) // 2 ]
    
    size            =   cv2.getTextSize( text = left_label, fontFace = cv2.FONT_HERSHEY_SIMPLEX, fontScale = 1, thickness = 2 )
    
    x               =   10
    y               =   10 + size[ 0 ][ 1 ]
    
    _               =   cv2.putText( img = image, text = left_label, org = ( x, y ), fontFace = cv2.FONT_HERSHEY_SIMPLEX, fontScale = 1, color = red, thickness = 2 )
    
    size            =   cv2.getTextSize( text = right_label, fontFace = cv2.FONT_HERSHEY_SIMPLEX, fontScale = 1, thickness = 2 )
    
    x               =   10 + size[ 0 ][ 0 ] - image.shape[ 1 ]
    y               =   10 + size[ 0 ][ 1 ]
    
    _               =   cv2.putText( img = image, text = right_label, org = ( -x, y ), fontFace = cv2.FONT_HERSHEY_SIMPLEX, fontScale = 1, color = red, thickness = 2 )
    
    for [ x, y, text, color ] in elements:
        
        size            =   cv2.getTextSize( text = text, fontFace = cv2.FONT_HERSHEY_SIMPLEX, fontScale = 1, thickness = 2 )
        
        x               =   int( x * scale ) - size[ 0 ][ 0 ] // 2
        y               =   int( y * scale ) + size[ 0 ][ 1 ] // 2
        
        _               =   cv2.putText( img = image, text = text, org = ( x, y ), fontFace = cv2.FONT_HERSHEY_SIMPLEX, fontScale = 1, color = color, thickness = 2 )
    
    return image, scale, offset

def grid( positions, grid_size ):
    
    elements        =   [ ]
    
    for position in positions:
        
        elements        =   elements + [ [ position[ 0 ], position[ 1 ], "X", red ] ]
    
    for i in range( len( positions ) - 1 ):
        
        steps           =   ( grid_size[ i % 2 ] - 1 )
        
        step_x          =   ( positions[ i + 1 ][ 0 ] - positions[ i ][ 0 ] ) / steps
        step_y          =   ( positions[ i + 1 ][ 1 ] - positions[ i ][ 1 ] ) / steps
        
        start_x         =   positions[ i ][ 0 ]
        start_y         =   positions[ i ][ 1 ]
        
        for j in range( 1, steps ):
            
            position        =   [ start_x + j * step_x, start_y + j * step_y ]
            elements        =   elements + [ [ position[ 0 ], position[ 1 ], "*", blue ] ]
    
    return elements

def ppm( image ):
    
    header          =   "P6 " + str( image.shape[ 1 ] ) + " " + str( image.shape[ 0 ] ) + " 255 "
    rgb             =   cv2.cvtColor( image, cv2.COLOR_BGR2RGB )
    ppm             =   header.encode( ) + rgb.tobytes( )
    
    return ppm

def scores( positions, values, highlight ):
    
    elements        =   [ ]
    
    for i, [ position, value ] in enumerate( zip( positions, values ) ):
        
        if ( i == highlight ):
        
            value           =   "_"
            color           =   green
        
        elif ( value == 0 ):
            
            value           =   "*"
            color           =   blue
        
        elif ( value == -1 ):
            
            value           =   "X"
            color           =   red
        
        else:
            
            value           =   str( value )
            color           =   red
            
        elements        =   elements + [ [ position[ 0 ], position[ 1 ], value, color ] ]
    
    return elements