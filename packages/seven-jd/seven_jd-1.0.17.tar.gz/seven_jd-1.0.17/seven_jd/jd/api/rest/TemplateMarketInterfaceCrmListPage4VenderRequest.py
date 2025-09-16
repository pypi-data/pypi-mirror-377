from seven_jd.jd.api.base import RestApi

class TemplateMarketInterfaceCrmListPage4VenderRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.venderId = None
			self.pageNo = None
			self.pageSize = None

		def getapiname(self):
			return 'jingdong.template.market.interface.crm.listPage4Vender'

			





