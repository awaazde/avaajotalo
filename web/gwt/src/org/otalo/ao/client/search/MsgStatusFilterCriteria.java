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
import com.google.gwt.user.client.ui.FlexTable;

/**
 * @author nikhil
 *
 */
public class MsgStatusFilterCriteria extends Composite implements ClickHandler {

	private CheckBox any;
	private CheckBox inbox;
	private CheckBox approved;
	private CheckBox rejected;
	private CheckBox responses;
	
	private CustomStringBuilder selectedStatusQuery; 
	/**
	 * Constructs new author criteria panel
	 */
	public MsgStatusFilterCriteria() {
		any 		= new CheckBox("Any");
		inbox 		= new CheckBox("Inbox");
		approved 	= new CheckBox("Approved");
		rejected 	= new CheckBox("Rejected");
		responses 	= new CheckBox("Responses");
		
		any.setName(AoAPI.SearchConstants.StausConstants.STATUS_ANY);
		inbox.setName(AoAPI.SearchConstants.StausConstants.STATUS_INPUT);
		approved.setName(AoAPI.SearchConstants.StausConstants.STATUS_APPROVED);
		rejected.setName(AoAPI.SearchConstants.StausConstants.STATUS_REJECTED);
		responses.setName(AoAPI.SearchConstants.StausConstants.STATUS_RESPONDED);
		
		any.addClickHandler(this);
		inbox.addClickHandler(this);
		approved.addClickHandler(this);
		rejected.addClickHandler(this);
		responses.addClickHandler(this);
		
		FlexTable fieldGrid = new FlexTable();
		fieldGrid.setCellSpacing(8);
		fieldGrid.setWidget(0, 0, any);
		fieldGrid.getFlexCellFormatter().setColSpan(0, 0, 2);
		fieldGrid.setWidget(1, 0, inbox);
		fieldGrid.setWidget(1, 1, approved);
		fieldGrid.setWidget(2, 0, rejected);
		fieldGrid.setWidget(2, 1, responses);
		fieldGrid.addStyleName("status-filter");
		any.setValue(true);
		setResetAny();
		
		initWidget(fieldGrid);
		
		selectedStatusQuery = new CustomStringBuilder();
	}
	
	public void reset() {
		any.setValue(true);
		setResetAny();
		selectedStatusQuery = new CustomStringBuilder();
	}
	
	public String getSelectedValue() {
		return selectedStatusQuery.toString();
	}
	
	@Override
	public void onClick(ClickEvent event) {
		CheckBox sender = (CheckBox) event.getSource();
		if(AoAPI.SearchConstants.StausConstants.STATUS_ANY.equalsIgnoreCase(sender.getName())) {
			//if its any then first disable all others and removing all of them from selected status queue
			setResetAny();
			selectedStatusQuery.clear();
		}
		else {
			if(sender.getValue())
				selectedStatusQuery.add(sender.getName());
			else
				selectedStatusQuery.remove(sender.getName());		
		}
	}
	
	private void setResetAny() {
		if(any.getValue()) {
			inbox.setValue(false);
			approved.setValue(false);
			rejected.setValue(false);
			responses.setValue(false);
		}
		inbox.setEnabled(!any.getValue());
		approved.setEnabled(!any.getValue());
		rejected.setEnabled(!any.getValue());
		responses.setEnabled(!any.getValue());
	}
}
