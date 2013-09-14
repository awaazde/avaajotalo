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

import org.otalo.ao.client.AutoCompleteTagWidget;
import org.otalo.ao.client.widget.chlist.event.ChosenChangeEvent;
import org.otalo.ao.client.widget.chlist.event.ChosenChangeEvent.ChosenChangeHandler;

/**
 * @author nikhil
 *
 */
public class SearchTagWidget extends AutoCompleteTagWidget {

	private EventObserver notifier; //notifies when any tag is selected
	
	public SearchTagWidget(boolean isShowLabel, boolean isEditable, EventObserver notifier) {
		super(isShowLabel, isEditable);
		this.notifier = notifier;
		this.tagInput.addChosenChangeHandler(new TagChosenChangeHandler());
	}
	
	private class TagChosenChangeHandler implements ChosenChangeHandler {
		@Override
		public void onChange(ChosenChangeEvent event) {
			setSelectedTagData();
			notifier.notifyQueryChangeListener("tags", selectedTags.getValue());
		}
	}
}
