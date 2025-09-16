from seven_jd.jd.api.base import RestApi

class DataVenderSubPackGetRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.parent_search_id = None

		def getapiname(self):
			return 'jingdong.data.vender.sub.pack.get'

			





