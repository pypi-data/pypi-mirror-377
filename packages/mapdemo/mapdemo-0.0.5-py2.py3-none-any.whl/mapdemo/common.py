"""The common module contains common functions and classes used by the other modules.
"""

def hello_world():
    """Prints "Hello World!" to the console.
    """
    print("Hello World!")


def random_number():
    """Return a random number between 0 and 1.

    Returns:
        float: A random number between 0 and 1.
    """
    import random
    return random.random()    

import ipyleaflet
from ipyleaflet import LayersControl, FullScreenControl, DrawControl, ScaleControl, MeasureControl

class Map(ipyleaflet.Map):
    """Simple, ready-to-use Map with optional controls, avoids duplicates."""

    def __init__(self, center=[20,0], zoom=2, **kwargs):
        scroll_wheel_zoom = kwargs.pop("scroll_wheel_zoom", True)
        height = kwargs.pop("height", "600px")

        # Optional controls (default)
        layer_control = kwargs.pop("layer_control", True)
        fullscreen_control = kwargs.pop("fullscreen_control", True)
        draw_control = kwargs.pop("draw_control", False)
        scale_control = kwargs.pop("scale_control", False)
        measure_control = kwargs.pop("measure_control", False)

        # Initialize base ipyleaflet.Map
        super().__init__(center=center, zoom=zoom, scroll_wheel_zoom=scroll_wheel_zoom, **kwargs)
        self.layout.height = height

        # Add controls
        if layer_control: self.add_layer_control()
        if fullscreen_control: self.add_fullscreen_control()
        if draw_control: self.add_draw_control()
        if scale_control: self.add_scale_control()
        if measure_control: self.add_measure_control()

    # -------- Utility to replace existing control -------- #
    def _replace_control(self, control_type, new_control):
        for c in list(self.controls):
            if isinstance(c, control_type):
                self.remove_control(c)
        self.add_control(new_control)

    # -------- Control Methods -------- #
    def add_layer_control(self, position="topright"):
        self._replace_control(LayersControl, LayersControl(position=position))

    def add_fullscreen_control(self, position="topright"):
        self._replace_control(FullScreenControl, FullScreenControl(position=position))

    def add_draw_control(self, **kwargs):
        self._replace_control(DrawControl, DrawControl(**kwargs))

    def add_scale_control(self, position="bottomleft", metric=True, imperial=False):
        self._replace_control(ScaleControl, ScaleControl(position=position, metric=metric, imperial=imperial))

    def add_measure_control(self, position="topright", primary_length_unit="kilometers"):
        self._replace_control(
            MeasureControl,
            MeasureControl(position=position, primary_length_unit=primary_length_unit)
        )

     # ---------------- Layer Adding Methods ---------------- #
    def add_rast_layer(self, url, name, **kwargs):
        """Add a raster tile layer (TileLayer) with name for LayersControl."""
        layer = TileLayer(url=url, name=name, **kwargs)
        self.add_layer(layer)

    def add_vect_layer(self, data, name, **kwargs):
        """Add vector layer (GeoJSON) with name for LayersControl."""
        import ipyleaflet
        layer = ipyleaflet.GeoJSON(data=data, name=name, **kwargs)
        self.add_layer(layer)

    # Generic add_layer wrapper
    def add_layer(self, layer):
        """Add any ipyleaflet layer with a name."""
        if not hasattr(layer, "name"):
            layer.name = "Layer"
        super().add_layer(layer)

    def add_raster_layer(self, url, name):
        # Check if a layer with same name or URL already exists
        for layer in self.layers:
            if isinstance(layer, TileLayer) and getattr(layer, "url", None) == url:
                print(f"Layer '{name}' already added, skipping.")
                return
        tile = TileLayer(url=url, name=name)
        self.add_layer(tile)
    
    def add_vector_layer(self, data, name):
        # Check if a vector layer with the same name exists
        for layer in self.layers:
            if hasattr(layer, "name") and layer.name == name:
                print(f"Vector layer '{name}' already added. Skipping.")
                return
        # Add layer if not duplicate
        self.add_layer(ipyleaflet.GeoJSON(data=data, name=name))
