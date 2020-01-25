import logging

from pyats import aetest
from genie.testbed import load

logger = logging.getLogger(__name__)

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def connect_to_tb_devices(self, testbed):

        self.parent.parameters['testbed'] = testbed = load(testbed)

        uut = testbed.devices['uut']

        uut.connect()

        logger.info('We have made connectivity to device %s' % uut.name)

class Test_BGP(aetest.Testcase):

    @aetest.setup
    def setup(self, testbed):
        self.bgp = testbed.devices['uut'].learn('bgp')

    @aetest.test
    def test_bgp_has_neighbors(self):
        nbr_info = []
        for bgp_instance in self.bgp.routes_per_peer['instance']:
            for vrf in self.bgp.routes_per_peer['instance'][bgp_instance]['vrf']:
                for nbr in self.bgp.routes_per_peer['instance'][bgp_instance]['vrf'][vrf]['neighbor']:
                    nbr_info.append((bgp_instance, vrf, nbr))

        if not nbr_info:
            self.failed('BGP neighbors are missing!')
        else:
            self.passed('We have %s neigbors' % len(nbr_info), 
                        data = {'neighbors': nbr_info})
  
if __name__ == "__main__":
    # if this script is run stand-alone
    import os
    from genie.testbed import load

    HERE = os.path.dirname(__file__)

    aetest.main(testbed = load(os.path.join(HERE, '..', 'files', 'workshop-testbed.yaml')))