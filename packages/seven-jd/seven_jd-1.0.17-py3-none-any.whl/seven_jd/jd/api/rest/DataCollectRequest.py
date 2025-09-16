from seven_jd.jd.api.base import RestApi

class DataCollectRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.data_class = None
			self.data = None

		def getapiname(self):
			return 'jingdong.data.collect'

			





