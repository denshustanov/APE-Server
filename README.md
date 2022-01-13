#Installation
* Install Python3
* Install all dependencies from requirements.txt
* run app.py
# API Reference
# Camera Control
### Connect To Camera
***

**URL**: ``` /camera/connect ```

**Metohd**: `GET`

**Auth required** : YES

###Success Responce
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
    }
}
```


