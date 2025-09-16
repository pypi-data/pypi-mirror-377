from seven_jd.jd.api.base import RestApi

class JosIsvTokenEncryptionRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.tokenStr = None

		def getapiname(self):
			return 'jingdong.jos.isv.token.encryption'

			





