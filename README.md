# ABMCropModel3

To simulate crop model,

'''python

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
             
'''
