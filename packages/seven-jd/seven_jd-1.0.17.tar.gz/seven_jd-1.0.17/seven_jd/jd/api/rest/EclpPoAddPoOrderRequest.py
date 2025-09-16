from seven_jd.jd.api.base import RestApi

class EclpPoAddPoOrderRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.spPoOrderNo = None
			self.deptNo = None
			self.referenceOrder = None
			self.inboundRemark = None
			self.buyer = None
			self.logicParam = None
			self.supplierNo = None
			self.sellerSaleOrder = None
			self.saleOrder = None
			self.orderMark = None
			self.billType = None
			self.acceptUnQcFlag = None
			self.boxFlag = None
			self.entirePrice = None
			self.boxNo = None
			self.boxGoodsNo = None
			self.boxGoodsQty = None
			self.boxSerialNo = None
			self.boxIsvGoodsNo = None
			self.poReturnMode = None
			self.customsInfo = None
			self.poType = None
			self.billOfLading = None
			self.receiveLevel = None
			self.multiReceivingFlag = None
			self.waybillNo = None
			self.isvOutWarehouse = None
			self.bizType = None
			self.waitBoxDetailFlag = None
			self.unitFlag = None
			self.serialDetailMapJson = None
			self.serialNoScopeMapJson = None
			self.allowLackFlag = None
			self.isUpdate = None
			self.sellerOrderType = None
			self.customField = None
			self.sellerWarehouseNo = None
			self.whNo = None
			self.soNo = None
			self.deptGoodsNo = None
			self.isvGoodsNo = None
			self.numApplication = None
			self.goodsStatus = None
			self.barCodeType = None
			self.sidCheckout = None
			self.unitPrice = None
			self.totalPrice = None
			self.qualityCheckRate = None
			self.batAttrListJson = None
			self.orderLine = None
			self.isvLotattrs = None
			self.checkLotattrs = None
			self.goodsPrice = None
			self.warehousingFlag = None
			self.isvGoodsUnit = None

		def getapiname(self):
			return 'jingdong.eclp.po.addPoOrder'

			





