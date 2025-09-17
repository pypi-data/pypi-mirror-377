from typing import Dict, List, Tuple

from requests import Request

from ows_lib.client.mixins import OgcClient
from ows_lib.client.utils import update_queryparams
from ows_lib.models.ogc_request import OGCRequest


class WebMapServiceMixin(OgcClient):
    """Abstract WebMapService class which implements some basic functionality for all wms client applications
    """
    @property
    def crs_qp(self):
        raise NotImplementedError

    @property
    def get_map_operation_name(self):
        raise NotImplementedError

    @property
    def get_feature_info_operation_name(self):
        raise NotImplementedError

    def get_map_request(
            self,
            layers: List[str],
            styles: List[str],
            crs: str,
            bbox: Tuple[float, float, float, float],
            width: int,
            height: int,
            format: str,
            transparent: bool = None,
            bgcolor: int = 0xFFFFFF,
            exceptions: str = "xml",
            time: List[str] = None,
            elevation: float = None) -> OGCRequest:
        """Constructs a GetMap request to use for requesting

        :param layers: The name of layers which shall be requested
        :type layers: List[str]
        :param styles: The styles of the layers which shall be requested
        :type styles: List[str]
        :param crs: the reference system which shall be used
        :type crs: str
        :param bbox: the bounding box 
        :type bbox: Tuple[float, float, float, float]
        :param width: the pixel width 
        :type width: int
        :param height: the pixel height
        :type height: int
        :param format: the response format
        :type format: str
        :param transparent: shall the response be a transparent image?, defaults to None
        :type transparent: bool, optional
        :param bgcolor: the background color of the response, defaults to 0xFFFFFF
        :type bgcolor: int, optional
        :param exceptions: the exception format which shall be used by the server, defaults to "xml"
        :type exceptions: str, optional
        :param time: the time value or range for map data, defaults to None
        :type time: List[str], optional
        :param elevation: _description_, defaults to None
        :type elevation: float, optional
        :return: the constructed get map request object
        :rtype: Request
        """

        if isinstance(transparent, str):
            if transparent == "TRUE":
                transparent = True
            else:
                transparent = False

        params = {
            "VERSION": self.capabilities.service_type.version,
            "REQUEST": "GetMap",
            "SERVICE": self.capabilities.service_type.name,
            "LAYERS": ",".join(layers),
            "STYLES": ",".join(styles),
            self.crs_qp: crs,
            "BBOX": ",".join(bbox),
            "WIDTH": width,
            "HEIGHT": height,
            "FORMAT": format,
            "TRANSPARENT": transparent,
            "BGCOLOR": hex(bgcolor),
            "EXCEPTIONS": exceptions,
        }
        if time:
            params.update({"TIME": ",".join(time)})
        if elevation:
            params.update({"ELEVATION": elevation})

        url = update_queryparams(
            url=self.capabilities.get_operation_url_by_name_and_method(
                self.get_map_operation_name, "Get").url,
            params=params)

        return Request(method="GET", url=url)

    def get_feature_info_request(
            self,
            get_map_request: Request,
            query_layers: List[str],
            info_format: str,
            i: int,
            j: int,
            feature_count: int = 0,
            exceptions: str = "xml") -> OGCRequest:
        """Constructs a GetFeatureInfo request to use for requesting

        :param get_map_request: The GetMap request where this request shall based on
        :type get_map_request: requests.Request
        :param query_layers: The list of layers for that the feature info shall be requested
        :type query_layers: List[str]
        :param info_format: The concrete format of the response
        :type info_format: str
        :param i: the x value of the x/y point tuple
        :type i: int
        :param j: the y value of the x/y point tuple
        :type j: int
        :param feature_count: The number of features that shall be returned, defaults to 0
        :type feature_count: int, optional
        :param exceptions: the exception format of the server to response with, defaults to "xml"
        :type exceptions: str, optional
        :return: the constructed get feature info request object
        :rtype: requests.Request
        """

        params: Dict = get_map_request.params

        get_feature_info_params = {
            "VERSION": self.capabilities.service_type.version,
            "REQUEST": "GetFeatureInfo",
            "SERVICE": self.capabilities.service_type.name,
            "QUERY_LAYERS": ",".join(query_layers),
            "INFO_FORMAT": info_format,
            "FEATURE_COUNT": feature_count,
            "I": i,
            "J": j,
            "EXCEPTIONS": exceptions,
        }

        params.update(get_feature_info_params)

        url = update_queryparams(
            url=self.capabilities.get_operation_url_by_name_and_method(
                self.get_feature_info_operation_name, "Get").url,
            params=params)

        return OGCRequest(method="GET", url=url)
