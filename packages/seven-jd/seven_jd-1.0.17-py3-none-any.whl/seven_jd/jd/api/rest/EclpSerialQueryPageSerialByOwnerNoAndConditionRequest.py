from seven_jd.jd.api.base import RestApi

class EclpSerialQueryPageSerialByOwnerNoAndConditionRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.billType = None
			self.ownerNo = None
			self.startTime = None
			self.endTime = None
			self.warehouseNo = None
			self.pageNo = None
			self.pageSize = None
			self.queryType = None

		def getapiname(self):
			return 'jingdong.eclp.serial.queryPageSerialByOwnerNoAndCondition'

			





