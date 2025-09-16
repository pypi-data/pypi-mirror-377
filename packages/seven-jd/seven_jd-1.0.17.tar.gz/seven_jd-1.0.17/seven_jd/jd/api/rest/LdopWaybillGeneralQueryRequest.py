from seven_jd.jd.api.base import RestApi

class LdopWaybillGeneralQueryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.customerCode = None
			self.deliveryId = None
			self.phone = None
			self.dynamicTimeFlag = None

		def getapiname(self):
			return 'jingdong.ldop.waybill.generalQuery'

			





