import tkinter
import tkinter.ttk

class Panel( tkinter.Frame ):
    
    def __init__( self, master, elements ):
        
        _               =   super( ).__init__( master = master )
        
        self.buttons    =   { }
        self.labels     =   { }
        
        _               =   self.add( elements = elements )
        
        return
    
    def add( self, elements ):
        
        for i, [ type, text, command ] in enumerate( elements ):
            
            if ( type == 0 ):
                _                       =   self.add_separator( row = i )
            
            elif ( type == 1 ):
                self.buttons[ text ]    =   self.add_button( row = i, text = text, command = command )
                
            elif ( type == 2 ):
                self.labels[ text ]     =   self.add_label( row = i, text = text, command = command )
        
        return
    
    def add_button( self, row, text, command ):
        
        button          =   tkinter.ttk.Button( master = self, text = text, command = command, takefocus = False )
        _               =   button.grid( row = row, column = 0, columnspan = 2, padx = 10, pady = 5, ipadx = 8, ipady = 2, sticky = "news" )
        
        return [ button, command ]
    
    def add_label( self, row, text, command ):
        
        label           =   tkinter.ttk.Label( master = self, text = text      , anchor = "w" )
        count           =   tkinter.ttk.Label( master = self, text = command( ), anchor = "e", width = 6 )
        
        _               =   label.grid( row = row, column = 0, columnspan = 1, padx = ( 17,  0 ), pady = 2, sticky = "news" )
        _               =   count.grid( row = row, column = 1, columnspan = 1, padx = (  0, 17 ), pady = 2, sticky = "news" )
        
        return [ count, command ]
    
    def add_separator( self, row ):
        
        separator       =   tkinter.ttk.Separator( master = self, orient = tkinter.HORIZONTAL )
        
        _               =   separator.grid( row = row, columnspan = 2, padx = 10, pady = 2, sticky = "news" )
        
        return
    
    def change_button( self, text, newText, newCommand ):
        
        button, command =   self.buttons[ text ]
        _               =   button.config( state = tkinter.NORMAL, text = newText, command = newCommand )
        
        return
    
    def disable_button( self, text ):
        
        button, command =   self.buttons[ text ]
        _               =   button.config( state = tkinter.DISABLED, text = text, command = command )
        
        return
    
    def disable_buttons( self ):
        
        for text in self.buttons:
            
            _               =   self.disable_button( text = text )
        
        return
    
    def enable_button( self, text ):
        
        button, command =   self.buttons[ text ]
        _               =   button.config( state = tkinter.NORMAL, text = text, command = command )
        
        return
    
    def enable_buttons( self ):
        
        for text in self.buttons:
            
            _               =   self.enable_button( text = text )
        
        return
    
    def refresh_label( self, text ):
        
        count, command  =   self.labels[ text ]
        _               =   count.config( text = command( ) )
        
        return
    
    def refresh_labels( self ):
        
        for text in self.labels:
            
            _               =   self.refresh_label( text = text )
        
        _               =   self.update_idletasks( )
        
        return