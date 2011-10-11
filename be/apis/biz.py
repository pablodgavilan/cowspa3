import datetime
import be.repository.access as dbaccess

biz_store = dbaccess.biz_store
bizplace_store = dbaccess.bizplace_store

class BizCollection:

    def new(self, name, address, city, country, email, short_description=None, long_description=None, tags=None, website=None, blog=None, twitter=None, facebook=None, linkedin=None, phone=None, fax=None, sip=None, skype=None, mobile=None):
        created = datetime.datetime.now()
        biz_id = dbaccess.OidGenerator.next("Biz")
        data = dict(id=biz_id, name=name, created=created, short_description=short_description, long_description=long_description, tags=tags, website=website, blog=blog, twitter=twitter, facebook=facebook, address=address, city=city, country=country, email=email, phone=phone, fax=fax, sip=sip, skype=skype, mobile=mobile)
        biz_store.add(**data)

        return biz_id

    def list(self, ):
        """
        returns list of bizplace info dicts
        """
        
    def search(self, q, limit=5):
        return dbaccess.search_biz(q,limit)

class BizResource:

    def info(self, biz_id):
        """
        returns dict containing essential information of specified business
        """
        return dbaccess.biz_info(biz_id)

    def update(self, biz_id, mod_data):
        """
        """

    def bizplaces(self, biz_id):
        """
        """

biz_resource = BizResource()
biz_collection = BizCollection()
