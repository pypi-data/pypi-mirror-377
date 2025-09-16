from seven_jd.jd.api.base import RestApi

class PopCrmAddCouponRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.vender_name = None
			self.validate_days = None
			self.quota = None
			self.discount = None
			self.start_time = None
			self.shop_id = None
			self.end_time = None
			self.batch_count = None
			self.mkt_activity_id = None
			self.app_key = None
			self.task_inst_id = None
			self.mkt_activity_inst_id = None
			self.task_id = None
			self.marketing_name = None
			self.strategy_inst_id = None
			self.customer_count = None

		def getapiname(self):
			return 'jingdong.pop.crm.addCoupon'

			





