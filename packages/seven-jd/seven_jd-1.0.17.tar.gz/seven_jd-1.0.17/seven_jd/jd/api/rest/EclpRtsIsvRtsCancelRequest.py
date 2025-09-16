from seven_jd.jd.api.base import RestApi

class EclpRtsIsvRtsCancelRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.eclpRtsNo = None
			self.isvRtsNum = None
			self.deptNo = None
			self.deliveryMode = None
			self.warehouseNo = None
			self.supplierNo = None
			self.receiver = None
			self.receiverPhone = None
			self.email = None
			self.province = None
			self.city = None
			self.county = None
			self.town = None
			self.address = None
			self.deptGoodsNo = None
			self.goodsName = None
			self.quantity = None
			self.realQuantity = None
			self.goodsStatus = None

		def getapiname(self):
			return 'jingdong.eclp.rts.isvRtsCancel'

			





