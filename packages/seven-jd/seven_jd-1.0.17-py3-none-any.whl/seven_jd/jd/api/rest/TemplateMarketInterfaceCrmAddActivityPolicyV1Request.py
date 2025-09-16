from seven_jd.jd.api.base import RestApi

class TemplateMarketInterfaceCrmAddActivityPolicyV1Request(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.venderId = None
			self.activityId = None
			self.interestId = None
			self.projectId = None
			self.subSystemType = None

		def getapiname(self):
			return 'jingdong.template.market.interface.crm.addActivityPolicyV1'

			





