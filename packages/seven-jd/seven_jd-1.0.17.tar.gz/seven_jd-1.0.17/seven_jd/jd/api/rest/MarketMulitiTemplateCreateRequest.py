from seven_jd.jd.api.base import RestApi

class MarketMulitiTemplateCreateRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.mulitiTemplateVo = None

		def getapiname(self):
			return 'jingdong.market.muliti.template.create'

			
	

class MulitiContentVo(object):
		def __init__(self):
			"""
			"""
			self.messageTxt = None
			self.mulitiFileName = None
			self.busiType = None
			self.url = None
			self.md5 = None
			self.order = None


class MulitiTemplateVo(object):
		def __init__(self):
			"""
			"""
			self.contents = None
			self.templateTheme = None





