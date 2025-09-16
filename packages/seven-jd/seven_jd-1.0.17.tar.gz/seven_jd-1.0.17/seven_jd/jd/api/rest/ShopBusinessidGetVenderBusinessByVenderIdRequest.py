from seven_jd.jd.api.base import RestApi

class ShopBusinessidGetVenderBusinessByVenderIdRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.i18nParam = None

		def getapiname(self):
			return 'jingdong.shop.businessid.getVenderBusinessByVenderId'

			
	

class I18nParam(object):
		def __init__(self):
			"""
			"""





