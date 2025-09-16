from seven_jd.jd.api.base import RestApi

class EclpCategoryGetSecondLevelCategoriesRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.firstCategoryNo = None
			self.secondCategoryNo = None

		def getapiname(self):
			return 'jingdong.eclp.category.getSecondLevelCategories'

			





