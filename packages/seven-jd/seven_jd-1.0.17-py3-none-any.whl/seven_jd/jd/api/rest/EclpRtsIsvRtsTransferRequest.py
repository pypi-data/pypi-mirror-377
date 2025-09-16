from seven_jd.jd.api.base import RestApi

class EclpRtsIsvRtsTransferRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.eclpRtsNo = None
			self.isvRtsNum = None
			self.rtsType = None
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
			self.createUser = None
			self.packFlag = None
			self.allowLack = None
			self.logicParam = None
			self.remark = None
			self.purchaser = None
			self.customField = None
			self.sellerBizType = None
			self.insuredPrice = None
			self.deptGoodsNo = None
			self.goodsName = None
			self.quantity = None
			self.realQuantity = None
			self.goodsStatus = None
			self.goodsLevel = None
			self.lotProductionBatchNo = None
			self.lotProductionDate = None
			self.lotSupplier = None
			self.batAttrListJson = None
			self.goodsPrice = None
			self.totalAmount = None
			self.isvGoodsNo = None
			self.orderLine = None

		def getapiname(self):
			return 'jingdong.eclp.rts.isvRtsTransfer'

			





