from seven_jd.jd.api.base import RestApi

class AreasOverseasCityGetRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.parentId = None

		def getapiname(self):
			return 'jingdong.areas.overseasCity.get'

			





