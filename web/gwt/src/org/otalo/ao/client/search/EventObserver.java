package org.otalo.ao.client.search;

public interface EventObserver {

	/**
	 * Notifies the search query handler about any event performed for search
	 * @param searchProperty
	 * @param oldState
	 * @param newState
	 */
	public void appendIntoQueryQueue(String searchProperty, String latestState);
	
	/**
	 * Removes from search query queue
	 * @param searchProperty
	 */
	public void removeFromQueryQueue(String searchProperty);
	
	/**
	 * Resets the paging info
	 */
	public void resetPagingInformation();
}
