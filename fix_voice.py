# Created by Jeff Hollaway
import re
with open('tests/test_system.py','r') as f:
    t = f.read()
t = t.replace('source="voice_trigger"', 'source=ClipSource.VOICE_TRIGGER')
if 'from modules.models import ClipSource' not in t:
    t = 'from modules.models import ClipSource\n' + t
with open('tests/test_system.py','w') as f:
    f.write(t)
print('voice trigger fix applied')
