
def test_custom_grid_class():
    try:
        from pygridsio.IO.AscZmapIO import Grid
        from pygridsio.IO.voxet import Voxet
    except:
        raise ModuleNotFoundError("PyGridsio should always keep a copy of the Grid "
                                  "and Voxet classes, see docstring of each class "
                                  "for explaination.")
