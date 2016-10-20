import io
import requests
from requests_ntlm import HttpNtlmAuth
import getpass

def save_report(path, file, user='jonathan.craton', password=None):
  """ Saves a report to a file """

  print("Downloading %s..." % path)
   
  url = 'https://sqlstudentrecs.houghton.edu/ReportsWebService?%s&rs:ParameterLanguage=&rs:Command=Render&rs:Format=CSV' % path
  
  requests.packages.urllib3.disable_warnings()
  response = requests.get(url, auth=HttpNtlmAuth(
      'houghton\\%s' % user,
      password or getpass.getpass()),
      verify=False)
  response_file = io.StringIO(response.text)
  response_file.seek(1)
  
  with open(file, "w") as fout:
    for line in response_file:
        fout.write(line)
    
if __name__ == '__main__':
  password = getpass.getpass()
  
  save_report('/Student+Life/Retention+Analysis', 'data.csv', password = password)
  save_report('/Housing+(managed)/tables/people', 'people.csv', password = password)