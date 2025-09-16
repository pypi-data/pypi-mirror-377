from seven_jd.jd.api.base import RestApi

class PopCrmHomePageGetMemberRuleDataRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.buid = None
			self.timezone = None
			self.ip = None
			self.nationId = None
			self.verticalTag = None
			self.language = None
			self.verticalSite = None
			self.terminal = None
			self.value1 = None
			self.site = None
			self.horizontalTag = None
			self.tenantId = None
			self.currency = None

		def getapiname(self):
			return 'jingdong.pop.crm.homePage.getMemberRuleData'

			





