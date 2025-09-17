import cv2
import numpy

import importlib.resources

class CNN( cv2.dnn.Net ):
    
    def __init__( self ):
        
        _               =   super( ).__init__( )
        
        path            =   str( importlib.resources.files( __package__ ).joinpath( "weights" ) )
        
        layer           =   [
                                { "type": "Convolution",    "params": { "num_output": 32, "kernel_size": 3, "dilation":  1 },   "blobs": [ "conv_1_kernel.npy", "conv_1_bias.npy" ] },
                                { "type": "ReLU",           "params": { "negative_slope": 0.3 }                             ,   "blobs": [                                        ] },
                                { "type": "Convolution",    "params": { "num_output": 32, "kernel_size": 3, "dilation":  2 },   "blobs": [ "conv_2_kernel.npy", "conv_2_bias.npy" ] },
                                { "type": "ReLU",           "params": { "negative_slope": 0.3 }                             ,   "blobs": [                                        ] },
                                { "type": "Convolution",    "params": { "num_output": 32, "kernel_size": 3, "dilation":  4 },   "blobs": [ "conv_3_kernel.npy", "conv_3_bias.npy" ] },
                                { "type": "ReLU",           "params": { "negative_slope": 0.3 }                             ,   "blobs": [                                        ] },
                                { "type": "Convolution",    "params": { "num_output": 32, "kernel_size": 3, "dilation":  8 },   "blobs": [ "conv_4_kernel.npy", "conv_4_bias.npy" ] },
                                { "type": "ReLU",           "params": { "negative_slope": 0.3 }                             ,   "blobs": [                                        ] },
                                { "type": "Convolution",    "params": { "num_output": 32, "kernel_size": 3, "dilation": 16 },   "blobs": [ "conv_5_kernel.npy", "conv_5_bias.npy" ] },
                                { "type": "ReLU",           "params": { "negative_slope": 0.3 }                             ,   "blobs": [                                        ] },
                                { "type": "Convolution",    "params": { "num_output": 64, "kernel_size": 3, "dilation": 32 },   "blobs": [ "conv_6_kernel.npy", "conv_6_bias.npy" ] },
                                { "type": "ReLU",           "params": { "negative_slope": 0.3 }                             ,   "blobs": [                                        ] },
                                { "type": "Convolution",    "params": { "num_output": 32, "kernel_size": 5, "dilation":  1 },   "blobs": [ "conv_7_kernel.npy", "conv_7_bias.npy" ] },
                                { "type": "ReLU",           "params": { "negative_slope": 0.3 }                             ,   "blobs": [                                        ] },
                                { "type": "Convolution",    "params": { "num_output":  6, "kernel_size": 1, "dilation":  1 },   "blobs": [ "conv_8_kernel.npy"                    ] }
                            ]
        
        for i, layer in enumerate( layer ):
            
            _               =   self.addLayerToPrev( name = "Layer_" + str( i ).zfill( 3 ), type = layer[ "type" ], params = layer[ "params" ], dtype = cv2.CV_32F )
            
            layer_id        =   self.getLayer( layerName = "Layer_" + str( i ).zfill( 3 ) )
            layer_id.blobs  =   [ numpy.load( file = path + "/" + blob ) for blob in layer[ "blobs" ] ]
        
        return
    
    def predict( self, image, positions ):
        
        size            =   131
        inputs          =   self.preprocess( image = image, positions = positions, size = size )
        
        inputs          =   numpy.transpose( inputs, axes = [ 0, 3, 1, 2 ] )
        _               =   self.setInput( blob = inputs )
        outputs         =   self.forward( )
        
        return numpy.argmax( numpy.squeeze( outputs ), axis = 1 )
    
    def preprocess( self, image, positions, size ):
        
        scale           =   ( ( size - 1 ) / 2 ) / ( positions[ 1, 1 ] - positions[ 0, 1 ] )
        crop_size       =   size
        
        image           =   cv2.resize( src = image, dsize = ( 0, 0 ), fx = scale, fy = scale )
        gray            =   cv2.cvtColor( src = image, code = cv2.COLOR_BGR2GRAY )
        clahe           =   cv2.createCLAHE( clipLimit = 1, tileGridSize = ( 9, 9 ) ).apply( src = gray )
        
        features        =   numpy.concatenate( ( image, gray[ ..., numpy.newaxis ], clahe[ ..., numpy.newaxis ] ), axis = -1 )
        
        pad_size        =   ( crop_size - 1 ) // 2
        padded          =   numpy.pad( features, pad_width = ( ( pad_size, pad_size ), ( pad_size, pad_size ), ( 0, 0 ) ), mode = "constant", constant_values = ( 0 ) )
        
        crops           =   numpy.zeros( shape = ( len( positions ), crop_size, crop_size, features.shape[ 2 ] ), dtype = padded.dtype )
        
        for i in range( len( positions ) ):
            
            x               =   int( positions[ i, 0 ] * scale )
            y               =   int( positions[ i, 1 ] * scale )
            
            crops[ i ]      =   padded[ y : y + crop_size, x : x + crop_size ]
        
        averages        =   numpy.mean( crops[ ..., 3 ], axis = 0, dtype = int )
        repeats         =   numpy.repeat( averages[ numpy.newaxis, ..., numpy.newaxis ], repeats = len( crops ), axis = 0 )
        
        return numpy.concatenate( ( crops, repeats ), axis = -1 )