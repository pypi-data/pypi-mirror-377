from seven_jd.jd.api.base import RestApi

class DropshipDpsSearchAllOrdersRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.pageSize = None
			self.page = None
			self.beginDate = None
			self.endDate = None
			self.modifiedBeginDate = None
			self.modifiedEndDate = None
			self.pin_buyer = None
			self.open_id_buyer = None
			self.xid_buyer = None

		def getapiname(self):
			return 'jingdong.dropship.dps.searchAllOrders'

			





