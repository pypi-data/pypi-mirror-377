from seven_jd.jd.api.base import RestApi

class ArealimitWriteUpdateWareAreaLimitsRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.wareId = None
			self.areaId = None
			self.limitType = None

		def getapiname(self):
			return 'jingdong.arealimit.write.updateWareAreaLimits'

			





