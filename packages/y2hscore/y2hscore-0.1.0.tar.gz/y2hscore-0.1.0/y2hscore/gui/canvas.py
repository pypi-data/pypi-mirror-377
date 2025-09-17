import tkinter

class Canvas( tkinter.Canvas ):
    
    def __init__( self, master ):
        
        _               =   super( ).__init__( master = master, background = "white" )
        
        self.command    =   None
        self.file       =   None
        self.image      =   None
        self.mode       =   0
        self.offset     =   [ 0, 0 ]
        self.scale      =   1
        
        _               =   self.bind( sequence = "<Configure>", func = self.on_resize )
        _               =   self.tag_bind( tagOrId = "Image", sequence = "<Button>", func = self.on_click )
        
        return
    
    def add_image( self, file ):
        
        self.file       =   file
        _               =   self.refresh( )
        
        return
    
    def change_mode( self, mode, command ):
        
        self.mode       =   mode
        self.command    =   command
        
        _               =   self.refresh( )
        
        return
    
    def on_click( self, event ):
        
        x               =   int( ( event.x - self.offset[ 0 ] ) / self.scale )
        y               =   int( ( event.y - self.offset[ 1 ] ) / self.scale )
        
        if ( self.command is not None ):
            
            _               =   self.command( x = x, y = y )
        
        return
    
    def on_resize( self, event ):
        
        _               =   self.refresh( )
        
        return
    
    def refresh( self ):
        
        _               =   self.delete( "Image" )
        
        if ( self.file is None ):
            return
        
        canvas_width    =   self.winfo_width( )
        canvas_height   =   self.winfo_height( )
        
        ppm, self.scale, self.offset    =   self.file.draw_ppm( mode = self.mode, preferred_width = canvas_width, preferred_height = canvas_height )
        
        self.image      =   tkinter.PhotoImage( data = ppm )
        
        _               =   self.create_image( self.offset[ 0 ], self.offset[ 1 ], anchor = tkinter.NW, image = self.image, tags = [ "Image", ] )
        
        _               =   self.update_idletasks( )
        
        return
    
    def remove_image( self ):
        
        self.file       =   None
        self.image      =   None
        
        _               =   self.refresh( )
        
        return