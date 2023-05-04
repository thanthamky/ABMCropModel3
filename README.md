# ABMCropModel3

To query yield from crop model,

```python

import requests

url_yield = 'http://127.0.0.1:5001/crop_yield' # Max Process time about 1 min (Mac M1 pro)

params = {
          'rain': "[1800,2500]",
          'temp': "[20,35]",
          'diss': "False",
         }

with open('map_content.gz', 'rb') as file:
     file_data = {'file': file}
     response = requests.post(url_yield, params=params, files=file_data)
      data = response.json()
             
```
```
import requests

url_yield = 'http://127.0.0.1:5001/crop_yield_batch' # Max Process time about 1 min (Mac M1 pro)

params = {
    'rain': "[1800,2500]",
    'temp': "[20,35]",
    'diss': "True",
    'ij':"[1000,3500]",
    'shape':"[500,500]",
}

#data = {'data': map_com}
with open('map_content_500_500.gz', 'rb') as file:
    file_data = {'file': file}
    response = requests.post(url_yield, params=params, files=file_data)
    data = response.json()
  ```  


convert reponse data to pandas DaraFrame

```python
result = pd.DataFrame(json.loads(data['data']))
```


To Re-Simulate Crop Model
```python
url_sim = 'http://127.0.0.1:5001/crop_sim' # Max Process time about 10 min (Mac M1 pro)

response = requests.get(url_sim, timeout=600)
```
