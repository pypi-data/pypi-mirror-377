from django.contrib.gis.geos import GEOSGeometry
from epsg_cache.utils import get_epsg_srid
from eulxml import xmlmap


class Gml(xmlmap.XmlObject):
    srs_name = xmlmap.StringField(xpath="./@srsName")

    @property
    def to_geometry(self) -> GEOSGeometry:
        geometry = GEOSGeometry.from_gml(self.serialize())
        if self.srs_name:
            _, srid = get_epsg_srid(self.srs_name)
        else:
            srid = 4326  # default srs
        return GEOSGeometry(geo_input=geometry.wkt, srid=srid)
