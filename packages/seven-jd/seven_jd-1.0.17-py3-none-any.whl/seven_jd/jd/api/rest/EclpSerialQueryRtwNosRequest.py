from seven_jd.jd.api.base import RestApi

class EclpSerialQueryRtwNosRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.status = None
			self.startDate = None
			self.endDate = None
			self.pageStart = None
			self.pageSize = None
			self.source = None

		def getapiname(self):
			return 'jingdong.eclp.serial.queryRtwNos'

			





