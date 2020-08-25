/**
* @author Salesforce.com
* @date 2020
*
* @description This recommendation plugin returns a sorted list of recommendations
* as pricebook entries, ordered in descending order of score.
*/
public with sharing class ScoredRecoPluginImpl implements ProductRecommendationPlugin {
    public PricebookEntry[] recommend(SObject quote, List<SObject> quoteLines) {
        // Get the price book Id of the quote
        Id pricebookId = (Id)quote.get('SBQQ__PricebookId__c');
    
        // Get Ids of all products in the quote
        Id[] productIdsInQuote = new Id[0];
        for (SObject quoteLine : quoteLines) {
            Id productId = (Id)quoteLine.get('SBQQ__Product__c');
            productIdsInQuote.add(productId);
        }
    
        // Query the recommendation custom object records of all products in quote.
        ProductRecommendation__c[] recommendations = [SELECT SBQQ__Product2Id__r.Name, RecommendedProduct2Id__c, Score__c FROM ProductRecommendation__c WHERE SBQQ__Product2Id__c IN :productIdsInQuote];
    
        Map<Id, Integer> productVsScore = new Map<Id,Integer>();
        Map<Id, String> recIdVsProd = new Map<Id,String>();
        // Get Ids of all recommended products
        Id[] recommendedProductIds = new Id[0];
        for(ProductRecommendation__c recommendation : recommendations) {
            Id recommendedId = recommendation.RecommendedProduct2Id__c;
            recommendedProductIds.add(recommendedId);
            recIdVsProd.put(recommendedId, recommendation.SBQQ__Product2Id__r.Name);
            Integer score = productVsScore.get((Id)recommendedId);
            if (score == null || score < recommendation.Score__c) {
                score = (Integer)recommendation.Score__c;
                productVsScore.put(recommendedId, score);
            }
        }

        // Query the price book entries of the above recommended products
        PricebookEntry[] priceBookEntries = [SELECT Id, UnitPrice, Pricebook2Id, Product2Id, Product2.Name, Product2.IsActive, Product2.ProductCode FROM PricebookEntry WHERE Product2Id IN :recommendedProductIds AND Pricebook2Id = :pricebookId];

        // Custom Sort
        EntryWrapper[] entryList = new List<EntryWrapper>();
        for (PricebookEntry entry : priceBookEntries) {
            if (!productIdsInQuote.contains(entry.Product2Id) && entry.Product2.IsActive) {
                /*
                Optional customization :
                Suggested_For__c is a sample custom field created to store the productId, this suggestion if made for.
                To access this field as entry.Product2.Suggested_For__c,
                add this as a SOQL search field (Product2.Suggested_For__c) in the above query for getting pricebook entries
                Eg. PricebookEntry[] priceBookEntries = [SELECT Id, Pricebook2Id, Product2.Name, Product2.Suggested_For__c FROM...]
                // entry.Product2.Suggested_For__c = recIdVsProd.get(entry.Product2Id);
                */
                entryList.add(new EntryWrapper(entry, productVsScore.get(entry.Product2Id)));
            }
        }
        entryList.sort();
        
        PricebookEntry[] orderedList = new PricebookEntry[0];
        for (EntryWrapper entryWrapper : entryList) {
            orderedList.add(entryWrapper.pbEntry);
        }
        
        return orderedList;
    }
}