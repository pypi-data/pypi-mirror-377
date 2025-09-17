from insitupy import WITH_NAPARI

if WITH_NAPARI:
    from numbers import Number
    from typing import List, Literal, Optional, Tuple
    from warnings import warn

    import matplotlib
    import napari
    import numpy as np
    import pandas as pd
    from matplotlib.colors import rgb2hex
    from napari.types import LayerDataTuple
    from napari.utils.notifications import show_info, show_warning
    from pandas.api.types import is_numeric_dtype
    from shapely import (LinearRing, LineString, MultiPoint, MultiPolygon,
                         Point, Polygon)

    from insitupy._constants import (ANNOTATIONS_SYMBOL,
                                     DEFAULT_CATEGORICAL_CMAP,
                                     DEFAULT_CONTINUOUS_CMAP, POINTS_SYMBOL,
                                     REGIONS_SYMBOL)
    from insitupy.interactive._configs import _get_viewer_uid, config_manager
    from insitupy.utils._checks import check_rgb_column
    from insitupy.utils._colors import _data_to_rgba, _determine_climits

    def _add_geometries_as_layer(
        dataframe: pd.DataFrame,
        viewer: napari.Viewer,
        layer_name: str,
        #scale_factor: Union[Tuple, List, np.ndarray],
        edge_width: Number = 10, # µm
        opacity: float = 1,
        rgb_color: Optional[Tuple] = None,
        show_names: bool = False,
        allow_duplicate_layers: bool = False,
        mode: Literal["Annotations", "Regions"] = "Annotations",
        tolerance: Number = 5
        ):

        # list to store information on shapes
        shape_list = []
        shape_type_list = []

        # lists to store the point x and y coordinates
        point_x_list = []
        point_y_list = []

        # iterate through annotations of this class and collect them as list
        color_list = {"Points": [], "Shapes": []}
        uid_list = {"Points": [], "Shapes": []}
        type_list = {"Points": [], "Shapes": []} # list to store whether the polygon is exterior or interior
        names_list = {"Points": [], "Shapes": []}

        # get the config
        viewer_config = config_manager[_get_viewer_uid(viewer)]

        # prepare layer names
        if mode == "Regions":
            shapes_layer_name_with_symbol = REGIONS_SYMBOL + " " + layer_name
        elif mode == "Annotations":
            shapes_layer_name_with_symbol = ANNOTATIONS_SYMBOL + " " + layer_name
        else:
            raise ValueError(f"Unknown value for `mode`: {mode}")

        points_layer_name_with_symbol = POINTS_SYMBOL + " " + layer_name

        if shapes_layer_name_with_symbol in viewer.layers:
            shapes_layer_exists = True
        else:
            shapes_layer_exists = False

        if points_layer_name_with_symbol in viewer.layers:
            points_layer_exists = True
        else:
            points_layer_exists = False

        # check if colors are given
        if "color" in dataframe.columns:
            # make sure the RGB column consists only of valid RGB tuples or lists
            rgbs_valid = check_rgb_column(dataframe, "color")
            if not rgbs_valid:
                warn('Not all RGB values given in column "color" are valid. Used blue for all geometries.')
                dataframe["color"] = [(0,0,255)] * len(dataframe)
        else:
            if rgb_color is not None:
                dataframe["color"] = [rgb_color] * len(dataframe)
            else:
                dataframe["color"] = [(0,0,255)] * len(dataframe)

        for uid, row in dataframe.iterrows():
            # get coordinates
            geometry = row["geometry"]
            #uid = row["id"]
            hexcolor = rgb2hex([elem / 255 for elem in row["color"]])
            rgbacolor = [elem / 255 for elem in row["color"]] + [1] # scale to range 0-1 and add opacity value

            # check if polygon is a MultiPolygon or just a simple Polygon object
            if isinstance(geometry, MultiPolygon):
                data = list(geometry.geoms)
                annotation_type = "polygon_like"
            elif isinstance(geometry, Polygon):
                data = [geometry]
                annotation_type = "polygon_like"
            elif isinstance(geometry, LineString):
                data = geometry
                annotation_type = "line_like"
            elif isinstance(geometry, Point) or isinstance(geometry, MultiPoint):
                data = geometry
                annotation_type = "point_like"
            else:
                raise ValueError(f"Received unknown geometry type: {type(geometry)}")

            # check if this uid is already in the current layer. If so, skip it
            if annotation_type in ["polygon_like", "line_like"]:
                if shapes_layer_exists:
                    layer = viewer.layers[shapes_layer_name_with_symbol]
                    if uid in layer.properties["uid"]:
                        print(f"Already in layer: {uid}") if viewer_config.verbose else None
                        continue

            if annotation_type == "point_like":
                if points_layer_exists:
                    layer = viewer.layers[points_layer_name_with_symbol]
                    if uid in layer.properties["uid"]:
                        print(f"Already in layer: {uid}") if viewer_config.verbose else None
                        continue

            if annotation_type == "polygon_like":
                for p in data:
                    # simplify polygon for visualization
                    p = p.simplify(tolerance)
                    # extract exterior coordinates from shapely object
                    # Note: the last coordinate is removed since it is identical with the first
                    # in shapely objects, leading sometimes to visualization bugs in napari
                    exterior_array = np.array([p.exterior.coords.xy[1].tolist()[:-1],
                                            p.exterior.coords.xy[0].tolist()[:-1]]).T
                    shape_list.append(exterior_array)  # collect shape
                    color_list["Shapes"].append(hexcolor)  # collect corresponding color
                    uid_list["Shapes"].append(uid)  # collect corresponding unique id
                    type_list["Shapes"].append("polygon_exterior")
                    names_list["Shapes"].append(row["name"])
                    shape_type_list.append("polygon")

                    # if polygon has interiors, plot them as well
                    # for information on donut-shaped polygons in napari see: https://forum.image.sc/t/is-it-possible-to-generate-doughnut-shapes-in-napari-shapes-layer/88834
                    if len(p.interiors) > 0:
                        for linear_ring in p.interiors:
                            if isinstance(linear_ring, LinearRing):
                                interior_array = np.array([linear_ring.coords.xy[1].tolist()[:-1],
                                                        linear_ring.coords.xy[0].tolist()[:-1]]).T
                                shape_list.append(interior_array)  # collect shape
                                color_list["Shapes"].append(hexcolor)  # collect corresponding color
                                uid_list["Shapes"].append(uid)  # collect corresponding unique id
                                type_list["Shapes"].append("polygon_interior")
                                names_list["Shapes"].append(row["name"])
                                shape_type_list.append("polygon")
                            else:
                                ValueError(f"Input must be a LinearRing object. Received: {type(linear_ring)}")

            elif annotation_type == "line_like":
                line_array = np.array([data.coords.xy[1].tolist(), data.coords.xy[0].tolist()]).T

                # collect data
                shape_list.append(line_array)
                color_list["Shapes"].append(hexcolor)  # collect corresponding color
                uid_list["Shapes"].append(uid)  # collect corresponding unique id
                type_list["Shapes"].append("line") # information on type of coordinates - important for interior/exterior of polygons
                names_list["Shapes"].append(row["name"])
                shape_type_list.append("path")

            elif annotation_type == "point_like":
                try:
                    # in case of MultiPoints we first have to extract the individual geometries
                    point_coords = [elem.coords.xy for elem in geometry.geoms]
                except AttributeError:
                    # a normal Point object does not have multiple geometries and coordinates can be accessed directly
                    point_coords = [geometry.coords.xy]

                # collect coordinates and other data on the points
                for coord in point_coords:
                    point_x_list.append(coord[1].tolist()[0])
                    point_y_list.append(coord[0].tolist()[0])
                    color_list["Points"].append(rgbacolor)  # collect corresponding color
                    uid_list["Points"].append(uid)  # collect corresponding unique id
                    type_list["Points"].append("point") # information on type of coordinates - important for interior/exterior of polygons
                    names_list["Points"].append(row["name"])

        if len(shape_list) > 0:
            properties_dict = {
                    'uid': uid_list["Shapes"], # list with uids
                    'type': type_list["Shapes"] # list giving information on whether the polygon is interior or exterior
                }
            if show_names:
                properties_dict['name'] = names_list["Shapes"]

                text_dict = {
                    'string': '{name}',
                    'anchor': 'upper_left',
                    #'translation': [-5, 0],
                    'size': 8,
                    'color': color_list["Shapes"]
                    }
            else:
                text_dict = None

            # add shapes to viewer
            if shapes_layer_name_with_symbol in viewer.layers:
                show_warning(f"A layer with the name '{shapes_layer_name_with_symbol}' already exists. Shapes added to this layer.")
                layer = viewer.layers[shapes_layer_name_with_symbol]

                viewer_config._auto_set_uid = False
                layer.add(
                    data=shape_list,
                    shape_type=shape_type_list,
                    edge_width=edge_width, # µm
                    edge_color=color_list["Shapes"],
                    face_color='transparent',
                )

                # add properties
                layer.properties["uid"][-len(shape_list):] = properties_dict["uid"]
                layer.properties["type"][-len(shape_list):] = properties_dict["type"]

                if show_names:
                    layer.properties["name"][-len(shape_list):] = properties_dict["name"]
                    # layer.properties["name"] = np.append(layer.properties["name"], properties_dict["name"])

                viewer_config._auto_set_uid = True

            else:
                viewer.add_shapes(
                    data=shape_list,
                    name=shapes_layer_name_with_symbol,
                    properties=properties_dict,
                    shape_type=shape_type_list,
                    edge_width=edge_width, # µm
                    edge_color=color_list["Shapes"],
                    face_color='transparent',
                    opacity=opacity,
                    #scale=scale_factor,
                    text=text_dict
                    )
                show_info(f"New layer '{shapes_layer_name_with_symbol}' created.")

        point_data = np.stack([point_x_list, point_y_list]).T
        if len(point_data) > 0:
            # add points to viewer
            # if not points_layer_name_with_symbol in viewer.layers:
            #     add = True
            # elif allow_duplicate_layers:
            #     add = True
            # else:
            #     add = False

            # if add:

            properties_dict = {
                        'uid': uid_list["Points"], # list with uids
                        'type': type_list["Points"] # list giving information on whether the polygon is interior or exterior
                    }

            if points_layer_name_with_symbol in viewer.layers:
                show_warning(f"A layer with the name '{points_layer_name_with_symbol}' already exists. Points added to this layer.")
                layer = viewer.layers[points_layer_name_with_symbol]

                layer.add(
                    coords=point_data,
                    # face_color=color_list["Points"]
                )

                # change colors of the newly added data
                layer.face_color[-len(point_data):] = color_list["Points"]
                layer.refresh() # refresh layer to show new colors
            else:
                viewer.add_points(
                    data=point_data,
                    name=points_layer_name_with_symbol,
                    properties=properties_dict,
                    size=10,
                    border_color="black",
                    face_color=color_list["Points"],
                    #scale=scale_factor
                )


    def _create_points_layer(points,
                            color_values: List[Number],
                            name: str,
                            point_names: List[str],
                            point_size: int = 6, # is in scale unit (so mostly µm)
                            opacity: float = 1,
                            visible: bool = True,
                            border_width: float = 0,
                            border_color: str = 'red',
                            upper_climit_pct: int = 99,
                            categorical_cmap: matplotlib.colors.ListedColormap = DEFAULT_CATEGORICAL_CMAP,
                            continuous_cmap = DEFAULT_CONTINUOUS_CMAP,
                            ) -> LayerDataTuple:
        if categorical_cmap is None:
            categorical_cmap = DEFAULT_CATEGORICAL_CMAP
        # get colors
        colors, mapping, cmap = _data_to_rgba(data=color_values,
                               continuous_cmap=continuous_cmap,
                               categorical_cmap=categorical_cmap,
                               upper_climit_pct=upper_climit_pct)

        # generate point layer
        layer = (
            points,
            {
                'name': name,
                'properties': {
                    "value": color_values,
                    "cell_name": point_names
                    },
                'symbol': 'o',
                'size': point_size,
                'face_color': colors,
                'opacity': opacity,
                'visible': visible,
                'border_width': border_width,
                'border_color': border_color,
                'metadata': {"upper_climit_pct": upper_climit_pct}
                },
            'points'
            )
        return layer

    def _update_points_layer(
        layer: napari.layers.Layer,
        new_color_values: List[Number],
        new_name: Optional[str] = None,
        upper_climit_pct: int = 99,
        categorical_cmap: matplotlib.colors.ListedColormap = DEFAULT_CATEGORICAL_CMAP,
        continuous_cmap = DEFAULT_CONTINUOUS_CMAP,
        # cmap: str = "viridis"
        ) -> None:
        # get the RGBA colors for the new values
        if categorical_cmap is None:
            categorical_cmap = DEFAULT_CATEGORICAL_CMAP
        new_colors, mapping, cmap = _data_to_rgba(data=new_color_values,
                                                continuous_cmap=continuous_cmap,
                                                categorical_cmap=categorical_cmap,
                                                upper_climit_pct=upper_climit_pct)

        # change the colors of the layer
        layer.face_color = new_colors

        # change properties of layer
        new_props = layer.properties.copy()
        new_props['value'] = new_color_values
        layer.properties = new_props

        if new_name is not None:
            layer.name = new_name

#TODO: Why is this function not used anywhere?
# def _determine_color_settings(
#     color_values,
#     cmap,
#     upper_climit_pct
#     ):
#     # check if the data should be plotted categorical or continous
#     if is_numeric_dtype(color_values):
#         is_categorical = False # if the data is numeric it should be plotted continous
#     else:
#         is_categorical = True # if the data is not numeric it should be plotted categorically

#     if is_categorical:
#         # get color cycle for categorical data
#         color_mode = "cycle"
#         # palettes = CustomPalettes()
#         # color_cycle = getattr(palettes, "tab20_mod").colors
#         color_cycle = DEFAULT_CATEGORICAL_CMAP.colors
#         color_map = None
#         climits = None
#     else:
#         color_mode = "colormap"
#         color_map = cmap
#         color_cycle = None

#         climits = _determine_climits(
#             color_values=color_values,
#             upper_climit_pct=upper_climit_pct
#         )

#     return color_mode, color_cycle, color_map, climits