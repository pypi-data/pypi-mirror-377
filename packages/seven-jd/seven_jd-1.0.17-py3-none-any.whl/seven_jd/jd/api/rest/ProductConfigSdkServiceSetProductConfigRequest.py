from seven_jd.jd.api.base import RestApi

class ProductConfigSdkServiceSetProductConfigRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.productConfigReq = None

		def getapiname(self):
			return 'jingdong.productConfigSdkService.setProductConfig'

			
	

class Attribute1(object):
		def __init__(self):
			"""
			"""
			self.skuStockNum = None
			self.promiseDays = None
			self.czFlag = None
			self.skuId = None


class ProductConfigReq(object):
		def __init__(self):
			"""
			"""
			self.productConfigInfoDtoList = None





