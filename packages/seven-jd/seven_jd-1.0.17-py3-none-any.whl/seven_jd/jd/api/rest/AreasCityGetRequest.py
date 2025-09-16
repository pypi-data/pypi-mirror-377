from seven_jd.jd.api.base import RestApi

class AreasCityGetRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.parent_id = None

		def getapiname(self):
			return 'jingdong.areas.city.get'

			





