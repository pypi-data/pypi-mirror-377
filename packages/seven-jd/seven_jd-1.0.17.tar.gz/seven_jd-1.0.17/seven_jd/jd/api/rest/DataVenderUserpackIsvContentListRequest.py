from seven_jd.jd.api.base import RestApi

class DataVenderUserpackIsvContentListRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.page_index = None
			self.page_size = None
			self.search_id = None

		def getapiname(self):
			return 'jingdong.data.vender.userpack.isv.content.list'

			





