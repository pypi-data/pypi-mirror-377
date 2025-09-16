from seven_jd.jd.api.base import RestApi

class CategoryReadFindByPIdRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.parentCid = None
			self.field = None

		def getapiname(self):
			return 'jingdong.category.read.findByPId'

			





