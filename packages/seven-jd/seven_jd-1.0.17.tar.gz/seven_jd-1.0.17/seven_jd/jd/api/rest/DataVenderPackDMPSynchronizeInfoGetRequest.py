from seven_jd.jd.api.base import RestApi

class DataVenderPackDMPSynchronizeInfoGetRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.record_id = None
			self.page_index = None
			self.page_size = None

		def getapiname(self):
			return 'jingdong.data.vender.pack.DMP.synchronize.info.get'

			





