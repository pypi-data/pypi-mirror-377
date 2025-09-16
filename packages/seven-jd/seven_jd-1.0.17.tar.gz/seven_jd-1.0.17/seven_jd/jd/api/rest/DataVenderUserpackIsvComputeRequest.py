from seven_jd.jd.api.base import RestApi

class DataVenderUserpackIsvComputeRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.result_name = None
			self.result_desc = None
			self.condition = None
			self.callback = None

		def getapiname(self):
			return 'jingdong.data.vender.userpack.isv.compute'

			





