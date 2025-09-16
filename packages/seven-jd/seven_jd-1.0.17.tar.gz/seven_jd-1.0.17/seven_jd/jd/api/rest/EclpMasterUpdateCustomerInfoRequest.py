from seven_jd.jd.api.base import RestApi

class EclpMasterUpdateCustomerInfoRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.sellerNo = None
			self.deptNo = None
			self.customerNo = None
			self.customerName = None
			self.contacts = None
			self.phone = None
			self.customerEmail = None
			self.customerAddress = None
			self.customerType = None
			self.transitType = None
			self.warehouseName = None
			self.provinceName = None
			self.cityName = None
			self.countyName = None
			self.townName = None
			self.rection = None
			self.customerRemark = None
			self.licenseAddr = None
			self.licenseUnit = None
			self.licenseUnitNo = None
			self.warehouseNo = None
			self.sellerName = None
			self.medicineEnterpriseNature = None

		def getapiname(self):
			return 'jingdong.eclp.master.updateCustomerInfo'

			





