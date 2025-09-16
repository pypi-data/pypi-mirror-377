
import PythonAPIClientBase
from .LoginSession import AdminLoginSession
import json
import requests
import copy
from .Types import UserObj
from .Workflows import Workflows

# From TestHelperSuperclass. Second version is reversed
infoAPIPrefix = '/api/public/info'
infoutilityAPIPrefix = '/api/public/infoutility'
loginAPIPrefix = '/api/public/login'
privateUserAPIPrefix = '/api/private/user'
privateAdminAPIPrefix = '/api/private/admin'

infoAPIPrefixExt = '/public/api/info'
infoutilityAPIPrefixExt = '/public/api/infoutility'
loginAPIPrefixExt = '/public/api/login'
privateUserAPIPrefixExt = '/private/api/user'
privateAdminAPIPrefixExt = '/private/api/admin'

frontend_instance_map = {
    "dev": {
        "url": "http://localhost:9000/#"
    },
    "prod": {
        "url": "https://evernetproperties.com/#"
    }
}

class ApiClient(PythonAPIClientBase.APIClientBase):
  frontend_instance = None

  def __init__(self, baseURL, frontend_instance, mock=None, verboseLogging=PythonAPIClientBase.VerboseLoggingNullLogClass()):
    super().__init__(baseURL=baseURL, mock=mock, forceOneRequestAtATime=True, verboseLogging=verboseLogging)
    self.frontend_instance = frontend_instance

  def get_frontend_instance_data(self):
    return frontend_instance_map[self.frontend_instance]

  def sendInfoApiRequest(
      self,
      reqFn,
      origin,
      url,
      data,
      loginSession,
      injectHeadersFn,
      skipLockCheck
  ):
    return self.sendRequest(
      reqFn=reqFn,
      origin=origin,
      url=infoAPIPrefixExt + url,
      data=data,
      loginSession=loginSession,
      injectHeadersFn=injectHeadersFn,
      skipLockCheck=skipLockCheck
    )

  def sendLoginApiRequest(
      self,
      reqFn,
      origin,
      url,
      data,
      loginSession,
      injectHeadersFn,
      skipLockCheck
  ):
    return self.sendRequest(
      reqFn=reqFn,
      origin=origin,
      url=loginAPIPrefixExt + url,
      data=data,
      loginSession=loginSession,
      injectHeadersFn=injectHeadersFn,
      skipLockCheck=skipLockCheck
    )

  def sendUserApiRequest(
      self,
      reqFn,
      origin,
      url,
      data,
      loginSession,
      injectHeadersFn,
      skipLockCheck
  ):
    return self.sendRequest(
      reqFn=reqFn,
      origin=origin,
      url=privateUserAPIPrefixExt + url,
      data=data,
      loginSession=loginSession,
      injectHeadersFn=injectHeadersFn,
      skipLockCheck=skipLockCheck
    )

  def sendAdminApiRequest(
      self,
      reqFn,
      origin,
      url,
      data,
      loginSession,
      injectHeadersFn,
      skipLockCheck,
      params = None
  ):
    return self.sendRequest(
      reqFn=reqFn,
      origin=origin,
      url=privateAdminAPIPrefixExt + url,
      data=data,
      params=params,
      loginSession=loginSession,
      injectHeadersFn=injectHeadersFn,
      skipLockCheck=skipLockCheck
    )

  def sendInfoUtilityApiRequest(
      self,
      reqFn,
      origin,
      url,
      data,
      injectHeadersFn,
      skipLockCheck,
      params = None
  ):
    return self.sendRequest(
      reqFn=reqFn,
      origin=origin,
      url=infoutilityAPIPrefixExt + url,
      data=data,
      params=params,
      loginSession=None,
      injectHeadersFn=injectHeadersFn,
      skipLockCheck=skipLockCheck
    )

  def getServerInfo(self):
    url = "/serverinfo"
    result = self.sendInfoApiRequest(
      reqFn=requests.get,
      origin=None,
      url=url,
      data=None,
      loginSession=None,
      injectHeadersFn=None,
      skipLockCheck=True
    )
    if result.status_code != 200:
      print("Error Calling url:", url)
      print("Response code:", result.status_code)
      print("Response text:", result.text)
      raise Exception("Could not get server info")
    return json.loads(result.text)

  def getLoginSession(self, apikey):
    return AdminLoginSession(APIClient=self, apikey=apikey)

  def getMyProfile(self, loginSession):
    result = self.sendUserApiRequest(
      reqFn=requests.get,
      origin=None,
      url="/me",
      data=None,
      loginSession=loginSession,
      injectHeadersFn=None,
      skipLockCheck=True
    )
    if result.status_code != 200:
      print("Error getting user profile")
      print("status", result.status_code)
      print("response", result.text)
      raise Exception("Error getting user profile")
    resultJson = json.loads(result.text)
    return resultJson

  def getsUsers(self, loginSession):
    offset = 0
    result_items = []

    while True:
      result = self.sendAdminApiRequest(
        reqFn=requests.get,
        origin=None,
        url="/users",
        params={
          "pagesize": 1,
          "offset": offset
        },
        data=None,
        loginSession=loginSession,
        injectHeadersFn=None,
        skipLockCheck=True
      )
      if result.status_code != 200:
        print("Error getting user profile")
        print("status", result.status_code)
        print("response", result.text)
        raise Exception("Error getting user profile")
      resultJson = json.loads(result.text)
      result_items += resultJson["result"]
      offset += resultJson["pagination"]["pagesize"]
      if len(resultJson["result"]) == 0:
        break

    resultObjs = []
    for curresult in result_items:
      resultObjs.append(UserObj(curresult))

    return resultObjs

  def getPatch(self, loginSession, patchid, adminMode=False):
    fn = self.sendUserApiRequest
    if adminMode:
      fn = self.sendAdminApiRequest
    result = fn(
      reqFn=requests.get,
      origin=None,
      url="/patches/" + patchid,
      data=None,
      loginSession=loginSession,
      injectHeadersFn=None,
      skipLockCheck=True
    )
    if result.status_code != 200:
      print("Error getting patch")
      print("status", result.status_code)
      print("response", result.text)
      raise Exception("Error getting patch")
    resultJson = json.loads(result.text)
    return resultJson

  def updatePatch(self, loginSession, patchDict):
    # I build this to fix workflow
    #  but didn't need to use it because loading and resaving the project clears the data error
    raise Exception("Untested")
    result = self.sendAdminApiRequest(
      reqFn=requests.post,
      origin=None,
      url="/patches",
      data=json.dumps(copy.deepcopy(patchDict)),
      loginSession=loginSession,
      injectHeadersFn=None,
      skipLockCheck=True
    )
    if result.status_code != 200:
      print("Error updating patch")
      print("status", result.status_code)
      print("response", result.text)
      raise Exception("Error updating patch")
    resultJson = json.loads(result.text)
    return resultJson

  def getProject(self, loginSession, projectid, adminMode=False):
    fn = self.sendUserApiRequest
    if adminMode:
      fn = self.sendAdminApiRequest
    result = fn(
      reqFn=requests.get,
      origin=None,
      url="/projects/" + projectid,
      data=None,
      loginSession=loginSession,
      injectHeadersFn=None,
      skipLockCheck=True
    )
    if result.status_code != 200:
      print("Error getting project")
      print("status", result.status_code)
      print("response", result.text)
      raise Exception("Error getting project")
    resultJson = json.loads(result.text)
    return resultJson

  def upsertProject(self, loginSession, projectDict, adminMode=False):
    fn = self.sendUserApiRequest
    if adminMode:
      fn = self.sendAdminApiRequest
    result = fn(
      reqFn=requests.post,
      origin=None,
      url="/projects",
      data=json.dumps(projectDict),
      loginSession=loginSession,
      injectHeadersFn=None,
      skipLockCheck=True
    )
    if result.status_code != 200:
      print("Error upserting project")
      print("status", result.status_code)
      print("response", result.text)
      raise Exception("Error upserting project")
    resultJson = json.loads(result.text)
    return resultJson

  def getStaticWorkflows(self, raw=False):
    fn = self.sendInfoUtilityApiRequest
    result = fn(
      reqFn=requests.get,
      origin="https://evernetproperties.com",
      url="/static/workflows",
      data=None,
      injectHeadersFn=None,
      skipLockCheck=True
    )
    if result.status_code != 200:
      print("Error getting workflow")
      print("status", result.status_code)
      print("response", result.text)
      raise Exception("Error getting workflow")
    resultJson = json.loads(result.text)
    if isinstance(resultJson, str):
      raise Exception("Bad origin supplied")
    if raw:
      return resultJson
    return Workflows(resultJson)
