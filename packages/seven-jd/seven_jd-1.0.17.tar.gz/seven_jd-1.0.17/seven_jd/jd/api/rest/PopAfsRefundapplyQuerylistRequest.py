from seven_jd.jd.api.base import RestApi

class PopAfsRefundapplyQuerylistRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.status = None
			self.id = None
			self.order_id = None
			self.buyer_id = None
			self.buyer_name = None
			self.apply_time_start = None
			self.apply_time_end = None
			self.check_time_start = None
			self.check_time_end = None
			self.page_index = None
			self.page_size = None

		def getapiname(self):
			return 'jingdong.pop.afs.refundapply.querylist'

			





