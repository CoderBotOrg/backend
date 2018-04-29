"""
One listener is subscribed to a topic called 'rootTopic'.
One 'rootTopic' message gets sent. 
"""

from pubsub import pub


# ------------ create a listener ------------------

def listener1(pippo):
    print('Function listener1 received:')
    print('  pippo =', pippo)


# ------------ register listener ------------------

pub.subscribe(listener1, 'rootTopic')

# ---------------- send a message ------------------

print('Publish something via pubsub')
pippo = dict(a=456, b='abc')
pub.sendMessage('rootTopic', pippo=pippo)
