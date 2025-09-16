from seven_jd.jd.api.base import RestApi

class VenderAuthFindUserRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.pin = None
			self.open_id_seller = None
			self.xid_seller = None

		def getapiname(self):
			return 'jingdong.vender.auth.findUser'

			





