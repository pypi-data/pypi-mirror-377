import urllib.parse
from typing import Dict, List
from urllib.parse import parse_qs, urlparse

from django.contrib.gis.gdal import SpatialReference
from django.contrib.gis.geos import GEOSGeometry, Polygon
from epsg_cache.registry import Registry
from epsg_cache.utils import get_epsg_srid
from requests import Session

from ows_lib.client.enums import OGCServiceEnum
from ows_lib.client.exceptions import (MissingBboxParam, MissingCrsParam,
                                       MissingServiceParam)
from ows_lib.xml_mapper.capabilities.mixins import OGCServiceMixin


def update_queryparams(url: str, params: Dict):
    """Helper function to update query paramase inside an existing url with trailing query params"""
    url_parts = urllib.parse.urlparse(url)
    query = dict(urllib.parse.parse_qsl(url_parts.query))
    query.update(params)
    return url_parts._replace(query=urllib.parse.urlencode(query=query)).geturl()


def _construct_polygon_from_bbox_query_param_for_wfs(get_dict):
    """Construct a polygon from the parsed bbox query parameter, based on the given service type and version.

    **WFS 1.0.0 (see wfs specs - 6.2.8.2.3 BBOX)**:
    * Provides geographic coordinates in longitude/latitude | east/north and may not be trusted to
        respect the EPSG definition axis order. ==> mathematical x,y order is used.
    * The coordinate reference system of the bbox always matches the crs of the SRS query param.


    **WFS >1.0.0 (see wfs specs - 14.3.3 Bounding box)**:
    * Respects the axis order defined by the EPSG definition. ==> dynamic x,y order based on the result
        of the epsg registry is used.
    * The bbox values support n axis crs systems ==> BBOX=lcc1,lcc2,...,lccN,ucc1,ucc2,...uccN[,crsuri]
    * The coordinate reference system of the bbox by default is WGS84 (EPSG:4326). IF the bbox param provides a
    crsuri value this coordinate reference system shall be used instead.

    :return: the bbox parsed from the get_dict or an empty polygon if something went wrong.
    :rtype: :class:`django.contrib.gis.geos.polygon.Polygon`
    """
    try:
        major_version, minor_version, _ = get_dict["version"].split(
            ".")
        major_version = int(major_version)
        minor_version = int(minor_version)
        bbox = get_dict["bbox"]
        srid = get_dict.get("srs", None)
        if not srid:
            srid = get_dict.get("srsname", None)
            if not srid:
                raise MissingCrsParam

        xy_order = True

        if major_version == 1 and minor_version < 1:
            min_x, min_y, max_x, max_y = bbox.split(",")
            min_x = float(min_x)
            min_y = float(min_y)
            max_x = float(max_x)
            max_y = float(max_y)
        else:
            bbox_values = bbox.split(",")
            registry = Registry()
            if len(bbox_values) == 4:
                epsg_sr = registry.get(srid=4326)
            elif len(bbox_values) == 5:
                _, srid = get_epsg_srid(bbox_values[4])
                epsg_sr = registry.get(srid=srid)
            else:
                raise NotImplementedError(
                    "multiple dimension crs is not implemented.")
            min_x = float(bbox_values[0])
            min_y = float(bbox_values[1])
            max_x = float(bbox_values[2])
            max_y = float(bbox_values[3])
            xy_order = epsg_sr.is_xy_order

        if xy_order:
            return Polygon(((min_x, min_y), (min_x, max_y), (max_x, max_y), (max_x, min_y), (min_x, min_y)),
                           srid=srid)
        else:
            return Polygon(((min_y, min_x), (max_y, min_x), (max_y, max_x), (min_y, max_x), (min_y, min_x)),
                           srid=srid)
    except Exception:
        pass
    return GEOSGeometry('POLYGON EMPTY')


def _construct_polygon_from_bbox_query_param_for_wms(get_dict):
    """Construct a polygon from the parsed bbox query parameter, based on the given service type and version.

    * In WMS version < 1.3.0 requests with a Geographic Coordinate Reference System, the bbox is interpreted with
        X-axis ≙ Longitude and Y-axis ≙ Latitude value.
    * In WMS version >= 1.3.0 requests the bbox axis order is interpreted like the axis order of the requested
        reference system.

    .. note:: excerpt from ogc specs

        * **OGC WMS 1.1.0**: When the SRS parameter specifies a Geographic Coordinate Reference System, e.g.,
            "EPSG:4326", the returned image is implicitly projected using a pseudo-Plate Carrée projection that plots
            Longitude along the X-axis and Latitude along the Y-axis. The BBOX request parameter (Section 7.2.3.6)
            values for such a coordinate reference system shall be specified in the order minimum longitude, minimum
            latitude, maximum longitude, maximum latitude. The BBOX parameter values shall use the coordinate
            reference system units.
            Some Projected Coordinate Reference Systems, e.g., "EPSG:30800" ("RT38 2.5 gon W", used in Sweden), have
            axes order other than X=East, Y=North. The BBOX request parameter values for such a coordinate system
            shall be specified in the order minimum Easting, minimum Northing, maximum Easting, maximum Northing.
            The BBOX parameters shall use the coordinate reference system units. (see 6.5.5.1)
        * **OGC WMS 1.3.0**: EXAMPLE EPSG:4326 refers to WGS 84 geographic latitude, then longitude. That is, in
            this CRS the x axis corresponds to latitude, and the y axis to longitude. (see 6.7.3.3)

    :return: the bbox parsed from the get_dict or an empty polygon if something went wrong.
    :rtype: :class:`django.contrib.gis.geos.polygon.Polygon`
    """
    try:
        _, minor_version, _ = get_dict["version"].split(
            ".")
        minor_version = int(minor_version)
        srid = get_dict.get("srs", None)
        if not srid:
            srid = get_dict.get("crs", None)
            if not srid:
                raise MissingCrsParam

        bbox = get_dict["bbox"]
        min_x, min_y, max_x, max_y = bbox.split(",")
        min_x = float(min_x)
        min_y = float(min_y)
        max_x = float(max_x)
        max_y = float(max_y)

        xy_order = True
        if minor_version >= 3:
            sr = SpatialReference(srs_input=srid)
            registry = Registry()
            epsg_sr = registry.get(srid=sr.srid)
            srid = epsg_sr.srid
            xy_order = epsg_sr.is_xy_order
        else:
            if ":" in srid:
                srid = srid.split(":")[-1]
            srid = int(srid)

        if xy_order:
            return Polygon(((min_x, min_y), (min_x, max_y), (max_x, max_y), (max_x, min_y), (min_x, min_y)),
                           srid=srid)
        else:
            return Polygon(((min_y, min_x), (max_y, min_x), (max_y, max_x), (min_y, max_x), (min_y, min_x)),
                           srid=srid)
    except Exception:
        pass
    return GEOSGeometry('POLYGON EMPTY')


def construct_polygon_from_bbox_query_param(get_dict) -> GEOSGeometry:
    """Construct a polygon from the parsed bbox query parameter, based on the given service type and version.

    :return: the bbox parsed from the get_dict or an empty polygon if something went wrong.
    :rtype: :class:`django.contrib.gis.geos.geometry.GEOSGeometry`
    """
    service_type = get_dict.get("SERVICE", get_dict.get("service", None))
    if not service_type:
        raise MissingServiceParam
    if not get_dict.get("BBOX", get_dict.get("bbox", None)):
        raise MissingBboxParam
    if service_type.lower() == "wms":
        return _construct_polygon_from_bbox_query_param_for_wms(get_dict=get_dict)
    elif service_type.lower() == "wfs":
        return _construct_polygon_from_bbox_query_param_for_wfs(get_dict=get_dict)


def get_requested_layers(params: Dict) -> List[str]:
    """Filters the given params by requested layers

    :param params: all query parameters
    :type params: Dict
    :return: the requested layers from the query params
    :rtype: List[str]
    """
    return list(filter(None, params.get("LAYERS", params.get("layers", "")).split(",")))


def get_requested_feature_types(params: Dict) -> List[str]:
    """Filters the given params by requested featuretypes

    :param params: all query parameters
    :type params: Dict
    :return: the requested featuretypes from the query params
    :rtype: List[str]
    """
    return list(filter(None, params.get("TYPENAMES", params.get("typenames", "")).split(",")))


def get_requested_records(params: Dict) -> List[str]:
    """Filters the given params by requested featuretypes

    :param params: all query parameters
    :type params: Dict
    :return: the requested featuretypes from the query params
    :rtype: List[str]
    """
    return list(filter(None, params.get("Id", "").split(",")))


def _extract_service_and_version(
    capabilities: OGCServiceMixin | str
) -> tuple[OGCServiceEnum, str]:
    """Hilfsfunktion: ermittelt SERVICE und VERSION"""
    if isinstance(capabilities, OGCServiceMixin):
        service = OGCServiceEnum(capabilities.service_type.name.lower())
        version = capabilities.service_type.version
        return service, version

    if isinstance(capabilities, str):
        parsed = urlparse(capabilities)
        query = parse_qs(parsed.query)
        service = query.get("SERVICE", [None])[0]
        version = query.get("VERSION", [None])[0]
        if not service or not version:
            raise ValueError(
                "URL must contain SERVICE and VERSION parameters")
        try:
            return OGCServiceEnum(service.lower()), version
        except ValueError:
            raise ValueError(f"Unknown SERVICE type: {service}")

    raise TypeError("capabilities must be of type OGCServiceMixin or str")


def get_client(capabilities: OGCServiceMixin | str,
               session: Session = Session(),
               ):
    """Helper function to construct the correct client version for given capabilities document

    :param capabilities: The parsed capabilities document
    :type capabilities: OGCServiceMixin
    :return: the concrete service client
    :rtype: WebMapService | WebFeatureService | CatalogueService
    """
    from ows_lib.client.maps import CLIENT_MAP

    service, version = _extract_service_and_version(capabilities)

    ClientClass = CLIENT_MAP.get((service, version))
    if not ClientClass:
        raise ValueError(
            f"No client class registered for SERVICE={service.value} and VERSION={version}")

    return ClientClass(capabilities=capabilities, session=session)
