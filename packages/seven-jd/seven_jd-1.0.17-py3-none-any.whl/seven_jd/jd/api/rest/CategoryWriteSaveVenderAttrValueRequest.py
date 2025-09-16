from seven_jd.jd.api.base import RestApi

class CategoryWriteSaveVenderAttrValueRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.valueId = None
			self.attValue = None
			self.attributeId = None
			self.categoryId = None
			self.indexId = None
			self.key = None
			self.value = None

		def getapiname(self):
			return 'jingdong.category.write.saveVenderAttrValue'

			





