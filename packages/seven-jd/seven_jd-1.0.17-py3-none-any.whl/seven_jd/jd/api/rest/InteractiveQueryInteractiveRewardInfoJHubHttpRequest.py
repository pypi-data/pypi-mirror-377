from seven_jd.jd.api.base import RestApi

class InteractiveQueryInteractiveRewardInfoJHubHttpRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.sysParam = None
			self.interactiveRewardParam = None

		def getapiname(self):
			return 'jingdong.interactive.queryInteractiveRewardInfoJHubHttp'

			
	

class SysParam(object):
		def __init__(self):
			"""
			"""
			self.sourceCode = None
			self.appKey = None


class InteractiveRewardParam(object):
		def __init__(self):
			"""
			"""
			self.ext = None
			self.encryptProjectPoolId = None
			self.account = None
			self.encryptProjectId = None
			self.encryptAssignmentIds = None
			self.projectFailRewardsFlag = None
			self.open_id_buyer = None
			self.xid_buyer = None





