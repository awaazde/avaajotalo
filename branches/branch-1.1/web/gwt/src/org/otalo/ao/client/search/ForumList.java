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

import java.util.List;

import org.otalo.ao.client.JSONRequest;
import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.JSONRequester;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.JSOModel;

import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.ListBox;

/**
 * @author nikhil
 *
 */
public class ForumList extends Composite {

	private ListBox forumsList;
	private EventObserver notifier; //this notifier will be notified in case of any change in any of the filter criteria.
	
	public ForumList(EventObserver notifier) {
		forumsList = new ListBox();
		forumsList.addStyleName("dropdown-select");
		forumsList.addChangeHandler(new ForumsChangeHandler());
		fillForumData();
		this.notifier = notifier;
		initWidget(forumsList);
	}

	public ForumList(EventObserver notifier, boolean isMultiSelect) {
		forumsList = new ListBox(isMultiSelect);
		forumsList.addStyleName("dropdown-select");
		forumsList.addChangeHandler(new ForumsChangeHandler());
		fillForumData();
		this.notifier = notifier;
		initWidget(forumsList);
	}
	
	public void reset() {
		fillForumData();
	}
	
	private void fillForumData() {
		JSONRequest request	 = new JSONRequest();
		request.doFetchURL(AoAPI.FORUM, new ForumDataRequester());
	}
	
	
	private class ForumsChangeHandler implements ChangeHandler {
		@Override
		public void onChange(ChangeEvent event) {
			ListBox sender = (ListBox) event.getSource();
			String selectedForum = sender.getValue(sender.getSelectedIndex());
			if(AoAPI.SearchConstants.FORUM_ANY.equalsIgnoreCase(selectedForum)) {
				notifier.appendIntoQueryQueue(AoAPI.SearchConstants.FORUM, "");
			}
			else {
				notifier.appendIntoQueryQueue(AoAPI.SearchConstants.FORUM, selectedForum);
			}
		}
		
	}
	
	/**
	 * Tag requester class
	 * @author nikhil
	 *
	 */
	private class ForumDataRequester implements JSONRequester {
		public ForumDataRequester() {
		}
		public void dataReceived(List<JSOModel> models) {
			//clearing tag input
			forumsList.clear();
			forumsList.addItem("Any", "forum_any");
			
			Forum f;
			for (JSOModel model : models) {
				f = new Forum(model);
				forumsList.addItem(f.getName(), f.getName());
			}
		}
	}
}
