from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.cli import CLI

if '__main__' == __name__:
    net = Mininet(controller=RemoteController)
    ryu = net.addController('ryu', controller=RemoteController, ip='127.0.0.1', port=6633)
    
    #Add PC
    # Add PC
    A = net.addHost('A', ip='10.0.0.1', mac='00:00:00:00:00:01')
    B = net.addHost('B', ip='10.0.0.2', mac='00:00:00:00:00:02')
    C = net.addHost('C', ip='10.0.0.3', mac='00:00:00:00:00:03')
    D = net.addHost('D', ip='10.0.0.4', mac='00:00:00:00:00:04')

    #Add switches
    S1 = net.addSwitch('S1')
    S2 = net.addSwitch('S2')
    S3 = net.addSwitch('S3')

    #Add links
    net.addLink(A,  S3, port2=1)
    net.addLink(B,  S1, port2=3)
    net.addLink(C,  S2, port2=3)
    net.addLink(D,  S2, port2=2)
    net.addLink(S1, S2, port1=2, port2=4)
    net.addLink(S1, S3, port1=1, port2=3)
    net.addLink(S2, S3, port1=1, port2=2)
    
    net.build()
    ryu.start()

    S1.start([ryu])
    S2.start([ryu])
    S3.start([ryu])

    CLI(net)

    net.stop()
