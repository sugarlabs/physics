"""RSVG/Cairo-based rendering of SVG into Pygame Images"""
from pygame import sprite, Rect
from olpcgames import svg

class SVGSprite( sprite.Sprite ):
    """Sprite class which renders SVG source-code as a Pygame image
    
    Note:
    
        Currently this sprite class is a bit over-engineered, it gets in the way 
        if you want to, e.g. animate among a number of SVG drawings, as it 
        assumes that setSVG will always set a single SVG file for rendering.
    """
    rect = image = None
    resolution = None
    def __init__( 
        self, svg=None, size=None, *args
    ):
        """Initialise the svg sprite
        
        svg -- svg source text (i.e. content of an svg file)
        size -- optional, to constrain size, (width,height), leaving one 
            as None or 0 causes proportional scaling, leaving both 
            as None or 0 causes natural scaling (screen resolution)
        args -- if present, groups to which to automatically add
        """
        self.size = size
        super( SVGSprite, self ).__init__( *args )
        if svg:
            self.setSVG( svg )
    def setSVG( self, svg ):
        """Set our SVG source"""
        self.svg = svg
        # XXX could delay this until actually asked to display...
        if self.size:
            width,height = self.size
        else:
            width,height = None,None
        self.image = svg.render( self.svg, (width,height) ).convert_alpha()
        rect = self.image.get_rect()
        if self.rect:
            rect.move( self.rect ) # should let something higher-level do that...
        self.rect = rect 
    def copy( self ):
        """Create a copy of this sprite without reloading the svg image"""
        result = self.__class__(
            size = self.size
        )
        result.image = self.image 
        result.rect = Rect(self.rect)
        result.resolution = self.resolution
        return result
