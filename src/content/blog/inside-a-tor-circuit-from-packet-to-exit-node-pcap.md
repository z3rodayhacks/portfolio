---
title: 'Inside a TOR Circuit: From Packet to Exit Node (PCAP-Level Analysis p-1)'
description: "In the previous article we talked about how dark web is not scary ,\
  \ basically explaining about how it works and what might you find in there but now\
  \ lets touch up on the technical part of how the data packet suffers to travel around\
  \ in the onion protocol.\n\nso , What actually happens when you open TOR Browser\
  \ ?\n\nwhen your computer has TOR Browser open , it stops acting like a typical\
  \ web browser and starts functioning as an Onion Proxy . It immediately establishes\
  \ a secure , encrypted tunnel through the TOR network.\n\nBefore we get a bit deeper\
  \ lets fresh up in a few words I might be Using in near future ,\n\nDNS Resolution:\n\
  \nIn a normal browser , your PC asks your ISP’s server “ Yo whats the ip for google.com?”\
  \ before connecting. but in TOR , this is handled via Remote Resolution\n\n    The\
  \ Process : Your Browser sends the domain name inside the encrypted TOR circuit.\
  \ The request travels through the Entry and Middle nodes as encrypted data\n   \
  \ The Exit : Only the Exit Node performs the actual DNS lookup\n    Why ? : This\
  \ prevents “DNS Leaks” , Where an ISP could see which sites you are visiting even\
  \ if the content itself is encrypted.\n\nPress enter or click to view image in full\
  \ size\nThis Image shows TOR forwards DNS requests through the SOCKS proxy so the\
  \ Exit Node performs resolution remotely.\n\nBootstrap Process:\n\nThis is the “startup”\
  \ sequence where the client ,\n\nInitialization : TOR first checks a small built-in\
  \ list of trusted relays called fallback directories , You can think of it like\
  \ “Okay … who do i contact first”\n\nConnection: Tor connects to one of these relays\
  \ and downloads the Consensus , a big list containing all the active TOR relays\
  \ currently online . Basically , which relays are active , which ones are fast ,\
  \ which ones can be trusted . Kind of like downloading the map before going on a\
  \ journey\n\nCompletion: Once TOR gets the relay list nad verifies the certificates\
  \ , the Bootstrap reaches 100% , Now TOR has enough information to start building\
  \ circuits and routing your traffic through the network\n\nTo See this in working\
  \ :\n\nOpen Terminal in any linux env(I use arch so ill be using arch native commands)\n\
  Press enter or click to view image in full size\nsudo pacman -S tor\nPress enter\
  \ or click to view image in full size\nTor Bootstrapping in real life (connecting\
  \ to relays , downloading network info , and building encrypted circuits before\
  \ entering the network )\n\nDirectory Authorities\n\nDirectory Authorities are the\
  \ trusted servers that help keep the Tor network organized . They collect information\
  \ about all the active relays in the network and create something called the consensus\
  \ [official list of relays TOR clients use]\n\nThey check :\n\n    which relays\
  \ are online\n    which ones are stable\n    which ones can be trusted\n\nOnce multiple\
  \ authorities agree , they publish the updated network consensus . TOR clients download\
  \ this during the bootstrap process before building circuits.\nCircuit Construction\
  \ : How TOR Builds a Path\n\nOnce the client downloads the consensus , TOR does\
  \ not randomly pick relays .\n\nIt carefully selects :\n\n    1ENTRY {Guard} Node\n\
  \    1MIDDLE Rlay\n    1Exit Node\n\nThe path is usually kept alive for around 10\
  \ minutes before rotating\n\nThe TOR client then performs a series of cryptographic\
  \ handshakes to establish encrypted session keys with every relay in the path.\n\
  \nBut the important part is :\n\nEach relay only knows the node before it and the\
  \ node after it.\n\nThe Entry node knows your IP but not the final destination.\n\
  The Exit node knows the destination but not your real IP.\nThe Middle relay only\
  \ forwards encrypted cells without knowing either side.\n\nThis separation is what\
  \ gives TOR its anonymity model.\nTOR Cells : The Real Packet Format\n\nTOR does\
  \ not forward raw TCP packets internally.\n\nInstead , it breaks data into fixed-size\
  \ structures called Cells.\n\nEach TOR cell is normally : 512 Bytes\n\nWhy fixed\
  \ size ?\n\nBecause variable packet sizes can leak information through traffic fingerprinting.\n\
  \nA TOR Cell contains :\n\n    Circuit ID : Identifies the circuit\n    Command:\
  \ Relay/Destroy/Create\n    Payload: Encrypted data\n\nTypes of TOR cells include\
  \ :\n\n    CREATE\n    CREATED\n    RELAY\n    DESTROY\n    PADDING\n\nFrom a PCAP\
  \ perspective , most TOR traffic appears as TLS encrypted TCP streams carrying these\
  \ cells.\nTLS Layer : What You Actually See In PCAP\n\nOne important thing beginners\
  \ misunderstand : You usually cannot directly see TOR cells in Wireshark unless\
  \ TOR traffic is decrypted\n\nSO, you can ask .. gli4ch what will you able to see\
  \ ??\n\nwe can see : TCP-> TLS->Encrypted Tor Data\n\nIn Wireshark , TOR traffic\
  \ commonly appears as :\n\n    TLS Client Hello\n    TLS Application Data\n    Encrypted\
  \ TCP streams\n\nHistorically TOR used TLS heavily to blend in with normal HTTPS\
  \ traffic.\n\nModern TOR versions may also use different pluggable transports like\
  \ :\n\n    obfs4\n    meek\n    snowflake\n\nto evade censorship and DPI systems.\n\
  Press enter or click to view image in full size\n\nNotice how after the TLS handshake\
  \ :\n\n    Application Data\n    -Application Data\n    -Application Data\n\nstarts\
  \ repeating continuously.\n\nThis is the encrypted TOR payload moving through the\
  \ circuit.\n\nWireshark cannot directly decode the TOR cells because they are encapsulated\
  \ inside TLS encryption\n\nSO, whats the use in this ??\n\n    Packet timings\n\
  \    Packet size patterns\n    Relay IPs\n    TLS fingerprints\n    Connection Persistence\n\
  \nrather than plaintext content these prove to be useful in many other ways\nPress\
  \ enter or click to view image in full size\nTCP Stream\n\nThis is the output you\
  \ get when You follow a Tor TCP Stream\n\nAfter identifying TOR traffic in wireshark\
  \ , we can right click a packet and select to Follow -> TCP Stream\n\nAt first ,\
  \ You might expect to see readable website requests or messages\n\ninstead , what\
  \ appears is something like this\n\nwhich mostly looks like a random garbage . but\
  \ this “garbage” is actually encrypted TOR traffic encapsulated inside TLS .\nConversation\
  \ Statistics\nPress enter or click to view image in full size\nConversations\n\n\
  Wireshark does not only allow us to inspect packets individually .\n\nIt also allows\
  \ us to analyze the entire communication session as a single conversation\n\nUsing:\n\
  \n    Statistics -> conversation\n\nWe can observe how TOR client communicates with\
  \ a relay over time.\n\nThe screenshot above shows an active TOR conversation between\
  \ the local machine and a TOR relay operating on port 9001\n\nso, what makes this\
  \ interesting ?\n\nUnlike normal web browsing where connections are often short-lived\
  \ :\n\n    Open Website → Load Content → Disconnect\n\nTOR usually maintains persistent\
  \ encrypted tunnels.\n\nIn this capture :\n\n    the TCP session stays active\n\
  \    encrypted data continuously flows both ways\n    the relay remains connected\
  \ for an extended duration\n\nThis is typical TOR circuit behavior.\n\nSymmetrical\
  \ Traffic Patterns\n\nNotice how both sides exchange relatively balanced amounts\
  \ of data :\n\n    Bytes A → B\n    Bytes B → A\n\nThis occurs because TOR circuits\
  \ constantly exchange encrypted relay cells in both directions.\n\nEven when the\
  \ user is idle :\n\n    keepalive traffic\n    circuit management\n    relay communication\n\
  \nmay continue flowing through the tunnel.\n\nwhy this matters ??\n\nEven though\
  \ the payload remains encrypted , conversation statistics still reveal important\
  \ metadata.\n\nAnalysts can use this to identify :\n\n    long-lived encrypted tunnels\n\
  \    suspected TOR relay communication\n    unusual persistent sessions\n    bandwidth\
  \ usage patterns\n    traffic correlation opportunities\n\nThis is one of the reasons\
  \ why metadata analysis is extremely powerful in modern network forensics.\nVisualizing\
  \ TOR Traffic Behavior\nPress enter or click to view image in full size\nI/O Graph\n\
  \nWireshark also allows us to study traffic patterns visually using :\n\n    Statistics\
  \ → IO Graphs\n\nInstead of analyzing packets one-by-one , IO Graphs show how network\
  \ activity changes over time.\n\nThe graph below represents TOR-related traffic\
  \ activity captured during a live session.\n\nThe X-axis represents :Time (seconds)\n\
  \nThe Y-axis represents :Packets per second\n\nThe black line shows the total packet\
  \ activity across the capture.\n\nAdditional overlays display :\n\n    filtered\
  \ TOR-related packets\n    TCP anomalies/errors\n    stream-specific behavior\n\n\
  What Does This Reveal ?\n\nAt first glance the traffic may look random.\n\nBut several\
  \ interesting patterns appear :\n\nBurst-Based Communication:\n\nNotice the repeated\
  \ spikes in traffic volume :\n\n↑ Packet Burst\n↓ Relative Silence\n↑ Another Burst\n\
  \nTOR traffic often behaves in bursts because data is transmitted through encrypted\
  \ relay cells and multiplexed streams.\n\nActivities like :\n\n    opening websites\n\
  \    loading images\n    switching tabs\n    downloading content\n\ncan generate\
  \ sudden spikes in encrypted traffic.\n\nPersistent Tunnel Behavior:\n\nUnlike normal\
  \ short-lived browsing sessions :\n\nTOR maintains continuous encrypted communication\
  \ with relays.\n\nEven during moments where the user appears inactive , background\
  \ TOR activity may still continue :\n\n    circuit maintenance\n    keepalive packets\n\
  \    relay synchronization\n    stream management\n\nThis creates the long-lived\
  \ stable traffic patterns visible in the graph.\nConclusion\n\nAt first glance ,\
  \ TOR traffic inside Wireshark may just look like meaningless encrypted noise :\n\
  \n    TLS Streams\n    Application Data\n    Random Binary Blobs\n    Persistent\
  \ TCP Sessions\n\nBut once we begin analyzing the traffic behavior itself , a much\
  \ deeper picture starts to appear.\n\nThrough PCAP analysis we can observe :\n\n\
  \    how TOR bootstraps into the network\n    how encrypted circuits are constructed\n\
  \    how relay communication behaves\n    how TLS tunnels encapsulate TOR cells\n\
  \    how traffic flows persist over time\n    and how metadata still leaks behavioral\
  \ patterns even when the payload remains encrypted\n\nOne of the most important\
  \ realizations in network forensics is this :\n\n    Encryption hides content.\n\
  \    It does not completely hide behavior.\n\nEven though Wireshark cannot directly\
  \ decrypt TOR circuits , analysts can still study :\n\n    timing patterns\n   \
  \ relay IPs\n    packet bursts\n    TLS fingerprints\n    stream persistence\n \
  \   traffic symmetry\n\nto build probabilistic understanding about what is happening\
  \ inside the network.\n\nAt the same time , this also demonstrates why TOR remains\
  \ one of the most sophisticated anonymity systems ever built.\n\nThe layered relay\
  \ architecture ensures that no single node can fully identify both :\n\n    who\
  \ the user is\n    and where the traffic is going\n\nwhich is the fundamental principle\
  \ behind onion routing itself.\n\nBut TOR is not magic invisibility.\n\nModern analysis\
  \ techniques increasingly focus on :\n\n    - metadata correlation\n    - traffic\
  \ fingerprinting\n    - behavioral analysis\n    - timing attacks\n\nrather than\
  \ attempting to directly break encryption.\n\nAnd this is exactly where modern TOR\
  \ research becomes truly fascinating.\n\nIn the next article we will move even deeper\
  \ into the internals of the TOR ecosystem exploring topics like :\n\n    TOR cell\
  \ architecture\n    JA3/TLS fingerprinting\n    Traffic correlation attacks\n  \
  \  Hidden services\n    Guard node attacks\n    Pluggable transports\n    and how\
  \ modern forensic systems attempt to identify TOR traffic without decrypting it.\n\
  \nBecause in modern cybersecurity :\n\n    sometimes the metadata tells the entire\
  \ story.\n\nyours truly\n\ngli4ch"
date: '2026-05-22'
thumbnail: /images/blog/screenshot_tutorial_wireshark_oui_console-f_mobile.jpg
tags:
- wireshark
- tor
- cybersecurity
featured: true
draft: false
---

Read the full article on Medium:

[Inside a TOR Circuit: From Packet to Exit Node (PCAP-Level Analysis p-1)](https://medium.com/@rkjashwanthraghav01/inside-a-tor-circuit-from-packet-to-exit-node-pcap-level-analysis-p-1-0d07d0e4cdc5)
