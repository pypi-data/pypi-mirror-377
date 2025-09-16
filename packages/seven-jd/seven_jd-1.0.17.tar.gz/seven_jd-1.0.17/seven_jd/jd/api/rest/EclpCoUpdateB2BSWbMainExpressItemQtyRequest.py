from seven_jd.jd.api.base import RestApi

class EclpCoUpdateB2BSWbMainExpressItemQtyRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.newWBType = None
			self.no = None
			self.expressItemQty = None
			self.extendFieldStr = None

		def getapiname(self):
			return 'jingdong.eclp.co.updateB2BSWbMainExpressItemQty'

			





