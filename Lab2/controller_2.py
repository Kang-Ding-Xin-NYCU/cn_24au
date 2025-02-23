from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
import requests
from itertools import combinations

class PathController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(PathController, self).__init__(*args, **kwargs)
        self.api_url = 'http://127.0.0.1:5000/paths'

        self.hosts = ['h1','h2','h3','h4','h5','h6','h7','h8','h9']
        self.host_pairs = list(combinations(self.hosts , 2))
        self.paths_computed = False

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        if self.paths_computed:
            self.logger.info("Paths already computed")
            return
        self.logger.info("Switch connected. Requesting paths from API Server...")
        self.paths_computed = True
        for source , destination in self.host_pairs:
            self.logger.info("Processing host pair: %s -> %s" , source , destination)
            paths = self.request_paths_from_api(source , destination)

            if paths:
                path1 = paths.get('path1')
                path2 = paths.get('path2')

                self.logger.info("Path 1: %s", path1)
                self.logger.info("Path 2: %s", path2)

                self.deploy_paths(ev.msg.datapath, path1, 1)
                self.deploy_paths(ev.msg.datapath, path2, 2)

    def request_paths_from_api(self , source , destination):
        payload = {'source': source, 'destination': destination}
        try:
            response = requests.post(self.api_url, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error("Failed to get paths from API. Status code: %d", response.status_code)
                return None
        except Exception as e:
            self.logger.error("Error connecting to API Server: %s", str(e))
            return None

    def deploy_paths(self, datapath, path, group_id):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        for i in range(len(path) - 1):
            if path[i].startswith('h') or path[i + 1].startswith('h'):
                continue
            in_port = int(path[i].replace('s', ''))
            out_port = int(path[i + 1].replace('s', ''))

            match = parser.OFPMatch(in_port=in_port)
            actions = [parser.OFPActionOutput(out_port)]
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

            mod = parser.OFPFlowMod(
                datapath=datapath,
                priority=100,
                match=match,
                instructions=inst
            )
            
            datapath.send_msg(mod)
