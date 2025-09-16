from seven_jd.jd.api.base import RestApi

class EclpMasterAddSupplierRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.isvSupplierNo = None
			self.supplierName = None
			self.contacts = None
			self.phone = None
			self.fax = None
			self.email = None
			self.province = None
			self.city = None
			self.county = None
			self.town = None
			self.address = None
			self.ext1 = None
			self.ext2 = None
			self.ext3 = None
			self.ext4 = None
			self.ext5 = None
			self.pictureUrls = None
			self.medicineEnterpriseNature = None

		def getapiname(self):
			return 'jingdong.eclp.master.addSupplier'

			





