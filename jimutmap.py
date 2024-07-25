STEP = 0.01
ZOOM = 16
VERBOSE = True
THREADS_ = 12
GET_MASKS = False
V_NUMBER = 9651
SQL_DBS = ['sticher.sqlite', 'temp_sanity.sqlite']
TIME_SLEEP = 1
def get_req_img_url(xTile, yTile):
    req_url = f"https://sat-cdn1.apple-mapkit.com/tile?style=7&size=1&scale=1&z={self.zoom}&x={xTile}&y={yTile}&v={self.v_number}&accessKey={self.access_key}"
    return req_url

