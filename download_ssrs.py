""" Downloads reports as CSV files from SSRS

Usage: python3 download_ssrs.py some_path=outfile.csv
"""

import io
import requests
from requests_ntlm import HttpNtlmAuth
import getpass
import config
import sys

def save_report(path, outfile, user, password):
  """ Saves a report to a file """

  print("Downloading %s..." % path)
   
  url = '%s?%s&rs:ParameterLanguage=&rs:Command=Render&rs:Format=CSV' % (config.ssrs_url, path)
  
  requests.packages.urllib3.disable_warnings()
  response = requests.get(url, auth=HttpNtlmAuth(
      user,
      password),
      verify=False)
  response_file = io.StringIO(response.text)
  response_file.seek(1)
  
  with open(outfile, "w") as fout:
    for line in response_file:
        fout.write(line)
    
if __name__ == '__main__':
  password = config.ssrs_password if hasattr(config, 'ssrs_password') else getpass.getpass()

  for arg in sys.argv[1:]:
    [path,outfile] = arg.split('=')
    save_report(path, outfile, config.ssrs_user, password)