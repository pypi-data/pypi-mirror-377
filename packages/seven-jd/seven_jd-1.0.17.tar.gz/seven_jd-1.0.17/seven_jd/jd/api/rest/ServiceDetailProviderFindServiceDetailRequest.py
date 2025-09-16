from seven_jd.jd.api.base import RestApi

class ServiceDetailProviderFindServiceDetailRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.afsServiceId = None
			self.appendInfoStep = None
			self.operatorPin = None
			self.operatorNick = None
			self.operatorRemark = None
			self.operatorDate = None
			self.platformSrc = None

		def getapiname(self):
			return 'jingdong.ServiceDetailProvider.findServiceDetail'

			





