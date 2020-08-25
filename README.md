# CPQ Product Recommendation Engine Demo
This is a demo recommendation engine which reads all org quotes from salesforce database, 
generates product recommendations and inserts them into the Salesforce database. 

## Architectural Overview
![Architecture](img/architecture.png?raw=true)

The recommendation engine is scheduled to run once a day, which can be configured in [job.py](job.py).

The recommendation custom object records inserted by the engine are queried and processed by the 
CPQ ProductRecommendationPlugin (Eg. [ScoredRecoPluginImpl](apex-plugin-impl/ScoredRecoPluginImpl.cls) in the below architecture diagram) which returns an ordered list of pricebook entries.
A couple of sample implementations of the plugin are provided in the 
directory [apex-plugin-impl](apex-plugin-impl).

## Setup and Run
   - Here's an example of a [recommendation custom object](custom-objects/ProductRecommendation__c)
     that you should add to your org
     before this engine is run to insert the custom object records into your org:
     
     ```
     ProductRecommendation__c {
         Id Product2Id__c,
         Id RecommendedProduct2Id__c,
         Integer Score__c
     }
     ```
   - Set the org login credentials as environment variables using `export`
        ```
        export ORG_USERNAME=<username>
        export ORG_PASSWORD=<password>
        export ORG_SECURITY_TOKEN=<token>
        export ORG_DOMAIN=<domain> - should be 'test' or 'login' or 'something.my'
        ```
   - Configure the recommendation custom object in the `bulk.py` code
        - Set the name of your recommendation custom object and its custom fields in the constant variables:
          `RECOMMENDATION_OBJECT`, `PRODUCT_ID_FIELD`, `RECOMMENDED_PRODUCT_ID_FIELD`, `SCORE_FIELD`
        - Construct the recommendation object record in the method - `get_recommendation_record()`
        
   - Open a terminal and `cd` into the project directory
   - Install dependencies
        ```console
        $ pip install -r requirements.txt
   - Make the file executable
        ```console
        $ chmod +x start.sh
   - Invoke the job script
        ```console
        $ ./start.sh

## Run Tests
[pytest](https://pytest.org/) is used to run the integration tests. <br>
As mentioned above, the org login credentials need to be set as environment variables before running the tests. <br>
To run the tests, type:

```
$ pytest
```
