
# OPENLXP-XIA
## What is it?
OpenLXP XIA is a Python package that provides the validation functionality of extracted metadata from the source. In addition, it helps transform metadata into target metadata and further load it into indexing services. The OpenLXP XIA package does not include the metadata extraction process because extraction methods can be different for different sources. But once metadata gets extracted from the source, OpenLXP-XIA continues the V-T-V-L  (Validate-Transform-Validate-Load) cycle. 

The schema files used for validation can be placed on the schema server. Currently, OpenLXP-XIA uses AWS S3 buckets as a schema server. 

Below are the workflow which are performed by the OpenLXP-XIA after package installation.


## Workflows
The OpenLXP-XIA implements five core workflows after extracting metadata from the Specifiec source, as follows:

1. `Validate`: Compares extracted learning experience metadata against the configured source metadata reference schema stored in the Experience Schema Service (XSS).

2. `Transform`: Transforms extracted+validated source learning experience metadata to the configured target schema using the "XSR-to-Target" transformation map stored in the Experience Schema Service (XSS)

3. `Validate`: Compares transformed learning experience metadata against the configured target metadata reference schema stored in the Experience Schema Service (XSS).

4. `Load`: Pushes transformed and validated learning experience metadata to the target Experience Index Service (XIS) for further processing.

5. `Log`: Records error, warning, informational, and debug events which can be reviewed and monitored.

## Prerequisites
`Python >=3.7` : Download and install python from here [Python](https://www.python.org/downloads/).


## Installation

    $ python -m pip install OpenLXP-XIA (use the latest package version)

Add OpenLXP-XIA in the setting.py in your project.

INSTALLED_APPS = [
        ...
        
        'openlxp_xia',
        
        ....
]

## Configuration

1. On the Admin page, log in with the admin credentials 

2. `Add xis configuration`: Configure Experience Index Services (XIS): 

    `Xis metadata api endpoint`: API endpoint for XIS where metadata will get stored.

    Example:  
    `Xis metadata api endpoint`: http://localhost:8080/api/metadata/

    `Xis supplemental api endpoint`: API endpoint for XIS where supplemental metadata will get stored.

    Example:  
    `Xis supplemental api endpoint`: http://openlxp-xis:8020/api/supplemental-data/

    (Note: Replace localhost with the XIS Host)


3.  `Add xia configuration` : Configure Experience Index Agents(XIA):

    `Publisher`: Agent Name

    `Xss api`: API endpoint for XSS where schemas will be retrieved from.

    Example:  
    `Xss api`: https://localhost:8000/api/
    
    `Source metadata schema`: Schema iri or name for source metadata validation
    
    `Target metadata schema`: Schema iri or name for target metadata validation

    (Note: Please make sure to upload schema files in the Experience Schema Server (XSS). )


4. `Add metadata field overwrite`: Here, we can add new fields and their values or overwrite values for existing fields.

    `Field name`: Add new or existing field Name
    
    `Field type`: Add date type of the field
    
    `Field value`: Add corresponding value
    
    `Overwrite`: Check the box if existing values need to be overwritten.

## Running ETL Pipeline:

ETL or EVTVL (Extract-Transform-Load) Pipeline can be run through two ways:

1. Through API Endpoint:
To run ETL tasks run below API:
    
    http://localhost:8000/api/xia-workflow
(Note: Change localhost with XIA host)

2. Periodically through celery beat: 
 On the admin page add periodic task and it's schedule. On selected time interval celery task will run.


## Logs
To check the running of celery tasks, check the logs of application and celery container.

## Documentation

## Troubleshooting


## License

 This project uses the [MIT](http://www.apache.org/licenses/LICENSE-2.0) license.
  
