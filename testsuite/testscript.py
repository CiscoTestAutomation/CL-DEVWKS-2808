import logging

from pyats import aetest
from genie.testbed import load

logger = logging.getLogger(__name__)

class CommonSetup(aetest.CommonSetup):
    'common setup section always runs first within the script'

    @aetest.subsection
    def connect_to_tb_devices(self, testbed):
        # convert a pyATS testbed to Genie testbed
        # genie testbed extends pyATS testbed and does more with it, eg, 
        # adding .learn() and .parse() functionality
        # this step will be harmonized and no longer required in near future
        self.parent.parameters['testbed'] = testbed = load(testbed)

        # connect to device
        uut = testbed.devices['uut']
        uut.connect()

        logger.info('We have made connectivity to device %s' % uut.name)

class Test_BGP(aetest.Testcase):

    @aetest.setup
    def setup(self, testbed):
        # do our learning
        self.bgp = testbed.devices['uut'].learn('bgp')

    @aetest.test
    def test_bgp_has_neighbors(self):
        # compute our neighbors
        nbr_info = []
        for bgp_instance in self.bgp.routes_per_peer['instance']:
            for vrf in self.bgp.routes_per_peer['instance'][bgp_instance]['vrf']:
                for nbr in self.bgp.routes_per_peer['instance'][bgp_instance]['vrf'][vrf]['neighbor']:
                    nbr_info.append((bgp_instance, vrf, nbr))

        # decide whether this testcase is pass or fail
        if not nbr_info:
            self.failed('BGP neighbors are missing!')
        else:
            # on pass - save the neighbor data for future analysis
            # in the final report
            self.passed('We have %s neigbors' % len(nbr_info), 
                        data = {'neighbors': nbr_info})
  
if __name__ == "__main__":
    # if this script is run stand-alone
    import os
    from genie.testbed import load

    HERE = os.path.dirname(__file__)

    aetest.main(testbed = load(os.path.join(HERE, '..', 'files', 'workshop-testbed.yaml')))