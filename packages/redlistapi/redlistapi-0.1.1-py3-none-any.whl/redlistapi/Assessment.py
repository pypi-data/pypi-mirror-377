from dataclasses import dataclass, field
import os
import warnings
from . import api
import numpy as np
import pandas
import json
import pickle

try:
    import shapely
    import geopandas
    import osgeo.gdal
    import geojson
    _SPATIAL_AVAILABLE = True
except ImportError:
    warnings.warn(
        "Optional spatial dependencies not installed."
        "Spatial methods will not work.",
        ImportWarning
        )
    _SPATIAL_AVAILABLE = False


@dataclass
class Assessment:
    """
    Represents an IUCN Red List assessment.

    Attributes:
        assessment (dict): The Red List assessment.
        ranges (dict): The range associated with the assessment.
        points (dict): The points associated with the assessment.

    Methods:
        ranges_as_geodataframe(): Get the assessment ranges as a geopandas.GeoDataframe instance.
        points_as_geodataframe(): Get the assessment points as a geopandas.GeoDataframe instance.
        geometry_to_file(): Writes the geometries (ranges and points) to file.
    """

    assessment: list
    ranges: list = None
    points: list = None
    _spatial: bool = _SPATIAL_AVAILABLE

    def __post_init__(self):
        if self._spatial:

            # From https://gdal.org/en/stable/drivers/vector/geojson.html (2024/10/25)
            #
            # OGR_GEOJSON_MAX_OBJ_SIZE=<MBytes>: (GDAL >= 3.0.2) Defaults to 200.
            # Size in MBytes of the maximum accepted single feature,
            # or 0 to allow for a unlimited size (GDAL >= 3.5.2).
            #
            # Since currently the server is on GDAL 3.0.4 (released 2020/01/28), we will set
            # the value to 10 000 000 (10 GB).
            # Once we have GDAL >= 3.5.2 we can try to set it to 0.
            os.environ['OGR_GEOJSON_MAX_OBJ_SIZE'] = '10000'

            # Setup GeoJSON max object size in MB (default = 200).
            # From GDAL >= 3.5.2 value can be set to 0 for unlimited.
            osgeo.gdal.SetConfigOption('OGR_GEOJSON_MAX_OBJ_SIZE', '10000')


    @property
    def assid(self):
        return self.assessment['assessment_id']

    @property
    def taxid(self):
        return self.assessment['taxon']['sis_id']
    
    @property
    def scientific_name(self):
        return self.assessment['taxon']['scientific_name']

    @property
    def main_common_name(self):
        name = [
            name.get('name')
            for name in self.assessment.get('taxon').get('common_names',[{}])
            if name.get('main')]
        if not name:
            return None
        return name[0]

    def to_pickle(self, path:str):
        '''
        Save the Assessment instance as a Python pickle file.
        
        Parameters:
            path (str): The path to the file where to pickle the instance.
        '''
        with open(path, 'wb') as file:
            pickle.dump(self, file)

    def _code_description(self, code_desc, lang = 'en'):
        if isinstance(code_desc, dict):
            return {
                'code'        : np.str_(code_desc.get('code')),
                'description' : np.str_(code_desc.get('description').get(lang))
                }
        if isinstance(code_desc, list):
            return [self._code_description(cd, lang) for cd in code_desc]
        raise NotImplementedError('Only dicts or lists are supported')
    
    def assessment_as_pandas(self):
        '''Notes
        
        This method creates a table from root-level parameters in the assessment
        response, and key parameters from the taxon and system sub-structures.
        
        Some parameters from the taxon sub-structure were not interpreted as the
        formal sutructure could not be decided:
            species_taxa,
            subpopulation_taxa,
            infrarank_taxa,
            ssc_groups,
            common_names,
            synonyms

        Some root-level parameters were renamed or interpreted to their english
        names for ease of interpretation:
            assessment_id,
            sis_taxon_id,
            red_list_category,
            criteria,
            population_trend,
        
        The 3 possible system levels were translated to english language names
        and cast as boolean to 3 separate columns.
        '''
        ass = self.assessment # shortener to make the following mess somewhat more readable
        dlist = [{
            'assid'             : np.int64(ass.get('assessment_id',   None)),                     # renamed
            'taxid'             : np.int64(ass.get('sis_taxon_id',    None)),                     # renamed
            'assessment_date'   : np.datetime64(ass.get('assessment_date', None)),
            'year_published'    : np.int32(ass.get('year_published',  None)),
            'latest'            : np.bool_(ass.get('latest',          None)),
            'scientific_name'   : np.str_( ass.get('taxon', {}).get('scientific_name',    None)),
            'kingdom_name'      : np.str_( ass.get('taxon', {}).get('kingdom_name',       None)),
            'phylum_name'       : np.str_( ass.get('taxon', {}).get('phylum_name',        None)),
            'class_name'        : np.str_( ass.get('taxon', {}).get('class_name',         None)),
            'order_name'        : np.str_( ass.get('taxon', {}).get('order_name',         None)),
            'family_name'       : np.str_( ass.get('taxon', {}).get('family_name',        None)),
            'genus_name'        : np.str_( ass.get('taxon', {}).get('genus_name',         None)),
            'species_name'      : np.str_( ass.get('taxon', {}).get('species_name',       None)),
            'authority'         : np.str_( ass.get('taxon', {}).get('authority',          None)),
            'species'           : np.str_( ass.get('taxon', {}).get('species',            None)),
            'subpopulation'     : np.str_( ass.get('taxon', {}).get('subpopulation',      None)),
            'infrarank'         : np.str_( ass.get('taxon', {}).get('infrarank',          None)),
            'species_taxa'      : np.str_( ass.get('taxon', {}).get('species_taxa',       None)), # complex structure
            'subpopulation_taxa': np.str_( ass.get('taxon', {}).get('subpopulation_taxa', None)), # complex structure
            'infrarank_taxa'    : np.str_( ass.get('taxon', {}).get('infrarank_taxa',     None)), # complex structure
            'ssc_groups'        : np.str_( ass.get('taxon', {}).get('ssc_groups',         None)), # complex structure
            'common_names'      : np.str_( ass.get('taxon', {}).get('common_names',       None)), # complex structure
            'synonyms'          : np.str_( ass.get('taxon', {}).get('synonyms',           None)), # complex structure
            'possibly_extinct'  : np.bool_(ass.get('possibly_extinct', None)),
            'possibly_extinct_in_the_wild' : np.bool_(ass.get('possibly_extinct_in_the_wild', None)),
            'red_list_category' : np.str_( ass.get('red_list_category', {}).get('code', None)),   # interpreted
            'red_list_criteria' : np.str_( ass.get('criteria',          None)),                   # renamed
            'url'               : np.str_( ass.get('url',               None)),
            'citation'          : np.str_( ass.get('citation',          None)),
            'assessment_ranges' : np.bool_(ass.get('assessment_ranges', None)),
            'assessment_points' : np.bool_(ass.get('assessment_points', None)),
            'population_trend'  : np.str_((ass.get('population_trend', {}) or {}).get('description', {}).get('en', None)),
            'terrestrial' : np.bool_(0 in [int(system['code']) for system in ass.get('systems', {})]),
            'freshwater'  : np.bool_(1 in [int(system['code']) for system in ass.get('systems', {})]),
            'marine'      : np.bool_(2 in [int(system['code']) for system in ass.get('systems', {})]),
            }]
        return pandas.DataFrame(dlist)

    def biogeographical_realms_as_pandas(self, lang='en'):
        ass = self.assessment
        dlist = self._code_description(ass.get('biogeographical_realms'), lang = lang)
        return pandas.DataFrame(dlist)
    
    def conservation_actions_as_pandas(self):
        ass = self.assessment
        dlist = ass.get('conservation_actions')
        return pandas.DataFrame(dlist)
    
    def credits_as_pandas(self):
        ass = self.assessment
        dlist = ass.get('credits')
        return pandas.DataFrame(dlist)
    
    def documentation_as_pandas(self):
        ass = self.assessment
        dlist = [ass.get('documentation')]
        return pandas.DataFrame(dlist)
    
    def errata_as_pandas(self):
        ass = self.assessment
        dlist = ass.get('errata')
        return pandas.DataFrame(dlist)
    
    def faos_as_pandas(self):
        ass = self.assessment
        dlist = ass.get('faos')
        return pandas.DataFrame(dlist)
    
    def growth_forms_as_pandas(self):
        ass = self.assessment
        dlist = ass.get('growth_forms')
        return pandas.DataFrame(dlist)
    
    def habitats_as_pandas(self, lang='en'):
        ass = self.assessment
        dlist = [
            { 
                'code'            : np.str_(habitat.get('code', None)),
                'description'     : np.str_(habitat.get('description').get(lang, None)),
                'majorImportance' : np.str_(habitat.get('majorImportance', None)),
                'season'          : np.str_(habitat.get('season', None)),
                'suitability'     : np.str_(habitat.get('suitability', None))
                }
            for habitat in ass.get('habitats')
            ]
        return pandas.DataFrame(dlist)
    
    def lmes_as_pandas(self):
        ass = self.assessment
        dlist = ass.get('lmes')
        return pandas.DataFrame(dlist)

    def locations_as_pandas(self, lang='en'):
        ass = self.assessment
        dlist = [
            {
                'code'         : np.str_(location.get('code')),
                'description'  : np.str_(location.get('description').get(lang, None)),
                'formerlyBred' : np.bool_(location.get('formerlyBred')),
                'is_endemic'   : np.bool_(location.get('is_endemic')),
                'origin'       : np.str_(location.get('origin')),
                'presence'     : np.str_(location.get('presence')),
                'seasonality'  : np.str_(location.get('seasonality'))
                }
            for location in ass.get('locations')
            ]
        return pandas.DataFrame(dlist)

    def references_as_pandas(self):
        ass = self.assessment
        dlist = ass.get('references')
        return pandas.DataFrame(dlist)

    def researches_as_pandas(self):
        ass = self.assessment
        dlist = ass.get('researches')
        return pandas.DataFrame(dlist)

    def scopes_as_pandas(self, lang = 'en'):
        ass = self.assessment
        dlist = self._code_description(ass.get('scopes'), lang = lang)
        return pandas.DataFrame(dlist)

    def stresses_as_pandas(self, lang = 'en'):
        ass = self.assessment
        dlist = self._code_description(ass.get('stresses'), lang = lang)
        return pandas.DataFrame(dlist)
    
    def supplementary_info_as_pandas(self):
        ass = self.assessment
        dlist = [ass.get('supplementary_info')]
        return pandas.DataFrame(dlist)
    
    def systems_as_pandas(self, lang = 'en'):
        ass = self.assessment
        dlist = self._code_description(ass.get('systems'), lang = lang)
        return pandas.DataFrame(dlist)
    
    def taxon_as_pandas(self):
        ass = self.assessment
        dlist = [ass.get('taxon')]
        return pandas.DataFrame(dlist)
    
    def taxon_common_names_as_pandas(self, lang = 'en'):
        '''This is in taxon'''
        ass = self.assessment
        dlist = [
            {
                'language_code' : cn.get('language').get('code'),
                'language'      : cn.get('language').get('description').get(lang),
                'main'          : cn.get('main'),
                'name'          : cn.get('name')
                }
            for cn in ass.get('taxon').get('common_names')
            ]
        return pandas.DataFrame(dlist)
    
    def taxon_species_taxa_as_pandas(self):
        '''This is in taxon'''
        ass = self.assessment
        dlist = ass.get('taxon').get('species_taxa')
        return pandas.DataFrame(dlist)
    
    def taxon_subpopulation_taxa_as_pandas(self):
        '''This is in taxon'''
        ass = self.assessment
        dlist = ass.get('taxon').get('subpopulation_taxa')
        return pandas.DataFrame(dlist)

    def taxon_infrarank_taxa_as_pandas(self):
        '''This is in taxon'''
        ass = self.assessment
        dlist = ass.get('taxon').get('infrarank_taxa')
        return pandas.DataFrame(dlist)
    
    def taxon_ssc_groups_as_pandas(self):
        '''This is in taxon'''
        ass = self.assessment
        dlist = ass.get('taxon').get('ssc_groups')        
        return pandas.DataFrame(dlist)

    def taxon_synonyms_as_pandas(self):
        '''This is in taxon...'''
        ass = self.assessment
        dlist = ass.get('taxon').get('synonyms')
        return pandas.DataFrame(dlist)
    
    def threats_as_pandas(self, lang = 'en'):
        ass = self.assessment
        dlist = [
            {
                'ancestry'    : threat.get('ancestry'),
                'code'        : threat.get('code'),
                'description' : threat.get('description').get(lang),
                'ias'         : threat.get('ias'),
                'internationalTrade' : threat.get('internationalTrade'),
                'scope'       : threat.get('scope'),
                'score'       : threat.get('score'),
                'severity'    : threat.get('severity'),
                'text'        : threat.get('text'),
                'timing'      : threat.get('timing'),
                'virus'       : threat.get('virus')
                }
            for threat in ass.get('threats')
            ]
        return pandas.DataFrame(dlist)
    
    def use_and_trade_as_pandas(self, lang = 'en'):
        ass = self.assessment
        dlist = [
            {
                'code'          : uat.get('code'),
                'description'   : uat.get('description').get(lang),
                'international' : uat.get('international'),
                'national'      : uat.get('national'),
                'other'         : uat.get('other'),
                'subsistence'   : uat.get('subsistence')
                }
            for uat in ass.get('use_and_trade')
            ]
        return pandas.DataFrame(dlist)
    
      #############################################
     # Spatial Methods From Here To End Of Class #
    #############################################

    def _geom_filter(self, geom_attribute, filters):
        if not self._spatial:
            raise ImportError("Spatial dependencies missing. Install with: pip install redlistapi[spatial]")

        return geojson.FeatureCollection(
            [feature for feature in getattr(self, geom_attribute)['features']
            if all(feature['properties'][key] in values for key, values in filters.items())]
            )
    
    def _features_iucn_to_kba_union(self, features, season):
        '''Unions a set of features into a single KBA geometric feature'''
        if not self._spatial:
            raise ImportError("Spatial dependencies missing. Install with: pip install redlistapi[spatial]")

        # Convert to shapely to perform the union, then return a geojson.
        # Need to use `if feature['geometry']` or you get ERROR with null geometry.
        # If you use `.buffer(0)` you mask all points.
        #geoms = [shapely.geometry.shape(f['geometry']).buffer(0) for f in features] # Raises ERROR with null geometry.
        #geoms = [shapely.geometry.shape(f['geometry']).buffer(0) for f in features if f['geometry']] # Masks all points
        geoms = [shapely.geometry.shape(f['geometry']) for f in features if f['geometry']]
        
        try:
            geoms = shapely.union_all(geoms)
        except:
            # NOTE: should be equivalent to OGR union with ['METHOD=STRUCTURE']
            geoms = shapely.union_all([shapely.make_valid(g) for g in geoms])

        return geojson.Feature(
                geometry=geoms,
                properties={
                    'taxid':self.taxid,
                    'binomial':self.scientific_name,
                    'season':season
                    }
                )

    def _geom_kba(self, geom_attribute):
        '''Generic IUCN to KBA geometry converter
        
        This method converts a species' IUCN geometries (ranges or points) to
        KBA geometries following the KBA Guidelines.

        It returns geometries classified as:
            'breeding' and/or 'nonbreeding' if the species has seasonal distributions.
            'resident' if the species does not have seasonal distributions.
        '''
        if not self._spatial:
            raise ImportError("Spatial dependencies missing. Install with: pip install redlistapi[spatial]")

        # no geom case
        if not getattr(self, geom_attribute):
            return None

        # origin filter
        origin_codes = (1, 2, 6)

        # presence filter        
        if self.assessment['possibly_extinct'] or self.assessment['possibly_extinct_in_the_wild']:
            presence_codes = (1, 2, 3)
        else:
            presence_codes = (1, 2)
    
        # set for season filter(s)
        season_set = set([f['properties']['seasonal'] for f in getattr(self, geom_attribute)['features']])

        # season filter: resident case
        if 2 not in season_set and 3 not in season_set:
            seasonal_codes = (1, 5)
            filter = {'origin':origin_codes, 'presence':presence_codes, 'seasonal':seasonal_codes}
            features = [self._features_iucn_to_kba_union(
                features = self._geom_filter(geom_attribute, filter)['features'],
                season = 'resident'
                )]

        else:
            features = []

            # season filter: breeding case
            if season_set.intersection({1, 2, 5}):
                seasonal_codes = (1, 2, 5)
                filter = {'origin':origin_codes, 'presence':presence_codes, 'seasonal':seasonal_codes}
                features.append(self._features_iucn_to_kba_union(
                    features = self._geom_filter(geom_attribute, filter)['features'],
                    season = 'breeding'
                    ))

            # season filter: nonbreeding case
            if season_set.intersection({1, 3, 5}):
                seasonal_codes = (1, 3, 5)
                filter = {'origin':origin_codes, 'presence':presence_codes, 'seasonal':seasonal_codes}
                features.append(self._features_iucn_to_kba_union(
                    features = self._geom_filter(geom_attribute, filter)['features'],
                    season = 'nonbreeding'
                    ))

        # return
        return geojson.FeatureCollection(features)

    @property
    def ranges_kba(self):
        if not self._spatial:
            raise ImportError("Spatial dependencies missing. Install with: pip install redlistapi[spatial]")

        return self._geom_kba('ranges')

    @property
    def points_kba(self):
        if not self._spatial:
            raise ImportError("Spatial dependencies missing. Install with: pip install redlistapi[spatial]")

        return self._geom_kba('points')

    def _geom_as_geodataframe(self, geom_attribute, kba=False):
        if not self._spatial:
            raise ImportError("Spatial dependencies missing. Install with: pip install redlistapi[spatial]")

        if getattr(self, geom_attribute):
            if kba:
                gdf = geopandas.GeoDataFrame.from_features(self._geom_kba(geom_attribute), crs='EPSG:4326')
            else:
                gdf = geopandas.GeoDataFrame.from_features(getattr(self, geom_attribute), crs='EPSG:4326')
        return gdf
    
    def ranges_as_geodataframe(self, kba=False):
        if not self._spatial:
            raise ImportError(
                "Spatial dependencies missing."
                "Install with: pip install redlistapi[spatial]"
                )

        return self._geom_as_geodataframe('ranges', kba=kba)
    
    def points_as_geodataframe(self, kba=False):
        if not self._spatial:
            raise ImportError("Spatial dependencies missing."
            "Install with: pip install redlistapi[spatial]"
            )

        return self._geom_as_geodataframe('points', kba=kba)

    def geometry_to_file(self, path, append=False, overwrite=False, kba=False):
        '''
        Write ranges and points to a GIS file.

        The file type is determined by the file name in the path parameter.
        It is STRONGLY suggested to use geopackage or other modern file types, as ESRI shapefiles
        do not support field names longer than 10 characters and will truncate the names.
        '''
        if not self._spatial:
            raise ImportError(
                "Spatial dependencies missing."
                "Install with: pip install redlistapi[spatial]"
                )

        if append and overwrite:
            raise ValueError('Append and overwrite cannot be used together.')
        
        if os.path.exists(path):
            if not append and not overwrite:
                raise ValueError(
                    "File already exists. Use append=True or overwrite=True.")
            elif overwrite:
                os.remove(path)

        if self.ranges:
            ranges = self.ranges_as_geodataframe(kba=kba)
            if len(ranges):
                ranges.to_file(path, layer='points', append=True)
        if self.points:
            points = self.points_as_geodataframe(kba=kba)
            if len(points):
                points.to_file(path, layer='ranges', append=True)


class AssessmentFactory:
    '''
    A factory to create Assessment objects
    
    Methods:
        from_assessment_id(token, assessment_id): Retrieves an assessment and its geometries. 
        from_species(token, species, scope): Retrieves a species's latest assessment and its geometries.
    '''
    def __init__(self, token):
        self.token = token

    def _scientific_name_to_assessment_id(self, genus, species, infra=None, scope='1'):
        '''
        Internal method to obtain a species' scope-specific assessemnt id.

        A species will have multiple assessments. This method filters to keep the latest assessments.
        It will then filter to keep only the assessment for the desired geographical scope.
        This should return only one assessment id, and will raise errors otherwise.

        Parameters:
            token (str): A Red List API token.
            genus_name (str): The species' genus name.
            species_name (str): The species' specific name.
            infra_name (str): The species' infra name/rank.

            scope (str): The geographical scope for the assessment. Defaults to '1' (Global).

        Returns:
            The species' latest assessment id (int) for the specified scope.
        '''
        assessments = api.v4.taxa.scientific_name(token=self.token, genus_name=genus, species_name=species, infra_name=infra).json()['assessments']
        assids = [
            assessment['assessment_id'] for assessment in assessments
            if assessment['latest'] and scope in [scope['code'] for scope in assessment['scopes']]
            ] # TODO check behaviour.
        if len(assids) > 1:
            raise ValueError('Too many positive matches')
        if assids:
            return assids[0]
        else:
            raise ValueError('No match')
        
    def _taxid_to_assid(self, taxid, scope='1'):
        '''
        Internal method to obtain a species' scope-specific assessemnt id.

        A species will have multiple assessments. This method filters to keep the latest assessments.
        It will then filter to keep only the assessment for the desired geographical scope.
        This should return only one assessment id, and will raise errors otherwise.

        Parameters:
            token (str): A Red List API token.
            taxid (int): The IUCN/SIS taxon id.
            scope (str): The geographical scope for the assessment. Defaults to '1' (Global).

        Returns:
            The species' latest assessment id (int) for the specified scope.
        '''
        assessments = api.v4.taxa.sis.by_sis_id(token=self.token, sis_id=taxid).json()['assessments']
        assids = [
            assessment['assessment_id'] for assessment in assessments
            if assessment['latest'] and scope in [scope['code'] for scope in assessment['scopes']]
            ] # TODO check behaviour.
        if len(assids) > 1:
            raise ValueError('Too many positive matches')
        if assids:
            return assids[0]
        else:
            raise ValueError('No match')

    def from_assessment_id(self, assessment_id):
        '''
        Create an Assessment class instance for a specified assessment id.

        This method can be used to retrieve any assessment id, including historical ones.

        Parameters:
            token (str): A Red List API token.
            assessment_id (int): A Red List species' assessment id.

        Returns:
            An Assessment class instance.
        '''
        assessment = api.v4.assessment.by_assessment_id(token=self.token, assessment_id=assessment_id).json()
        return Assessment(assessment=assessment)
    
    def from_taxid(self, taxid, scope='1'):
        '''
        Create an Assessment class instance.

        This method will return an Assessment class instance populated with the species' latest
        assessment.
        
        Since an Assessment class can only be populated with one assessment at a time, a spatial
        scope parameter is needed. By default this method will retrieve the species' global
        assessment.

        Parameters:
            token (str): A Red List API token.
            taxid (int): A Red List species' taxon id.
            scope (str): A Red List assessment scope code parsed as str.

        Returns:
            An Assessment class instance.
        '''
        assessment_id = self._taxid_to_assid(
            taxid,
            scope
            )
        return self.from_assessment_id(assessment_id)

    def from_scientific_name(self, genus_name, species_name, infra_name=None, scope='1'):
        '''
        Create an Assessment class instance.

        This method will return an Assessment class instance populated with the species' latest
        assessment.
        
        Since an Assessment class can only be populated with one assessment at a time, a spatial
        scope parameter is needed. By default this method will retrieve the species' global
        assessment.

        Parameters:
            token (str): A Red List API token.
            genus_name (str): A Red List species' genus name.
            species_name (str): A Red List species' specific name.
            infra_name (str): A Red List species' infra name.
            scope (str): A Red List assessment scope code parsed as str.

        Returns:
            An Assessment class instance.
        '''
        assessment_id = self._scientific_name_to_assessment_id(
            genus_name,
            species_name,
            infra_name,
            scope
            )        
        return self.from_assessment_id(assessment_id)
    
    @staticmethod
    def from_json(input):
        '''Create an Assessment class instance from a json file or string.
        
        Parameters:
            input (str): Path to a json file or a json string.

        Returns:
            An Assessment class instance.
        '''
        if os.path.isfile(input):
            try:
                with open(input, 'r') as file:
                    assessment = json.load(file)
            except json.JSONDecodeError:
                raise ValueError("The file exists but does not contain a valid JSON.")
        else:
            try:
                assessment = json.loads(input)
            except json.JSONDecodeError:
                raise ValueError("Input is neither a valid file path nor a valid JSON string.")
        return Assessment(assessment=assessment)


    @staticmethod
    def from_pickle(path:str):
        '''
        Create an Assessment class instance from a Python pickle file.

        Parameters:
            path (str): Path to a Red List API pickled assessment.
            
        Returns:
            An Assessment class instance.
        '''
        with open(path, 'rb') as file:
            assessment = pickle.load(file)

        if not isinstance(assessment, Assessment):
            raise ValueError('Pickle is not an Assessment')

        return assessment

    @staticmethod
    def to_pickle(assessment:Assessment, path:str):
        '''
        Save the Assessment instance as a Python pickle file.
        
        Parameters:
            path (str): The path to the file where to pickle the instance.
        '''
        if not isinstance(assessment, Assessment):
            raise ValueError('Assessment is not an Assessment')

        with open(path, 'wb') as file:
            pickle.dump(assessment, file)

