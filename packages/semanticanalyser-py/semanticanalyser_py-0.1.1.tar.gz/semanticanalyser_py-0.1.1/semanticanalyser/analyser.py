import requests
import json

class Matchtype:
  def __init__(self, type):
    self.type = type

  def get_type(self):
    return self.type

  def set_type(self, type):
    self.type =   type


class MatchProperty:
  def __init__(self, property):
    self.property = property

  def get_property(self):
    return self.property

  def set_property(self, property):
    self.property = property

class Match:
    def __init__(self, matching_term, match_property, match_type, term_code, vocabulary, concept_uri):
        self._matching_term = matching_term
        self._match_property = match_property
        self._match_type = match_type
        self._term_code = term_code
        self._vocabulary = vocabulary
        self._concept_uri = concept_uri

    def getMatchingTerm(self):
        return self._matching_term

    def getMatchProperty(self):
        return self._match_property

    def getMatchType(self):
        return self._match_type

    def getTermCode(self):
        return self._term_code

    def getVocabulary(self):
        return self._vocabulary

    def getConceptURI(self):
        return self._concept_uri


class Vocabularies:
  def __init__(self, id, type, about, name):
    self.id = id
    self.type = type
    self.about = about
    self.name = name

  def __str__(self):
    return f"ID: {self.id}, Type: {self.type}, About: {self.about}, Name: {self.name}"



class SemanticAnalyzer:
  def __init__(self, endpoint="https://semantics.bodc.ac.uk/api"):
    self.endpoint = endpoint

  def get_categories(self):
    try:
      response = requests.get(f"{self.endpoint}/categories")
      response.raise_for_status()
      categories_data = response.json()
      categories_list = []
      if '@graph' in categories_data:
          for graph_item in categories_data['@graph']:
              if 'result' in graph_item:
                  for result_item in graph_item['result']:
                      category = {
                          'name': result_item.get('name', 'N/A'),
                          'termCode': result_item.get('termCode', 'N/A')
                      }
                      categories_list.append(category)
          return categories_list
      else:
          print("Unexpected response structure for categories.")
          return None
    except requests.exceptions.RequestException as e:
      print(f"Error fetching categories: {e}")
      return None

  def get_vocabularies(self, category):
    try:
      response = requests.get(f"{self.endpoint}/categories/{category}/vocabularies")
      response.raise_for_status()
      vocabularies_data = response.json()
      vocabularies_list = []
      if '@graph' in vocabularies_data:
          for graph_item in vocabularies_data['@graph']:
              if 'result' in graph_item:
                  for result_item in graph_item['result']:
                      vocabulary = Vocabularies(
                          id=result_item.get('@id', 'N/A'),
                          type=result_item.get('@type', 'N/A'),
                          about=result_item.get('about', 'N/A'),
                          name=result_item.get('name', 'N/A'))
                      vocabularies_list.append(vocabulary)
          return vocabularies_list
      else:
          print("Unexpected response structure for vocabularies.")
          return None
    except requests.exceptions.RequestException as e:
      print(f"Error fetching vocabularies: {e}")
      return None


  def getMatchTypes(self):
    try:
      response = requests.get(f"{self.endpoint}/matchType")
      response.raise_for_status()
      match_types_data = response.json()
      if 'itemListElement' in match_types_data:
          return [Matchtype(item) for item in match_types_data['itemListElement']]
      else:
          print("Unexpected response structure for match types.")
          return None
    except requests.exceptions.RequestException as e:
      print(f"Error fetching match types: {e}")
      return None

  def getMatchProperties(self):
    try:
      response = requests.get(f"{self.endpoint}/matchproperties")
      response.raise_for_status()
      match_properties_data = response.json()
      ret = [];
      if '@graph' in match_properties_data:
        graph = match_properties_data.get('@graph')[0]
        if 'result' in graph:
          for res in graph['result']:
            ret.append(MatchProperty(res["name"]));
          return ret;
        else:
          print("Unexpected response structure: missing result.");
          return None;
      else:
          print("Unexpected response structure: missing graph.");
          return None;
    except requests.exceptions.RequestException as e:
      print(f"Error fetching match properties: {e}")
      return None

  def analyzeTerms(self, terms: list[str], matchTypes: list[Matchtype], matchProperties: list[MatchProperty]):
    payload = {
        "terms": terms,
        "matchTypes": [mt.get_type() for mt in matchTypes],
        "matchProperties": [mp.get_property() for mp in matchProperties]
    }
    headers = {'Content-Type': 'application/json'}

    try:
      response = requests.post(f"{self.endpoint}/analyse", data=json.dumps(payload), headers=headers)
      response.raise_for_status()
      return SemanticAnalysisResponse(response.json())
    except requests.exceptions.RequestException as e:
      print(f"Error during semantic analysis request: {e}")
      return None



class SemanticAnalysisResponse:
  def __init__(self, data):
    self.data = data
    self._matches = self._parse_matches()

  def get_analysis_results(self):
    return self.data

  def get_matches(self):
      return self._matches

  def _parse_matches(self):
      matches = []
      if self.data and '@graph' in self.data:
          for graph_item in self.data['@graph']:
              if 'result' in graph_item:
                  for result_item in graph_item['result']:
                      matching_term = graph_item.get('query', 'N/A')
                      match_property = result_item.get('matchProperty', 'N/A')
                      match_type = result_item.get('matchType', 'N/A')
                      term_code = result_item.get('termCode', 'N/A')
                      vocabulary = result_item.get('inDefinedTermSet', 'N/A')
                      concept_uri = result_item.get('@id', 'N/A')
                      match = Match(matching_term, match_property, match_type, term_code, vocabulary, concept_uri)
                      matches.append(match)
      return matches