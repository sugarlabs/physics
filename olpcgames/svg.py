"""Image-load from svg files to Pygame images

Dependent on RSVG and Cairo libraries
"""
from olpcgames import _cairoimage

def load( file, (width, height)=(None,None) ):
    """pygame.load like interface for loading SVG graphics
    
    file -- object with read() method (file-like object) or a string
        filename for a file to be read off the local system
    
        See render function for details of width and height 
        arguments 
    
    returns Pygame image instance
    """
    try:
        data = file.read()
    except AttributeError, err:
        data = open( file, 'r').read()
    return render( data, (width,height) )

def render( data, (width, height)=(None,None) ):
    """Render SVG graphic/data to a Pygame image object
    
    data -- SVG file for loading into the image, must be properly formed
        and valid SVG to allow the rendering to complete
    
    (width,height) -- size of the resulting image in pixels,  the graphic will 
        be scaled to fit into the image.
        
        If one dimension is left as None, then the graphic will be scaled to 
        fit the given dimension, with the other dimension provided by the 
        proportions of the graphic.
        
        If both dimensions are left as None, then they will both be provided 
        by the "natural" dimensions of the SVG at the natural (GTK-defined)
        resolution of the screen.
    
    returns Pygame image instance
    """
    import rsvg
    handle = rsvg.Handle( data = data )
    originalSize = (width,height)
    scale = 1.0
    hw,hh = handle.get_dimension_data()[:2]
    if hw and hh:
        if not width:
            if not height:
                width,height = hw,hh 
            else:
                scale = float(height)/hh
                width = hh/float(hw) * height
        elif not height:
            scale = float(width)/hw
            height = hw/float(hh) * width
        else:
            # scale only, only rendering as large as it is...
            if width/height > hw/hh:
                # want it taller than it is...
                width = hh/float(hw) * height
            else:
                height = hw/float(hh) * width
            scale = float(height)/hh
        
        csrf, ctx = _cairoimage.newContext( int(width), int(height) )
        ctx.scale( scale, scale )
        handle.render_cairo( ctx )
        return _cairoimage.asImage( csrf )
    return None
