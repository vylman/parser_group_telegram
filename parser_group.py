import time
from string import ascii_lowercase, digits
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.tl.types import ChannelParticipantsSearch


class ParserTelegram(object):

    def __init__(self, *, phone, api_id, api_hash, group_name, outputFile=None):
        self.client = TelegramClient(phone, api_id, api_hash)
        self.group_name = group_name
        self.outputFile = outputFile if outputFile is not None else 'output.txt'
        self.__participants = []
        self.__abc = list(ascii_lowercase  + digits + 'йцукенгшщзхъфывапролджэячсмитьбю')
        self.client.connect()
        if not self.client.is_user_authorized():
            self.client.send_code_request(phone)
            self.client.sign_in(phone, input('Enter code:'))

    def __set_array(self):
        self.__participants = list(set(self.__participants))

    @property
    def participants(self):
        self.__set_array()
        return self.__participants

    def __parse_admins(self):

        for n, user in enumerate(self.client.iter_participants(self.group_name, filter=ChannelParticipantsAdmins), 1):
            self.append(f'{user.id};{user.first_name};{user.last_name};{user.username};admin')

    def __parse_users_by_character(self, *, character: str = 'a') -> bool:
        offset = 0

        while True:
            participants = self.client(GetParticipantsRequest(channel=self.group_name,
                                                              filter=ChannelParticipantsSearch(character),
                                                              offset=offset, limit=200, hash=0))
            if not participants.users:
                return True
            for user in participants.users:
                status = 'user'
                try:
                    if user.deleted is True or user.first_name == "Deleted" and user.last_name == "Account":
                        continue
                    if user.bot is True:
                        status = 'bot'
                    self.__participants.append(f'{user.id};{user.first_name};{user.last_name};{user.username};{status}')

                # TODO: save to file if crash
                except Exception as ex:
                    print(ex)
                    pass
            offset += len(participants.users)


    def parse_group(self):
        for key in self.__abc:
            self.__parse_users_by_character(character=key)
            self.__set_array()
            time.sleep(5)
        self.__parse_admins()
        with open(self.outputFile,'w') as file:
            file.writelines(self.participants)


fetcher = ParserTelegram(api_id='api_id', api_hash='api_hash', phone='phone', group_name='group_name')
fetcher.parse_group()
