from lga import LGA

# Dear Tuck, all you need is the class LGA from lga.py
# HOW TO RUN
# cd twitter-analytics-team32/Web
# python config_web.py http://115.146.92.171
# python tuck.py

lga = LGA()
d = lga.get_centre_coord_and_radius()
print(d)
