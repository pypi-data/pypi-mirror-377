from seven_jd.jd.api.base import RestApi

class IerpSaasYtAddUserAndAccountRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.isSuper = None
			self.sex = None
			self.mobile = None
			self.userName = None
			self.clientIp = None
			self.roleCode = None
			self.outPin = None
			self.email = None
			self.deptCode = None
			self.status = None
			self.operatorPin = None
			self.requestId = None
			self.tenantToken = None

		def getapiname(self):
			return 'jingdong.ierp.saas.yt.addUserAndAccount'

			





