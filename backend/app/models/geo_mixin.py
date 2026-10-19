from geoalchemy2.shape import to_shape
from sqlalchemy import func

class GeoMixin:
    @property
    def latitude(self):
        if self.geom is None:
            return getattr(self, '_lat', None)
        if hasattr(self.geom, 'data'):
            try:
                shape = to_shape(self.geom)
                return float(shape.y)
            except Exception:
                pass
        return getattr(self, '_lat', None)

    @latitude.setter
    def latitude(self, val):
        self._lat = val
        self._sync_geom()

    @property
    def longitude(self):
        if self.geom is None:
            return getattr(self, '_lon', None)
        if hasattr(self.geom, 'data'):
            try:
                shape = to_shape(self.geom)
                return float(shape.x)
            except Exception:
                pass
        return getattr(self, '_lon', None)

    @longitude.setter
    def longitude(self, val):
        self._lon = val
        self._sync_geom()

    def _sync_geom(self):
        lat = getattr(self, '_lat', None)
        lon = getattr(self, '_lon', None)
        if lat is not None and lon is not None:
            # Garante que o PostGIS crie o ponto
            self.geom = func.ST_SetSRID(func.ST_MakePoint(float(lon), float(lat)), 4326)
        else:
            self.geom = None
