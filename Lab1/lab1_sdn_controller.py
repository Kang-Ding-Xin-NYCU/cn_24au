from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp, ipv4, tcp

class Lab1Controller(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Lab1Controller, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        self.install_default_flows(datapath)

    def install_default_flows(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

    # 1. ARP 規則
        match = parser.OFPMatch(eth_type=0x0806)  # ARP
        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        self.add_flow(datapath, 3, match, actions)


    # 2. ICMP 規則
        match = parser.OFPMatch(eth_type=0x0800, ip_proto=1)  # IPv4 + ICMP
        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        self.add_flow(datapath, 3, match, actions)


    # 3. A, B, C 自由通信
        for src, dst in [('10.0.0.1', '10.0.0.2'), ('10.0.0.2', '10.0.0.1')]:
            match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src, ipv4_dst=dst)  # IPv4
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            self.add_flow(datapath, 1, match, actions)
            self.logger.info(f"Installing flow: Allow {src} to {dst}")

        for src, dst in [('10.0.0.1', '10.0.0.3'), ('10.0.0.3', '10.0.0.1')]:
            match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src, ipv4_dst=dst)  # IPv4
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            self.add_flow(datapath, 1, match, actions)
            self.logger.info(f"Installing flow: Allow {src} to {dst}")

        for src, dst in [('10.0.0.2', '10.0.0.3'), ('10.0.0.3', '10.0.0.2')]:
            match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src, ipv4_dst=dst)  # IPv4
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            self.add_flow(datapath, 1, match, actions)
            self.logger.info(f"Installing flow: Allow {src} to {dst}")


    # 5. D 訪問 A, B 的特定埠
        for src, dst, port in [('10.0.0.4', '10.0.0.1', 22), ('10.0.0.4', '10.0.0.1', 80)]:
            match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src, ipv4_dst=dst, ip_proto=6, tcp_dst=port)
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            self.add_flow(datapath, 2, match, actions)
            self.logger.info(f"Installing flow: Allow {src} to {dst} port {port}")

        for src, dst, port in [('10.0.0.4', '10.0.0.2', 22), ('10.0.0.4', '10.0.0.2', 80)]:
            match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src, ipv4_dst=dst, ip_proto=6, tcp_dst=port)
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            self.add_flow(datapath, 2, match, actions)
            self.logger.info(f"Installing flow: Allow {src} to {dst} port {port}")


    # 6. 禁止 D 和 C 之間的通信
        match = parser.OFPMatch(eth_type=0x0800, ipv4_src='10.0.0.1', ipv4_dst='10.0.0.4')
        self.add_flow(datapath, 4, match, [])  # Drop
        match = parser.OFPMatch(eth_type=0x0800, ipv4_src='10.0.0.2', ipv4_dst='10.0.0.4')
        self.add_flow(datapath, 4, match, [])  # Drop
        match = parser.OFPMatch(eth_type=0x0800, ipv4_src='10.0.0.4', ipv4_dst='10.0.0.3')
        self.add_flow(datapath, 4, match, [])  # Drop
        match = parser.OFPMatch(eth_type=0x0800, ipv4_src='10.0.0.3', ipv4_dst='10.0.0.4')
        self.add_flow(datapath, 4, match, [])  # Drop


    # 7. 未匹配的 IPv4 規則
        match = parser.OFPMatch(eth_type=0x0800)  # IPv4
        actions = []
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)

