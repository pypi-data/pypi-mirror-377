from seven_jd.jd.api.base import RestApi

class LdopDeliveryProviderCancelWayBillRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.userPin = None
			self.waybillCode = None
			self.customerCode = None
			self.source = None
			self.cancelReason = None
			self.operatorName = None
			self.open_id_buyer = None
			self.xid_buyer = None

		def getapiname(self):
			return 'jingdong.ldop.delivery.provider.cancelWayBill'

			





