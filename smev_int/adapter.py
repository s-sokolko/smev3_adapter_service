import uuid
from zeep import Client, Settings, xsd


class Message:
    def __init__(self, adapter, content):
        self.factory = adapter.factory
        self.test_mode = adapter.test_mode
        self.content = content

    def build(self):
        factory = self.factory
        val = xsd.AnyObject(self.content._xsd_elm, self.content)
        data = factory.RequestContentType(
            content=factory.Content(
                MessagePrimaryContent=val
            )
        )
        meta = factory.RequestMetadataType(
            clientId=str(uuid.uuid4()),
            createGroupIdentity=factory.CreateGroupIdentity(
                FRGUServiceCode='00000000000000000000',
                FRGUServiceDescription='00000000000000000000',
                FRGUServiceRecipientDescription='00000000000000000000'
            ),
            testMessage=self.test_mode
        )
        msg = factory.RequestMessageType(
            RequestMetadata=meta,
            RequestContent=data
        )
        return msg


class Adapter:
    def __init__(self, url, mnemonic, test_mode=False):
        self.test_mode = test_mode
        self.mnemonic = mnemonic
        settings = Settings(strict=False)
        self.client = Client(url, settings=settings)
        self.factory = self.client.type_factory('urn://x-artefacts-smev-gov-ru/services/service-adapter/types')

    def send(self, content):
        msg = Message(self, content)
        r = self.client.service.Send(self.mnemonic, msg.build())
        return r.MessageId

    def get_response(self):
        result = self.client.service.Get(self.mnemonic, None, self.factory.QueryTypeCriteria('RESPONSE'))
        if not result.smevMetadata:
            return
        success = False if 'status' in result.Message and result.Message.status == 'ERROR' else True
        response = {
            'reference_id': result.smevMetadata.OriginalMessageID,
            'success': success,
            'data': result.Message.ResponseContent.content.MessagePrimaryContent._value_1 if success else result.Message.fault
        }
        return response