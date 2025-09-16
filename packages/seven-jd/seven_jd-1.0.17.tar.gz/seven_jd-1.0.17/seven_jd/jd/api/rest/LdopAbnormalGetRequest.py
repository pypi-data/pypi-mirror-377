from seven_jd.jd.api.base import RestApi

class LdopAbnormalGetRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.customerCode = None

		def getapiname(self):
			return 'jingdong.ldop.abnormal.get'

			





