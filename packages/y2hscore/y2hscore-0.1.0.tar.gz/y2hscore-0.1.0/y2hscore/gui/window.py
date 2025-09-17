import tkinter
import tkinter.filedialog

from ..gui.panel    import Panel
from ..gui.canvas   import Canvas

from ..io.folder    import Folder

from ..model.cnn    import CNN

class Window( tkinter.Tk ):
    
    def __init__( self ):
        
        _               =   super( ).__init__( )
        
        self.ext_img    =   ( ".jpg", "jpeg", ".jpe", ".jp2", ".tiff", ".tif" )
        self.ext_data   =   ".csv"
        self.out_img    =   [ 1920, 1080, ".png" ]
        self.grid_size  =   [ 12, 8 ]
        
        self.base_title =   "Y2HScore"
        
        self.elements   =   [
                                [ 1, "Open Folder",    self.folder_open     ],
                                [ 1, "Close Folder",   self.folder_close    ],
                                [ 2, "Images:",        self.count_files     ],
                                [ 0, "-",              None                 ],
                                [ 1, "Process Folder", self.folder_process  ],
                                [ 1, "Export Folder",  self.folder_export   ],
                                [ 2, "Processed:",     self.count_processed ],
                                [ 0, "-",              None                 ],
                                [ 1, "Next Image",     self.file_next       ],
                                [ 1, "Previous Image", self.file_previous   ],
                                [ 1, "Save Image",     self.file_save       ],
                                [ 0, "-",              None                 ],
                                [ 1, "Select Grid",    self.grid_select     ],
                                [ 1, "Detect Grid",    self.grid_detect     ],
                                [ 0, "-",              None                 ],
                                [ 1, "Select Scores",  self.scores_select   ],
                                [ 1, "Detect Scores",  self.scores_detect   ],
                                [ 1, "Reset Scores",   self.scores_reset    ]
                            ]
        
        self.cancel     =   False
        self.file       =   None
        self.files      =   0
        self.folder     =   None
        self.processed  =   0
        
        self.model      =   CNN( )
        
        _               =   self.title( self.base_title )
        
        self.panel      =   Panel( master = self, elements = self.elements )
        self.canvas     =   Canvas( master = self )
        
        _               =   self.panel.pack(  fill = tkinter.Y,    side = tkinter.LEFT,  expand = False )
        _               =   self.canvas.pack( fill = tkinter.BOTH, side = tkinter.RIGHT, expand = True  )
        
        screen_x        =   self.winfo_screenwidth( )
        screen_y        =   self.winfo_screenheight( )
        
        size_x          =   int( screen_x * 0.85 )
        size_y          =   int( screen_y * 0.80 )
        offset_x        =   int( screen_x * 0.07 )
        offset_y        =   int( screen_y * 0.07 )
        
        _               =   self.geometry( newGeometry = str( size_x ) + "x" + str( size_y ) + "+" + str( offset_x ) + "+" + str( offset_y ) )
        
        _               =   self.folder_close( )
        
        return
    
    def count_files( self ):
        
        return self.files
    
    def count_processed( self ):
        
        return self.processed
    
    def folder_cancel( self ):
        
        self.cancel     =   True
        
        return
    
    def file_cancel( self, event = None ):
        
        self.file.points    =   [ ]
        self.file.select    =   -1
        
        _               =   self.panel.enable_buttons( )
        
        _               =   self.canvas.change_mode( mode = 0, command = None )
        
        _               =   self.unbind_all( sequence = "<KeyPress>" )
        _               =   self.unbind_all( sequence = "<Escape>" )
        
        return
    
    def file_next( self ):
        
        _               =   self.file_save( )
        
        self.file       =   self.folder.next( )
        
        _               =   self.canvas.add_image( file = self.file )
        
        return
    
    def file_previous( self ):
        
        _               =   self.file_save( )
        
        self.file       =   self.folder.previous( )
        
        _               =   self.canvas.add_image ( file = self.file )
        
        return
    
    def file_save( self ):
        
        if ( self.file is not None ):
            
            _               =   self.file.save_data(  )
            _               =   self.file.save_image( preferred_width = self.out_img[ 0 ], preferred_height = self.out_img[ 1 ], filetype = self.out_img[ 2 ] )
        
        return
    
    def folder_close( self ):
        
        _               =   self.file_save( )
        
        self.cancel     =   False
        self.file       =   None
        self.files      =   0
        self.folder     =   None
        self.processed  =   0
        
        _               =   self.title( self.base_title )
        
        _               =   self.panel.disable_buttons( )
        _               =   self.panel.enable_button( text = "Open Folder" )
        _               =   self.panel.refresh_labels( )
        
        _               =   self.canvas.remove_image( )
        
        return
    
    def folder_export( self ):
        
        initialdir      =   "/".join( self.folder.path.split( "/" )[ 0 : -1 ] )
        initialfile     =   self.folder.path.split( "/" )[ -1 ]
        
        path            =   tkinter.filedialog.asksaveasfilename( initialdir = initialdir, initialfile = initialfile, defaultextension = self.ext_data, filetypes = [ ( "All files", "*.*") ] )
        
        if ( path is not None ):
            _               =   self.folder.export( path = path )
        
        return
    
    def folder_open( self ):
        
        path            =   tkinter.filedialog.askdirectory( )
        
        if ( path == "" ):
            return
        
        _               =   self.folder_close( )
        
        _               =   self.title( self.base_title + " - " + path )
        
        _               =   self.panel.enable_button( text = "Close Folder" )
        
        self.folder     =   Folder( path = path, image_extensions = self.ext_img, data_extension = self.ext_data, grid_size = self.grid_size )
        self.files      =   self.folder.length
        
        if ( self.files == 0 ):
            return
        
        self.file       =   self.folder.next( )
        
        _               =   self.panel.enable_buttons( )
        _               =   self.panel.refresh_labels( )
        
        _               =   self.canvas.add_image( file = self.file )
        
        return
    
    def folder_process( self ):
        
        self.cancel     =   not tkinter.messagebox.askokcancel( title = "Overwrite Confirmation", message = "Warning: Continuing will overwrite all existing data" )
        
        if ( self.cancel ):
            return
        
        self.processed  =   0
        
        _               =   self.panel.disable_buttons( )
        _               =   self.panel.change_button( text = "Process Folder", newText = "Cancel Process", newCommand = self.folder_cancel )
        _               =   self.panel.refresh_labels( )
        
        for i in range( self.files ):
            
            if ( self.grid_detect( ) ):
                
                _               =   self.update( )
                
                if ( self.cancel ):
                    break
                
                _               =   self.scores_detect( )
                _               =   self.update( )
                
                if ( self.cancel ):
                    break
            
            _               =   self.file_next( )
            _               =   self.update( )
            
            if ( self.cancel ):
                break
            
            self.processed  =   self.processed + 1
            _               =   self.panel.refresh_labels( )
        
        _               =   self.panel.enable_buttons( )
        
        return
    
    def grid_detect( self ):
        
        try:
            
            _               =   self.file.grid_detect( )
            
        except:
            
            _               =   print( "Grid detection failed on " + self.file.filename )
            
            return False
        
        _               =   self.canvas.refresh( )
        
        return True
    
    def grid_select( self ):
        
        self.file.points    =   [ ]
        
        _               =   self.panel.disable_buttons( )
        _               =   self.panel.change_button( text = "Select Grid", newText = "Cancel Selection", newCommand = self.file_cancel )
        
        _               =   self.canvas.change_mode( mode = 2, command = self.grid_select_click )
        
        _               =   self.bind_all( sequence = "<Escape>", func = self.file_cancel )
        
        return
    
    def grid_select_click( self, x, y ):
        
        _               =   self.file.points.append( [ x, y ] )
        
        _               =   self.canvas.refresh( )
        
        if ( len( self.file.points ) >= 4 ):
            
            _           =   self.file.grid_select( )
            _           =   self.file_cancel( )
        
        return
    
    def scores_detect( self ):
        
        try:
            
            _               =   self.file.scores_detect( self.model )
            
        except:
            
            _               =   print( "Score detection failed on " + self.file.filename )
            
            return False
        
        _               =   self.canvas.refresh( )
        
        return True
    
    def scores_select( self ):
        
        self.file.select    =   0
        
        _               =   self.panel.disable_buttons( )
        _               =   self.panel.change_button( text = "Select Scores", newText = "Cancel Selection", newCommand = self.file_cancel )
        
        _               =   self.canvas.change_mode( mode = 1, command = self.scores_select_click )
        
        _               =   self.bind_all( sequence = "<KeyPress>", func = self.scores_select_key )
        _               =   self.bind_all( sequence = "<Escape>", func = self.file_cancel )
        
        return
    
    def scores_select_click( self, x, y ):
        
        select          =   self.file.nearest_point( point = [ x, y ] )
        
        if ( select == -1 ):
            return
            
        self.file.select    =   select
        
        _               =   self.canvas.refresh( )
        
        return
    
    def scores_select_key( self, event ):
        
        if ( event.char in [ "0", "1", "2", "3", "4", "5" ] ):
            
            score           =   int( event.keysym )
            
            _               =   self.file.scores_select( index = self.file.select, score = score )
            _               =   self.file.scores_next( )
        
        elif ( event.char in [ "6", "7", "8", "9", "x", "X" ] ):
            
            score           =   -1
            
            _               =   self.file.scores_select( index = self.file.select, score = score )
            _               =   self.file.scores_next( )
        
        _               =   self.canvas.refresh( )
        
        return
    
    def scores_reset( self ):
        
        _               =   self.file.scores_reset( )
        
        _               =   self.canvas.refresh( )
        
        return