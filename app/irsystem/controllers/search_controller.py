from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "What's Next - A Travel Destination Recommendation System"
net_id = "Wanming Hu: wh298\n Smit Jain: scj39\n Judy Jiang: jj353\n Noah Kaplan: nk425\n Tatsuhiro Koshi: tk474\n"

@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('search')
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + query
		data = range(5)
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)



