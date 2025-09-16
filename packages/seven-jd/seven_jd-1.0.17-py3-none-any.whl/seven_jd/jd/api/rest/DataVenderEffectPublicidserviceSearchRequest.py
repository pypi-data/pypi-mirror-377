from seven_jd.jd.api.base import RestApi

class DataVenderEffectPublicidserviceSearchRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.page = None
			self.page_size = None
			self.start_date = None
			self.end_date = None
			self.wechat_publicid = None

		def getapiname(self):
			return 'jingdong.data.vender.effect.publicidservice.search'

			





