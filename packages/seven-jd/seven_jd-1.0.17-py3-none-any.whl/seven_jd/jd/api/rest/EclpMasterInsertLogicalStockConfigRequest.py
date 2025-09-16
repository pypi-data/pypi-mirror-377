from seven_jd.jd.api.base import RestApi

class EclpMasterInsertLogicalStockConfigRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.sellerNo = None
			self.deptNo = None
			self.sellerName = None
			self.deptName = None
			self.factor1No = None
			self.factor1Name = None
			self.factor2No = None
			self.factor2Name = None
			self.factor3No = None
			self.factor3Name = None
			self.factor4No = None
			self.factor4Name = None

		def getapiname(self):
			return 'jingdong.eclp.master.insertLogicalStockConfig'

			





