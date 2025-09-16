from seven_jd.jd.api.base import RestApi

class EclpMasterInsertSellerCategoryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.categoryName = None
			self.previousCategoryNo = None

		def getapiname(self):
			return 'jingdong.eclp.master.insertSellerCategory'

			





