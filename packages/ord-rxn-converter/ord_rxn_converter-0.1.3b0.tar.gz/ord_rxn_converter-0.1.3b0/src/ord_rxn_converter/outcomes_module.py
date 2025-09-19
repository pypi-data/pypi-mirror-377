# import requirements:
from ord_schema.proto import dataset_pb2, reaction_pb2
from google.protobuf.message import Message
from uuid import uuid4
from ord_rxn_converter.utility_functions_module import extract_all_enums
from ord_rxn_converter.identifiers_module import extract_compound_identifiers, generate_compound_table

#generate enums_data to be accessible here TODO - have importable object instead..?
enums_data = extract_all_enums(reaction_pb2)

def extract_reaction_outcomes(reactionID, outcomes): 

    """
    Extracts outcome information from ORD reaction data.

    Takes a reaction outcome object (in Google Protobuf message type based on
    ORD structure schema) and extracts data about reaction outcomes
    including reaction time, conversion percentages, product information, and
    analytical data.

    Args:
        reactionID (str): Unique identifier for the reaction.
        outcomes (list): List of outcome objects from a reaction, containing
            reaction time, conversion, products, and analyses data.

    Returns:
        tuple: A tuple containing two elements:
            outcomes_list (list): A list of lists, where each inner list contains:
                [reactionID, outcomeKey, reaction_time_value, time_unit, 
                conversion_value, products_list, analyses_list]
            outcome_identifiers (list): A list of compound identifiers associated
                with the reaction outcomes, or None if no products are present.
    """

    outcomes_list = []
    outcome_identifiers = []
    outcome_measurements = []
    
    for index, outcome in enumerate(outcomes, start=1):
        outcomeKey = f"outcomeKey_{index}_{reactionID}"
        
        # reaction_time = 1
        time_unit = enums_data['Time.TimeUnit'][outcome.reaction_time.units]
        
        # conversion = 2

        # products = 3
        if outcome.products:
            products = outcome.products 
            products_list, compound_table = extract_product(products)
            outcome_identifiers.extend(compound_table)
        else:
            products_list = None
            outcome_identifiers = None
          
        # analyses = 4  
        if outcome.analyses:
            analyses = outcome.analyses
            analyses_list = extract_analyses(analyses)
        else: analyses_list = None
            
        outcomes_list.append([reactionID, outcomeKey, outcome.reaction_time.value , time_unit, outcome.conversion.value, products_list, analyses_list])
    
    return outcomes_list, outcome_identifiers

def extract_product (products):
    """
    Extracts product data and related measurements from ORD product objects.

    Takes product objects from a reaction outcome and extracts information
    including identifiers, measurements, textures, features, and reaction roles.
    Also generates compound tables with standardized identifiers.

    Args:
        products (list): List of product objects from a reaction outcome.

    Returns:
        tuple: A tuple containing two elements:
            products_list (list): A list of lists, where each inner list contains:
                [inchi_key, is_desired_product, products_measurements, isolated_color,
                product_texture, feature_dict, reaction_role]
            compound_identifiers (list): A list of compound tables containing
                standardized compound identifiers for all products.
    """

    products_list = []
    products_measurements = []
    compound_identifiers = []
    
    for product in products:
        # identifiers = 1
        if product.identifiers:
            identifiers = product.identifiers
            inchi_key, identifier_list = extract_compound_identifiers(identifiers)
            compound_identifiers.append(generate_compound_table(identifiers))
        else: 
            identifier_list = None
            inchi_key = None

        # TODO: need to generate the InChIKey from SMILES or InChI & use the InChI to update the COMPOUND TABLE should this be in the identifiers function? 

        # is_desired_product = 2

        # measurements = 3 
        if product.measurements:
            measurements = product.measurements 
            measurement_list = extract_product_measurements(measurements)
            products_measurements.append(measurement_list)
        else: 
            measurement_list = None
            products_measurements.append(measurement_list)   

        # isolated_color = 4
        
        # texture = 5
        if product.texture:
            texture = enums_data['Texture.TextureType'][product.texture.type]
            product_texture = {texture:product.texture.details}
        else: product_texture = None
        
        # features = 6 
        feature_dict = {feature_key: feature for feature_key, feature in product.features} if product.features else None
        #for feature_key, feature in product.features.items():
        #    feature_list.append(dict(zip(feature_key, feature)))

        # reaction_role = 7
        reaction_role = enums_data['ReactionRole.ReactionRoleType'].get(product.reaction_role, 'UNKNOWN')
        
        products_list.append([inchi_key, product.is_desired_product, products_measurements, 
            product.isolated_color, product_texture, feature_dict, reaction_role])
    
    return products_list, compound_identifiers
def extract_product_measurements(measurements):
    """
    Extracts measurement data from ORD product measurements.

    Processes measurement objects to extract analytical data 
    including measurement types, values, spectroscopic details, and chromatographic
    information.

    Args:
        measurements (list): List of measurement objects associated with a product.

    Returns:
        list: A list of lists, where each inner list contains measurement data:
            [analysis_key, measurement_type, details, uses_internal_standard,
            is_normalized, uses_authentic_standard, compound_authentic, 
            measurement_value, retention_time, time_unit, mass_spec_type,
            mass_spec_details, tic_minimum, tic_maximum, eic_masses,
            selectivity, wavelength, wavelength_unit]
    """
    measurement_list = []
    for index, measurement in enumerate(measurements): 
        analysis_key = measurement.analysis_key if measurement.analysis_key else None
        compound_authentic = measurement.authentic_standard if measurement.authentic_standard else None
        measurement_type = enums_data['ProductMeasurement.ProductMeasurementType'][measurement.type]

        measurement_value_type = measurement.WhichOneof('value') if measurement.WhichOneof('value') else None

        # percentage = 8
        if measurement_value_type == 'percentage': 
            measurement_value = measurement.percentage.value
            measurement_value_unit = 'Percent'
            
        # float_value = 9
        elif measurement_value_type == 'float_value':
            measurement_value = measurement.float_value.value
            measurement_value_unit = None
        
        # string_value = 10
        elif measurement_value_type == 'string_value':
            measurement_value = measurement.string_value
            measurement_value_unit = None
        
        # amount = 11 
        elif measurement_value_type == 'amount':
            amount_type, measurement_value, measurement_value_unit = extract_amount(measurement.amount)
        
        else: 
            measurement_value = None
            measurement_value_unit = None

        # retention_time = 12 
        if measurement.retention_time:
            retention_time = measurement.retention_time.value
            time_unit = enums_data['Time.TimeUnit'][measurement.retention_time.units]
        else: 
            retention_time = None
            time_unit = None

        if measurement.selectivity:
            select_type = enums_data['ProductMeasurement.Selectivity.SelectivityType'][measurement.selectivity.type]
        
        # mass_spec_details = 13
        if measurement.mass_spec_details:
            mass_spec_type = enums_data['ProductMeasurement.MassSpecMeasurementDetails.MassSpecMeasurementType'][measurement.mass_spec_details.type]
            mass_spec_details = measurement.mass_spec_details.details 
            tic_minimum = measurement.mass_spec_details.tic_minimum_mz 
            tic_maximum = measurement.mass_spec_details.tic_maximum_mz 
            eic_masses = []
            for eic_mass in measurement.mass_spec_details.eic_masses:
                eic_masses.append(eic_mass)
        else: 
            mass_spec_type = None
            mass_spec_details = None
            tic_minimum = None
            tic_maximum = None
            eic_masses = None

        # wavelength = 15
        if measurement.wavelength:
            wavelength = measurement.wavelength.value
            wavelength_unit = enums_data['Wavelength.WavelengthUnit'][measurement.wavelength.units]
        else: 
            wavelength = None
            wavelength_unit = None
        
        measurement_list.append([index, inchi_key, identifier_list, analysis_key, measurement_type, 
            measurement.details if measurement.details else None, 
            measurement.uses_internal_standard if measurement.uses_internal_standard else None, 
            measurement.is_normalized if measurement.is_normalized else None, 
            measurement.authentic_standard if measurement.authentic_standard else None, 
            measurement_value_type, measurement_value, measurement_value_unit, retention_time, time_unit,
            select_type, wavelength, wavelength_unit])

    return measurement_list

def extract_analyses(analyses):
    """
    Extracts analytical data from ORD reaction analyses.

    Processes analysis objects to extract information about analytical techniques,
    instrument details, and associated data for reaction outcome characterization.

    Args:
        analyses (dict): Dictionary of analysis objects keyed by analysis_key.

    Returns:
        list: A list of dictionaries, where each dictionary contains:
            {'analysisKey': str, 'analysisType': str, 'Details': str, 'CHMO_ID': str, 'IsolatedSpecies': bool, 'data': dict, 'instrumentManufacturer': str, 'lastCalibrated': datetime}
    """
    analyses_list = []
    data_dict = {}
    for analysis_key, analysis in analyses.items():
        analysis_type = enums_data['Analysis.AnalysisType'].get(analysis.type, 'UNKNOWN')
        for data_key, data in analysis.data.items(): 
            value = getattr(data, data.WhichOneof('kind'))
            dict_value = [value, data.description]
            data_dict.update([(data_key, dict_value)])
        analyses_list.append(
            ({'analysisKey':analysis_key,
            'analysisType':analysis_type,
            'Details':analysis.details,
            'CHMO_ID':analysis.chmo_id,
            'IsolatedSpecies':analysis.is_of_isolated_species, 
            'data':data_dict, 
            'instrumentManufacturer':analysis.instrument_manufacturer, 
            'lastCalibrated':analysis.instrument_last_calibrated
            })
        )
    return analyses_list