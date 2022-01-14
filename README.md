# Description

Astro Photography Environmeny provides REST interface to control astrophotography setup end peroform deep-sky imaging from remote client.
### Features
* Nexstar mount control: goto coordinates, slew, and getting current position
* GPhoto2-compatible camera control: iso, shutter speed and image format setup, single-frame capturing


# Installation

* Install Python3
* Download project fiels `git pull https://github.com/denshustanov/APE-Server.git`
* Install all dependencies from requirements.txt `pip3 install -r requirements.txt`
* run app.py
# API Reference
# Camera Control
## Connect To Camera


**URL**: ``` /camera/connect ```

**Metohd**: `GET`

**Auth required** : YES

### Success Responce

**Condition** : GPhoto2-supported camera is available

**Code**: `200 OK`

**Content**: Connected camera config JSON

```json 
{
    "manufacturer": "Canon Inc.",
    "model": "Canon EOS 1200D",
    "shutter_counter": 30000,
    "iso":{
        "value": "800",
        "choices": [
        "100", "200", "400", "800", "1600", "3200", "6400", "Auto"
        ]
    },
    "image_format": {
        "value":"Tiny JPEG"
        "choices": [
            "Large Fine JPEG",
            "Large Normal JPEG",
            "Medium Fine JPEG",
            "Medium Normal JPEG",
            "Small Fine JPEG",
            "Small Normal JPEG",
            "Smaller JPEG",
            "Tiny JPEG",
            "RAW + Large Fine JPEG",
            "RAW"
        ],
    },
    "shutter_speed": {
        "choices":[
            "bulb",
            "30",
            "25",
            "20",
            "15",
            "13",
            "10.3",
            "8",
            "6.3",
            "5",
            "4",
            "3.2",
            "2.5",
            "2",
            "1.6",
            "1.3",
            "1",
            "0.8",
            "..."
        ],
        "value":"1/80"
    }
}
```

## Disconnect From Camera

**URL**: ``` /camera/disconnect ```

**Metohd**: `GET`

**Auth required** : YES

### Success Responce

**Code**: `200 OK`

## Set Camera Config

**URL**: ``` /camera/set-config ```

**Metohd**: `GET`

**Auth required** : YES
**Argumnets**: `setting, value`

### Success Responce

**Condition** : Camera is connected and request arguments are valid

**Code**: `200 OK`

## Capture image

**URL**: ``` /camera/capture ```

**Metohd**: `GET`

**Auth required** : YES

### Success Responce

**Condition** : camera is connected

**Code**: `200 OK`

**Content**: path to captured image file




