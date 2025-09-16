from seven_jd.jd.api.base import RestApi

class EclpCollectorQueryMaintenanceResultRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.startTime = None
			self.deptNo = None
			self.endTime = None
			self.warehouseNo = None

		def getapiname(self):
			return 'jingdong.eclp.collector.queryMaintenanceResult'

			





