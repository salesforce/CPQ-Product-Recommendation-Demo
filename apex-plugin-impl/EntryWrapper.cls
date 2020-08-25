/**
* @author Salesforce.com
* @date 2020
*
* @description This class implements Comparable, and encapsulates the pricebook entry along with a score.
*/
public class EntryWrapper implements Comparable {

    public PricebookEntry pbEntry;
    public Integer score;
    
    // Constructor
    public EntryWrapper(PricebookEntry entry, Integer sc) {
        pbEntry = entry;
        score = sc;
    }
    
    // Compare opportunities based on the opportunity amount.
    public Integer compareTo(Object compareTo) {
        // Cast argument to EntryWrapper
        EntryWrapper other = (EntryWrapper)compareTo;
        
        // The return value of 0 indicates that both elements are equal.
        Integer returnValue = 0;
        if (score < other.score) {
            // Set return value to a positive value.
            returnValue = 1;
        } else if (score > other.score) {
            // Set return value to a negative value.
            returnValue = -1;
        } else if ((score == null) && (other.score != null)){
            // nulls-last implementation
            returnValue = 1;
        } else if ((score != null) && (other.score == null)){
            // nulls-last implementation
            returnValue = -1;
        }        
        return returnValue;       
    }
}