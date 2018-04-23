from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

from defs import *
import backend_algorithm_v1 as v1
import backend_algorithm_v2 as v2


project_name = "Where Next - A Travel Destination Recommendation System"
net_id = "Wanming Hu: wh298, Smit Jain: scj39, Judy Jiang: jj353, Noah Kaplan: nk425, Tatsuhiro Koshi: tk474"


@irsystem.route('/', methods=['GET'])
def search():
	#query = request.args.get('search')
	output_message = ""
	activity_query = request.args.get('activity')
	location_query = request.args.get('location')
	description_query = request.args.get('description')
	system_version = request.args.get('version')

	if system_version == "v1":
		if not (location_query):
			location_query = ""
		if not (description_query):
			description_query = ""
		output_tupes = (location_query, description_query)	

		results = v1.getPlaces(output_tupes[0] + " " + output_tupes[1])	

		return render_template('search.html', activity_query = activity_query, 
			location_query = location_query, 
			description_query= description_query,
			output_message = (output_tupes[0] == "" and output_tupes[1] == ""), 
			results = results,
			map_geo = map_geo,
			version = system_version)
	elif system_version == "v2":
		# change this to the newer version of backend system
		if not (location_query):
			location_query = ""
		if not (description_query):
			description_query = ""
		output_tupes = (location_query, description_query)	

		results = v2.getPlaces(output_tupes)	

		return render_template('search.html', activity_query = activity_query, 
			location_query = location_query, 
			description_query= description_query,
			output_message = (output_tupes[0] == "" and output_tupes[1] == ""), 
			results = results,
			map_geo = map_geo,
			version = system_version)
	else:#this is the homepage render
		if not (location_query):
			location_query = ""
		if not (description_query):
			description_query = ""
		results = []
		return render_template('search.html', activity_query = activity_query, 
			location_query = location_query, 
			description_query= description_query,
			output_message = True, 
			results = results,
			map_geo = map_geo,
			version = system_version,
			autocomplete_data = "TESTTTTT!")

