import os
import requests
import sys

d = os.path.dirname(os.path.abspath(__file__))
darr = d.split('/')[-3:]
darr.remove('public_html')
root_url = 'https://people.cs.uct.ac.za/~' + '/'.join(darr)
os.chmod(os.path.join(d, 'bot.py'), 0o755)
os.chmod(os.path.join(d, 'template_battleground.txt'), 0o755)
print('Attempting to add bot at \n\t{}\nto network at\n\t{}'.format(root_url, sys.argv[1]))
r = requests.post(sys.argv[1], json={'root': root_url})
if r.ok:
    print('Done\nGo to https://people.cs.uct.ac.za/~KNXBOY001/gm/ to see the current battle')
else:
    print('Error\nError posting to network. Status code=' + str(r.status_code))
