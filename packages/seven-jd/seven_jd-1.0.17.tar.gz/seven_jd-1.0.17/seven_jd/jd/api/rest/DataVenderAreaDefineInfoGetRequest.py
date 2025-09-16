from seven_jd.jd.api.base import RestApi

class DataVenderAreaDefineInfoGetRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.area_level = None

		def getapiname(self):
			return 'jingdong.data.vender.area.define.info.get'

			





