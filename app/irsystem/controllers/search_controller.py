from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

from defs import *
import backend_algorithm_v1 as v1
import backend_algorithm_v2 as v2

from jinja2.ext import do


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
	unsplashed_queries = request.args.get('queries')
	max_distance = request.args.get('max_distance')

	if system_version == "v1":
		if not (location_query):
			location_query = ""
		if not (description_query):
			description_query = ""
		output_tupes = (location_query, description_query)
		results = v1.getPlaces(output_tupes[0] + " " + output_tupes[1])
		queries = []
		raw_country = ""
		for result in results:
			if(len(result[3]) > 0):
				raw_country = result[3][0][1]
				queries.append(raw_country)
			else:
				queries.append(None)
		return render_template('search.html', activity_query = activity_query,
			location_query = location_query,
			description_query= description_query,
			output_message = (output_tupes[0] == "" and output_tupes[1] == ""),
			max_distance = max_distance,
			results = results,
			map_geo = map_geo,
			version = system_version,
			unsplashed_queries = queries)
	elif system_version == "v2":
		# change this to the newer version of backend system
		if not (location_query):
			location_query = ""
		if not (description_query):
			description_query = ""
		output_tupes = (location_query, description_query)

		results = v2.getPlaces(output_tupes, max_distance)
		queries = []
		raw_country = ""
		for result in results:
			if(len(result[3]) > 0):
				raw_country = result[3][0][1]
				queries.append(raw_country)
			else:
				queries.append(None)
		return render_template('search.html', activity_query = activity_query,
			location_query = location_query,
			description_query= description_query,
			output_message = (output_tupes[0] == "" and output_tupes[1] == ""),
			max_distance = max_distance,
			results = results,
			map_geo = map_geo,
			version = system_version,
			unsplashed_queries = queries)
	elif system_version == "final":
		# change this to the final final version of backend system
		if not (location_query):
			location_query = ""
		if not (description_query):
			description_query = ""
		output_tupes = (location_query, description_query)

		results = v2.getPlaces(output_tupes, max_distance)
		queries = []
		raw_country = ""
		for result in results:
			if(len(result[3]) > 0):
				raw_country = result[3][0][1]
				queries.append(raw_country)
			else:
				queries.append(None)

		# setup display of what you searched for
		searched_query=[]
		if len(location_query) >0:
			searched_query.append(location_query)
		if len(description_query) >0:
			searched_query.append(description_query)

		searched_query = ', '.join(searched_query)

		if max_distance == '0':
			searched_distance= 'unrestricted distance'
		else:
			searched_distance= max_distance+' km'

		return render_template('search.html', activity_query = activity_query,
			location_query = location_query,
			description_query= description_query,
			output_message = (output_tupes[0] == "" and output_tupes[1] == ""),
			max_distance = max_distance,
			searched_query = searched_query,
			searched_distance = searched_distance,
			results = results,
			map_geo = map_geo,
			version = system_version,
			unsplashed_queries = queries)
	else:#this is the homepage render
		if not (location_query):
			location_query = ""
		if not (description_query):
			description_query = ""
		results = []
		queries = []
		raw_country = ""
		for result in results:
			if(len(result[3]) > 0):
				raw_country = result[3][0][1]
				queries.append(raw_country)
			else:
				queries.append(None)
		return render_template('search.html', activity_query = activity_query,
			location_query = location_query,
			description_query= description_query,
			output_message = True,
			max_distance = max_distance,
			results = results,
			map_geo = map_geo,
			version = system_version,
			unsplashed_queries = queries,
			autocomplete_data = "TESTTTTT!")



