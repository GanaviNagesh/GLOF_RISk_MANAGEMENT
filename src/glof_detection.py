import ee
from twilio.rest import Client

# Initialize Earth Engine
ee.Initialize(project='glof-monitoring')

# Twilio credentials
account_sid = 'ACb4cfb2545615a0f2c93211efbf7e0ea2'
auth_token = '15d966829e374159ff43940744db077b'
twilio_number = '+1 903 494 7592'
recipient_number = '+918074361200'


def send_alert(message):
    client = Client(account_sid, auth_token)
    sms = client.messages.create(
        body=message,
        from_=twilio_number,
        to=recipient_number
    )
    print("✅ SMS sent:", sms.sid)


def check_glof_status(lake_name="imja-tsho"):
    # Define lat/lon for the 5 lakes
    lakes = {
        "imja-tsho": (86.9367, 27.8915),
        "tsho-rolpa": (86.9162, 27.9000),
        "thorthormi": (86.9250, 27.8990),
        "lumding": (86.9520, 27.8800),
        "digcho": (86.9490, 27.8850)
    }

    if lake_name not in lakes:
        return "Unknown Lake", 0

    lon, lat = lakes[lake_name]

    roi = ee.Geometry.Point(lon, lat)
    start_date = '2023-09-28'
    end_date = '2023-10-04'

    collection = (ee.ImageCollection('COPERNICUS/S2')
                  .filterDate(start_date, end_date)
                  .filterBounds(roi)
                  .sort('CLOUDY_PIXEL_PERCENTAGE'))

    image = collection.first()

    if image.getInfo():
        ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
        water = ndwi.gt(0.3)
        water_pixels = water.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=roi.buffer(1000),
            scale=10,
            maxPixels=1e9
        ).get('NDWI').getInfo()

        if water_pixels and water_pixels > 10000:
            return "GLOF Detected", water_pixels
        else:
            return "No GLOF Detected", water_pixels
    else:
        return "No image available", 0
