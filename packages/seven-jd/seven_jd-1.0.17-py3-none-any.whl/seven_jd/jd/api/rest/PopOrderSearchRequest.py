from seven_jd.jd.api.base import RestApi

class PopOrderSearchRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.start_date = None
			self.end_date = None
			self.order_state = None
			self.optional_fields = None
			self.page = None
			self.page_size = None
			self.sortType = None
			self.dateType = None
			self.realPin = None
			self.open_id_buyer = None
			self.xid_buyer = None

		def getapiname(self):
			return 'jingdong.pop.order.search'

			





