from seven_jd.jd.api.base import RestApi

class EtmsPackageUpdateRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.customerCode = None
			self.deliveryId = None
			self.packageCount = None
			self.boxCodeList = None

		def getapiname(self):
			return 'jingdong.etms.package.update'

			





