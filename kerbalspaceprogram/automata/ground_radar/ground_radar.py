
import krpc

import numpy as np
from numpy import linspace


from PIL import Image

from time import sleep
from pprint import pprint


def make_image(data, mode='L'):
    img = Image.fromarray(data, mode=mode)
    return img

def normalize(input_data, max_value=255, astype=np.ubyte, copy=True):
    if copy:
        data = input_data.copy()
    else:
        data = input_data
        
    minimum, maximum = data.min(), data.max()
    data -= minimum
    data /= (maximum - minimum)
    data *= max_value
    return data.astype(astype, copy=False)


def scanline(lat, lon, height_func, distance=0.5, resolution=200):
    radius = distance / 2
    grid = np.array((
        linspace( lat - radius, lat + radius, num=resolution, endpoint=True),
        linspace( lon - radius, lon + radius, num=resolution, endpoint=True),
    ))
    
    scan = ( list(height_func(x,y) for x in grid[0]) for y in grid[1] )
    scan = np.array(list(scan))
    scan = np.rot90(scan) # Why can't I get the data correct on input??

    return (grid, scan)


   


if __name__ == "__main__":
    
    conn = krpc.connect(name='default')
    
    sc = conn.space_center
    v = vessel = sc.active_vessel
    body = vessel.orbit.body

    obt_a_frame = vessel.orbit.body.non_rotating_reference_frame
    obt_b_frame = vessel.orbit.body.orbital_reference_frame

    body_frame = vessel.orbit.body.reference_frame    
    srf_frame = vessel.surface_reference_frame

    flight = vessel.flight(body_frame)


    lat, lon = flight.latitude, flight.longitude
    lat, lon = round(lat, 6), round(lon, 6)
    print(f'{lat=}')
    print(f'{lon=}')


##    height_func = body.surface_height
    height_func = body.bedrock_height
    lat, lon = flight.latitude, flight.longitude
    
    distance = 30
    resolution = 200
    
    print("Scanning Terrain")
    grid, data = scanline(lat, lon, height_func, distance=distance, resolution=resolution)
    
    print("Making Image")

##    data = np.diff(data)   
    img = make_image(normalize(data))
    img.save(f'render-{distance}-{data.shape}.png', 'PNG')




            
        
        

    
