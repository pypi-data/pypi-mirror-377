from seven_jd.jd.api.base import RestApi

class MarketSmscardTemplateQueryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.templateId = None

		def getapiname(self):
			return 'jingdong.market.smscard.template.query'

			





