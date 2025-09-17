import cv2
import numpy

compute_x       =   960
compute_y       =   540

ratio           =   0.7

def align( grid, reference_ids, targets ):
    
    references      =   numpy.asarray( grid )[ numpy.asarray( reference_ids ) ]
    
    references      =   numpy.concatenate( ( references, numpy.ones( shape = ( len( references ), 1 ) ) ), axis = 1 )
    targets         =   numpy.concatenate( ( targets, numpy.ones( shape = ( len( targets ), 1 ) ) ), axis = 1 )
    
    transform       =   numpy.linalg.lstsq( a = references, b = targets )
    
    grid            =   numpy.concatenate( ( grid, numpy.ones( shape = ( len( grid ), 1 ) ) ), axis = 1 )
    grid            =   numpy.dot( a = grid, b = transform[ 0 ] )
    
    return grid[ :, : 2 ]

def align_blobs( grid, blobs ):
    
    tolerance       =   ( grid[ 1, 1 ] - grid[ 0, 1 ] ) / 3
    
    for step in range( 8 ):
        
        distances       =   numpy.linalg.norm( grid[ :, numpy.newaxis, : ] - blobs[ numpy.newaxis, :, : ] , axis = 2 )
        
        indices         =   numpy.argmin( distances, axis = 1 )
        distances       =   numpy.amin( distances, axis = 1 )
        
        mask            =   distances > tolerance
        indices[ mask ] =   -1
        matches         =   indices > -1
        
        if ( sum( matches ) < 4 ):
            break
        
        grid          =   align( grid = grid, reference_ids = matches, targets = blobs[ indices[ matches ] ] )
    
    return grid

def center_dish( dish, grid_x, grid_y ):
    
    position_x      =   dish[ 0 ]
    position_y      =   dish[ 1 ]
    radius          =   dish[ 2 ]
    
    step_x          =   2 * radius * ratio / ( grid_x - 1 )
    step_y          =   step_x
    
    start_x         =   position_x - ( grid_x - 1 ) / 2 * step_x
    start_y         =   position_y - ( grid_y - 1 ) / 2 * step_y
    
    grid            =   [ [ start_x + x * step_x, start_y + y * step_y ] for x in range( grid_x ) for y in range( grid_y ) ]
    
    return numpy.asarray( grid )

def detect( image, grid_x, grid_y ):
    
    compute_scale   =   1 / max( image.shape[ 1 ] / compute_x, image.shape[ 0 ] / compute_y )
    compute         =   cv2.resize( src = image, dsize = ( 0, 0 ), fx = compute_scale, fy = compute_scale )
    
    compute         =   cv2.cvtColor( src = compute, code = cv2.COLOR_BGR2GRAY )
    
    compute         =   cv2.createCLAHE( clipLimit = 1, tileGridSize = ( 15, 15 ) ).apply( src = compute )
    
    dish            =   cv2.HoughCircles( image = compute, method = cv2.HOUGH_GRADIENT, dp = 1, minDist = 1, minRadius = 150, maxRadius = 400 )
    dish            =   dish[ 0, 0 ]
    
    params                      =   cv2.SimpleBlobDetector_Params( )
    params.blobColor            =   255
    params.minArea              =   80
    params.maxArea              =   800
    params.filterByConvexity    =   False
    
    blobs           =   cv2.SimpleBlobDetector.create( parameters = params ).detect( image = compute )
    blobs           =   cv2.KeyPoint.convert( keypoints = blobs )
    
    distance        =   numpy.linalg.norm( blobs - dish[ 0 : 2 ], axis = 1 )
    tolerance       =   distance < dish[ 2 ] * 0.9
    blobs           =   blobs[ tolerance ]
    
    grid            =   center_dish( dish = dish, grid_x = grid_x, grid_y = grid_y )
    
    grid            =   align_blobs( grid = grid, blobs = blobs )
    
    return numpy.asarray( grid / compute_scale, dtype = int )

def match( edgepoints, grid_x, grid_y ):
    
    start_x         =   ( grid_x - 1 ) / 2
    start_y         =   ( grid_y - 1 ) / 2
    
    grid            =   [ [ start_x + x, start_y + y ] for x in range( grid_x ) for y in range( grid_y ) ]
    
    reference_ids   =   [ 0, -8, -1, 7 ]
    
    return align( grid = grid, reference_ids = reference_ids, targets = edgepoints )