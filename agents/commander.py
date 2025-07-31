from core.crypto import MilitaryCrypto
from core.utils import ooda_cycle
import schedule

class ProjectCommander:
    def __init__(self, crypto_system):
        self.crypto = crypto_system
        self.campaigns = {}
        
    def launch_campaign(self, campaign):
        campaign_id = self._generate_id(campaign)
        self.campaigns[campaign_id] = campaign
        ooda_cycle(campaign)
        return campaign_id
        
    def _generate_id(self, campaign):
        return self.crypto.hash_data(campaign['product'] + campaign['target_demo'])
