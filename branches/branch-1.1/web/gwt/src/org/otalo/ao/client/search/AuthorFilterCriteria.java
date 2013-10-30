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
public class AuthorFilterCriteria extends Composite implements ClickHandler{

	private CheckBox any;
	private CheckBox name;
	private CheckBox number;
	private CheckBox district;
	private CheckBox taluka;
	private CheckBox village;
	
	private CustomStringBuilder selectedFieldsQuery; 
	
	/**
	 * Constructs new author criteria panel
	 * @param notifier 
	 */
	public AuthorFilterCriteria() {
		any 		= new CheckBox("All");
		name 		= new CheckBox("Name");
		number 	= new CheckBox("Number");
		district 	= new CheckBox("District");
		taluka 	= new CheckBox("Taluka");
		village 	= new CheckBox("Village");
		
		any.setName(AoAPI.SearchConstants.AuthorConstants.ANY);
		name.setName(AoAPI.SearchConstants.AuthorConstants.AUTHOR_NAME);
		number.setName(AoAPI.SearchConstants.AuthorConstants.AUTHOR_NUMBER);
		district.setName(AoAPI.SearchConstants.AuthorConstants.AUTHOR_DISTRICT);
		taluka.setName(AoAPI.SearchConstants.AuthorConstants.AUTHOR_TALUKA);
		village.setName(AoAPI.SearchConstants.AuthorConstants.AUTHOR_VILLAGE);
		
		any.addClickHandler(this);
		name.addClickHandler(this);
		number.addClickHandler(this);
		district.addClickHandler(this);
		taluka.addClickHandler(this);
		village.addClickHandler(this);
		
		selectedFieldsQuery = new CustomStringBuilder();
		
		FlexTable authorFieldTable = new FlexTable();
		authorFieldTable.setCellSpacing(8);
		authorFieldTable.setWidget(0, 0, any);
		authorFieldTable.setWidget(0, 1, name);
		authorFieldTable.setWidget(1, 0, number);
		authorFieldTable.setWidget(1, 1, district);
		authorFieldTable.setWidget(2, 0, taluka);
		authorFieldTable.setWidget(2, 1, village);
		
		any.setValue(true);
		setResetAny();
		
		authorFieldTable.addStyleName("author-filter");
		initWidget(authorFieldTable);
	}
	
	public void reset() {
		any.setValue(true);
		setResetAny();
		selectedFieldsQuery = new CustomStringBuilder();
	}
	
	public String getSelectedValue() {
		return selectedFieldsQuery.toString();
	}
	
	private void setResetAny() {
		if(any.getValue()) {
			name.setValue(false);
			number.setValue(false);
			district.setValue(false);
			taluka.setValue(false);
			village.setValue(false);
		}
		//now disabling everything
		name.setEnabled(!any.getValue());
		district.setEnabled(!any.getValue());
		number.setEnabled(!any.getValue());
		taluka.setEnabled(!any.getValue());
		village.setEnabled(!any.getValue());
	}
	
	
	@Override
	public void onClick(ClickEvent event) {
		CheckBox sender = (CheckBox) event.getSource();
		if(AoAPI.SearchConstants.AuthorConstants.ANY.equalsIgnoreCase(sender.getName())) {
			//if its any then first disable all others and removing all of them from selected status queue
			setResetAny();
			selectedFieldsQuery.clear();
		}
		else {
			if(sender.getValue())
				selectedFieldsQuery.add(sender.getName());
			else
				selectedFieldsQuery.remove(sender.getName());
		}
	}
}
