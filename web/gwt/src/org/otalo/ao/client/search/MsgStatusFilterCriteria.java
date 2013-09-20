/**
  * Copyright (c) 2013 Regents of the University of California, Stanford University, and others
 * 
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 * 
 * http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */
package org.otalo.ao.client.search;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.util.CustomStringBuilder;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Grid;

/**
 * @author nikhil
 *
 */
public class MsgStatusFilterCriteria extends Composite {

	private CheckBox inbox;
	private CheckBox approved;
	private CheckBox rejected;
	private CheckBox responsed;
	
	private CustomStringBuilder selectedStatusQuery; 
	private EventObserver notifier; //this notifier will be notified in case of any change in any of the filter criteria.
	/**
	 * Constructs new author criteria panel
	 */
	public MsgStatusFilterCriteria(EventObserver notifier) {
		this.inbox 		= new CheckBox("Inbox");
		this.approved 	= new CheckBox("Approved");
		this.rejected 	= new CheckBox("Rejected");
		this.responsed 	= new CheckBox("Responsed");
		this.inbox.setName(AoAPI.SearchConstants.StausConstants.STATUS_INPUT);
		this.approved.setName(AoAPI.SearchConstants.StausConstants.STATUS_APPROVED);
		this.rejected.setName(AoAPI.SearchConstants.StausConstants.STATUS_REJECTED);
		this.responsed.setName(AoAPI.SearchConstants.StausConstants.STATUS_RESPONDED);
		this.inbox.addClickHandler(new CheckBoxClickHandler());
		this.approved.addClickHandler(new CheckBoxClickHandler());
		this.rejected.addClickHandler(new CheckBoxClickHandler());
		this.responsed.addClickHandler(new CheckBoxClickHandler());
		
		Grid fieldGrid = new Grid(4,1);
		fieldGrid.setWidget(0, 0, inbox);
		fieldGrid.setWidget(1, 0, approved);
		fieldGrid.setWidget(2, 0, rejected);
		fieldGrid.setWidget(3, 0, responsed);
		fieldGrid.addStyleName("status-filter");
		initWidget(fieldGrid);
		
		this.notifier = notifier;
		this.selectedStatusQuery = new CustomStringBuilder();
	}
	
	public void reset() {
		this.approved.setValue(false);
		this.inbox.setValue(false);
		this.rejected.setValue(false);
		this.responsed.setValue(false);
	}
	
	private class CheckBoxClickHandler implements ClickHandler {
		@Override
		public void onClick(ClickEvent event) {
			CheckBox sender = (CheckBox) event.getSource();
			if(sender.getValue())
				selectedStatusQuery.add(sender.getName());
			else
				selectedStatusQuery.remove(sender.getName());
			notifier.resetPagingInformation();
			notifier.notifyQueryChangeListener(AoAPI.SearchConstants.STATUS, selectedStatusQuery.toString());
		}	
	}
}
