from seven_jd.jd.api.base import RestApi

class EclpB2cPromiseInfoApiQueryWaybillFreightsRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.vendorCode = None
			self.orderId = None
			self.waybillCode = None

		def getapiname(self):
			return 'jingdong.eclp.b2c.PromiseInfoApi.queryWaybillFreights'

			





