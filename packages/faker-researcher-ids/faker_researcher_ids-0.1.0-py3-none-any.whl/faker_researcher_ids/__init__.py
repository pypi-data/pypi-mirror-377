from datetime import datetime
from faker.providers import BaseProvider
import string

class ScientificProvider(BaseProvider):
    @staticmethod
    def _orcid_checksum(digits: str) -> str:
        '''The algorithm was taken from https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier#2-checksum'''
        total = 0
        for digit in digits:
            total = (total + int(digit)) * 2
        result = (12 - (total % 11)) % 11
        return 'X' if result == 10 else str(result)

    def scopus_id(self) -> str:
        '''ScopusID is an unique 11-digit string'''
        return self.numerify('#' * 11)
    
    def orcid(self) -> str:
        '''Typically, ORCID identifiers are assigned between 0000-0001-5000-0007 and 0000-0003-5000-0001,
        or between 0009-0000-0000-0000 and 0009-0010-0000-0000, where last digit is a checksum.
        Source: https://webofscience.zendesk.com/hc/en-us/articles/26916258216209-Web-of-Science-Core-Collection-Search-Fields'''
        chance = self.random_int(min=0, max=5)
        lower_bound, upper_bound = (int(9000e+8), int(9001e+8)) if chance > 0 else (int(15e+6), int(35e+6))
        num = self.random_int(min=lower_bound, max=upper_bound)
        checksum = self._orcid_checksum(str(num))
        str_num = f'{num:012d}{checksum}'
        return f'https://orcid.org/000{str_num[0]}-{str_num[1:5]}-{str_num[5:9]}-{str_num[9:]}'
    
    def wos_id(self) -> str:
        '''ResearcherID structure: X-DDDD-YYYY (approx. before 2022) or XXX-DDDD-YYYY (since 2022), where
        X - letter (uppercase), D - digit, YYYY - year of issue'''
        year = self.random_int(2008, datetime.now().year)
        result = self.bothify('???-####-', letters=string.ascii_uppercase) + str(year)
        return result if year >= 2022 else result[2:]
        
    def google_scholar_id(self) -> str:
        '''Google Scholar ID is an unique string (typically, 12-symbol)
        that contains latin letters (uppercase and lowercase) and digits'''
        return self.lexify('?' * 12, letters=string.ascii_letters + string.digits)