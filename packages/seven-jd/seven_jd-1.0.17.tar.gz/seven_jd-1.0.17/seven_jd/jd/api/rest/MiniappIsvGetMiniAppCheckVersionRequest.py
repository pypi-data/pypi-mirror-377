from seven_jd.jd.api.base import RestApi

class MiniappIsvGetMiniAppCheckVersionRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.requestVO = None

		def getapiname(self):
			return 'jingdong.miniapp.isv.getMiniAppCheckVersion'

			
	

class RequestVO(object):
		def __init__(self):
			"""
			"""
			self.IsvAppId = None
			self.appId = None





