package org.otalo.ao.client.search;

public interface EventObserver {

	/**
	 * Notifies the search query handler about any event performed for search
	 * @param searchProperty
	 * @param oldState
	 * @param newState
	 */
	public void notifyQueryChangeListener(String searchProperty, String latestState);
	
	/**
	 * Resets the paging info
	 */
	public void resetPagingInformation();
}
