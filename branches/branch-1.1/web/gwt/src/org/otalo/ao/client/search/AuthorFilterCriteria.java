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
public class AuthorFilterCriteria extends Composite{

	private CheckBox name;
	private CheckBox number;
	private CheckBox district;
	private CheckBox taluka;
	private CheckBox village;
	
	private CustomStringBuilder selectedStatusQuery; 
	private EventObserver notifier; //this notifier will be notified in case of any change in any of the filter criteria.
	
	/**
	 * Constructs new author criteria panel
	 * @param notifier 
	 */
	public AuthorFilterCriteria(EventObserver notifier) {
		this.name 		= new CheckBox("Name");
		this.number 	= new CheckBox("Number");
		this.district 	= new CheckBox("District");
		this.taluka 	= new CheckBox("Taluka");
		this.village 	= new CheckBox("Village");
		
		this.name.setName("Name");
		this.number.setName("Number");
		this.district.setName("District");
		this.taluka.setName("Taluka");
		this.village.setName("Village");
		
		this.name.addClickHandler(new CheckBoxClickHandler());
		this.number.addClickHandler(new CheckBoxClickHandler());
		this.district.addClickHandler(new CheckBoxClickHandler());
		this.taluka.addClickHandler(new CheckBoxClickHandler());
		this.village.addClickHandler(new CheckBoxClickHandler());
		
		this.notifier = notifier;
		this.selectedStatusQuery = new CustomStringBuilder();
		
		FlexTable authorFieldTable = new FlexTable();
		authorFieldTable.setWidget(0, 0, name);
		authorFieldTable.setWidget(1, 0, number);
		authorFieldTable.setWidget(2, 0, district);
		authorFieldTable.setWidget(3, 0, taluka);
		authorFieldTable.setWidget(4, 0, village);
		authorFieldTable.addStyleName("author-filter");
		initWidget(authorFieldTable);
	}

	
	private class CheckBoxClickHandler implements ClickHandler {
		@Override
		public void onClick(ClickEvent event) {
			CheckBox sender = (CheckBox) event.getSource();
			if(sender.getValue())
				selectedStatusQuery.add(sender.getName());
			else
				selectedStatusQuery.remove(sender.getName());
			notifier.notifyQueryChangeListener("author", selectedStatusQuery.toString());
		}	
	}
}
