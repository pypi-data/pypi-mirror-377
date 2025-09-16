from seven_jd.jd.api.base import RestApi

class MarketSmscardTemplateCreateRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.templateCreateVo = None

		def getapiname(self):
			return 'jingdong.market.smscard.template.create'

			
	

class TemplateOriginText(object):
		def __init__(self):
			"""
			"""
			self.originUrl = None
			self.sms = None


class Action(object):
		def __init__(self):
			"""
			"""
			self.fallbackUrl = None
			self.application = None
			self.origin = None
			self.name = None
			self.packageName = None
			self.type = None
			self.url = None


class Element(object):
		def __init__(self):
			"""
			"""
			self.cover = None
			self.level = None
			self.action = None
			self.source = None
			self.text = None
			self.type = None
			self.srcType = None
			self.content = None


class Content(object):
		def __init__(self):
			"""
			"""
			self.elements = None


class Style(object):
		def __init__(self):
			"""
			"""
			self.scale = None
			self.currency = None


class Body(object):
		def __init__(self):
			"""
			"""
			self.contents = None
			self.style = None


class TemplateContent(object):
		def __init__(self):
			"""
			"""
			self.templateType = None
			self.body = None


class TemplateCreateVo(object):
		def __init__(self):
			"""
			"""
			self.templateOriginText = None
			self.showTimes = None
			self.templateName = None
			self.templateContent = None





