from seven_jd.jd.api.base import RestApi

class DataVenderPackDivideRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.sub_pack_ration = None
			self.parent_search_id = None
			self.sub_pack_cnt = None

		def getapiname(self):
			return 'jingdong.data.vender.pack.divide'

			





