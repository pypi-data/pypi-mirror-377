from seven_jd.jd.api.base import RestApi

class EclpMasterInsertShopRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.isvShopNo = None
			self.spSourceNo = None
			self.deptNo = None
			self.spShopNo = None
			self.shopName = None
			self.contacts = None
			self.phone = None
			self.address = None
			self.email = None
			self.fax = None
			self.afterSaleContacts = None
			self.afterSaleAddress = None
			self.afterSalePhone = None
			self.bdOwnerNo = None
			self.reserve1 = None
			self.reserve2 = None
			self.reserve3 = None
			self.reserve4 = None
			self.reserve5 = None
			self.reserve6 = None
			self.reserve7 = None
			self.reserve8 = None
			self.reserve9 = None
			self.reserve10 = None
			self.outstoreRules = None

		def getapiname(self):
			return 'jingdong.eclp.master.insertShop'

			





