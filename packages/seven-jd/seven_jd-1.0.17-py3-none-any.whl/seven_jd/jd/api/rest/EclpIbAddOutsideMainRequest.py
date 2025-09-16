from seven_jd.jd.api.base import RestApi

class EclpIbAddOutsideMainRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.outsideSource = None
			self.selfLiftCode = None
			self.warehouseNoIn = None
			self.isvOutsideNo = None
			self.shipperNo = None
			self.deptNo = None
			self.warehouseNoOut = None
			self.goodsNo = None
			self.planNum = None
			self.batAttrListJson = None

		def getapiname(self):
			return 'jingdong.eclp.ib.addOutsideMain'

			





