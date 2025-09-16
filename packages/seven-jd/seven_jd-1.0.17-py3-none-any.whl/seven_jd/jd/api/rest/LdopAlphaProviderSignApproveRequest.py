from seven_jd.jd.api.base import RestApi

class LdopAlphaProviderSignApproveRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.requestId = None
			self.approveResult = None
			self.approveMessage = None

		def getapiname(self):
			return 'jingdong.ldop.alpha.provider.sign.approve'

			





