from seven_jd.jd.api.base import RestApi

class StationinfojosserviceDeleteRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.companyCode = None
			self.stationCode = None

		def getapiname(self):
			return 'jingdong.stationinfojosservice.delete'

			





