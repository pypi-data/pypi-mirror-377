import json
import os
import requests
import warnings

warnings.filterwarnings("ignore")

def httpRequest(path, body):
  url = 'https://api.sysopswork.com:3000'
  method = 'POST'
  headers = {'Content-type': 'application/json'}
  try:
    response = requests.post(url + path, headers = headers, data = body, verify=False)
    if response.status_code == 200 and response.json():
      parsed = response.json()
      if parsed and 'success' in parsed and parsed['success'] == True:
        return parsed
    return None
  except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
    exit(1)
  return response

def getInputVal(inputId):
  response = httpRequest('/api/script/input', '{"token":"' + str(os.getenv("SYSOPSWORK_TOKEN")) + '","inputId":"' + str(inputId) + '"}')
  if response is not None:
    return response["content"]
  return None

def getSecretVal(secretName):
  response = httpRequest('/api/script/secret', '{"token":"' + str(os.getenv("SYSOPSWORK_TOKEN")) + '","secretName":"' + str(secretName) + '"}')
  if response is not None:
    return response["content"]
  return None

def getVarVal(variableName):
  response = httpRequest('/api/script/variable', '{"token":"' + str(os.getenv("SYSOPSWORK_TOKEN")) + '","variableName":"' + str(variableName) + '"}')
  if response is not None:
    return response["content"]
  return None

def setUpdate(progress=0, message='', rollback=False, errCode=0, errMessage=''):
  response = None
  if errCode != 0 and errMessage != '':
    if rollback == True:
      response = httpRequest('/api/status', '{"token":"' + str(os.getenv("SYSOPSWORK_TOKEN")) + '","rollback":true,"errorCode":' + str(errCode) + ',"errorMessage":"' + str(errMessage) + '"}')
    else:
      response = httpRequest('/api/status', '{"token":"' + str(os.getenv("SYSOPSWORK_TOKEN")) + '","errorCode":' + str(errCode) + ',"errorMessage":"' + str(errMessage) + '"}')
  elif rollback == True:
    response = httpRequest('/api/status', '{"token":"' + str(os.getenv("SYSOPSWORK_TOKEN")) + '","rollback":true,"progress":' + str(progress) + ',"message":"' + str(message) + '"}')
  else:
    response = httpRequest('/api/status', '{"token":"' + str(os.getenv("SYSOPSWORK_TOKEN")) + '","progress":' + str(progress) + ',"message":"' + str(message) + '"}')
  if response is not None:
    return 'success'
  return None

def setVarVal(variableName, variableValue):
  response = httpRequest('/api/script/post', '{"token":"' + str(os.getenv("SYSOPSWORK_TOKEN")) + '","variableName":' + str(variableName) + ',"variableValue":"' + str(variableValue) + '"}')
  if response is not None:
    return 'success'
  return None

def fatalError(errCode, message):
  setUpdate(errCode=errCode, errMessage=message)
  exit(errCode)

if __name__ == "__main__":
    print("Import this script into your code by using:\r\nimport sysopswork")
