from seven_jd.jd.api.base import RestApi

class DataVenderUserpackIsvDeleteRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.search_id = None

		def getapiname(self):
			return 'jingdong.data.vender.userpack.isv.delete'

			





