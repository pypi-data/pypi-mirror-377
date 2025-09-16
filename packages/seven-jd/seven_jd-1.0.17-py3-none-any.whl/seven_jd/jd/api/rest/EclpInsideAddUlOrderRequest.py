from seven_jd.jd.api.base import RestApi

class EclpInsideAddUlOrderRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.outUlNo = None
			self.sellerNo = None
			self.warehouseNo = None
			self.deptNo = None
			self.deliveryMode = None
			self.ulType = None
			self.allowReturnDest = None
			self.allowLackDest = None
			self.destMethod = None
			self.destReason = None
			self.destCompNo = None
			self.receiver = None
			self.receiverPhone = None
			self.email = None
			self.province = None
			self.city = None
			self.county = None
			self.town = None
			self.address = None
			self.backEmail = None
			self.createUser = None
			self.createTime = None
			self.remark = None
			self.orderLine = None
			self.goodsNo = None
			self.goodsName = None
			self.planQty = None
			self.goodsLevel = None
			self.ulItemBatchRequest = None

		def getapiname(self):
			return 'jingdong.eclp.inside.addUlOrder'

			





