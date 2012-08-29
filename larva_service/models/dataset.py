import json
import os
from flask.ext.mongokit import Document
from larva_service import db, app
from datetime import datetime
from shapely.geometry import Point
from shapely.wkt import loads
from paegan.cdm.dataset import CommonDataset
from shapely.geometry import box

class Dataset(Document):
    __collection__ = 'datasets'
    use_dot_notation = True
    structure = {
        'name'              : unicode,  # Name of the dataset
        'starting'          : datetime, # URL to Behavior JSON
        'ending'            : datetime, # Save the contents of behavior URL
        'timestep'          : int,      # Model timestep, in seconds
        'location'          : unicode,  # Number of particles to force
        'bbox'              : unicode,  # WKT of the bounding box
        'geometry'          : unicode,  # WKT of the bounding polygon
        'variables'         : dict,     # dict of variables, including attributes
        'keywords'          : list,     # keywords pulled from global attributes of dataset
        'messages'          : list,     # Error messages
        'created'           : datetime,
        'updated'           : datetime
    }
    default_values = {
                      'created': datetime.utcnow
                      }

    def calc(self):
        """
        Compute bounds for this dataset
        """
        try:
            nc = CommonDataset(self.location)

            query_var = nc.get_varname_from_stdname("eastward_sea_water_velocity")[0]

            # Set BBOX
            minx, miny, maxx, maxy = nc.getbbox(var=query_var)
            self.bbox = unicode(box(minx, miny, maxx, maxy).wkt)

            # Set Bounding Polygon
            # Bounding polygon is not implemented in Paegan yet
            #poly = nc.getboundingpolygon(var=query_var)
            #self.geometry = poly
            
            # Set Time bounds
            mintime, maxtime = nc.gettimebounds(var='u')
            self.starting = mintime
            self.ending = maxtime

            self.variables = nc.getvariableinfo()
        except:
            app.logger.warning("Could not calculate bounds for this dataset")
            raise

    def google_maps_coordinates(self):
        marker_positions = []
        if self.geometry:
            geo = loads(self.geometry)
        elif self.bbox:
            geo = loads(self.bbox)
        else:
            return marker_positions

        if isinstance(geo, Point):
            marker_positions.append((geo.coords[0][1], geo.coords[0][0]))
        else:
            for pt in geo.exterior.coords:
                # Google maps is y,x not x,y
                marker_positions.append((pt[1], pt[0]))

        return marker_positions

db.register([Dataset])