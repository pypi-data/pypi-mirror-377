from seven_jd.jd.api.base import RestApi

class JingdongDataVenderMarketingActivityUpdateSubmitRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.mkt_activity_id = None
			self.mkt_task_execute_time_plan = None
			self.task_desc = None
			self.task_type = None
			self.next_tasks = None
			self.task_name = None
			self.pre_tasks = None
			self.task_id = None
			self.extra_info = None

		def getapiname(self):
			return 'jingdong.jingdong.data.vender.marketing.activity.update.submit'

			





