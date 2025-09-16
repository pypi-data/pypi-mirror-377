from seven_jd.jd.api.base import RestApi

class EclpCloudQueryOrderInfoRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.machiningNo = None
			self.machiningType = None
			self.timeStart = None
			self.timeEnd = None
			self.warehouseNo = None
			self.tenantId = None

		def getapiname(self):
			return 'jingdong.eclp.cloud.queryOrderInfo'

			





