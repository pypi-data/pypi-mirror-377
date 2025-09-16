from seven_jd.jd.api.base import RestApi

class JosOpenidGetCustomerPointRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.openId = None
			self.xId = None
			self.brandsId = None

		def getapiname(self):
			return 'jingdong.jos.openid.getCustomerPoint'

			





