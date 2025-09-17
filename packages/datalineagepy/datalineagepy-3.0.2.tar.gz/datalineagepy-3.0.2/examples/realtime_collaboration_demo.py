"""
Real-Time Collaboration Demo for DataLineagePy
Demonstrates starting a collaboration server and connecting a client.
"""
import sys
import threading
from datalineagepy.collaboration.realtime_collaboration import CollaborationServer, CollaborationClient

if len(sys.argv) > 1 and sys.argv[1] == "server":
    # Start the collaboration server
    CollaborationServer().run()
else:
    # Start a client and print state updates
    CollaborationClient().run()
