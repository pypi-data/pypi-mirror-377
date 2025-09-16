from seven_jd.jd.api.base import RestApi

class ConvertFourAreaByLatLngRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.latitude = None
			self.longitude = None

		def getapiname(self):
			return 'jingdong.convertFourAreaByLatLng'

			





