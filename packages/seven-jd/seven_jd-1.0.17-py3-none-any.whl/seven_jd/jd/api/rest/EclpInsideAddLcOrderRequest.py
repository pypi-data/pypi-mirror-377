from seven_jd.jd.api.base import RestApi

class EclpInsideAddLcOrderRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.sellerLcNo = None
			self.sellerNo = None
			self.wareHouseNo = None
			self.deptNo = None
			self.outsideLogicStock = None
			self.insideLogicStock = None
			self.lack = None
			self.orderLine = None
			self.isvGoodsNo = None
			self.outGoodsLevel = None
			self.inGoodsLevel = None
			self.planQty = None

		def getapiname(self):
			return 'jingdong.eclp.inside.addLcOrder'

			





