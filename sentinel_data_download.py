from platform import platform
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date

# Write your usrname and password
api = SentinelAPI('usrname', 'password', 'https://apihub.copernicus.eu/apihub')

# search by polygon, time, and SciHub query keywords
footpoint = geojson_to_wkt(read_geojson('./utils/map.geojson'))
products = api.query(footpoint,
                    date=('20220703', date(2022, 7,29)),
                    platformname='Sentinel-2',
                    area_relation='contains',
                    cloudcoverpercentage=(0,60))

# download all results from the search
api.download_all(products) 
#print(products.items())


