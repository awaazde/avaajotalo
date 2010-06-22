/*
 * Copyright (c) 2009 Regents of the University of California, Stanford University, and others
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

package org.otalo.ao.client;

import java.util.List;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.MessageForum;
import org.otalo.ao.client.model.MessageResponder;
import org.otalo.ao.client.model.User;
import org.otalo.ao.client.model.Message.MessageStatus;

import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.VerticalPanel;

public class AORoutingWidget extends RoutingWidget {
	private MessageForum mf;
	private ListBox responders = new ListBox(true);
	private VerticalPanel routeTable = new VerticalPanel();
	private Hidden respondersChanged = new Hidden("responders_changed", "0");
	
	public AORoutingWidget()
	{
		Label title = new Label("Assigned Responders:");
		routeTable.add(title);
		responders.setName("responders");
		responders.addChangeHandler(new ChangeHandler() {
			public void onChange(ChangeEvent event) {
				respondersChanged.setValue("1");
			}
		});
		routeTable.add(respondersChanged);
		responders.setVisibleItemCount(5);
		routeTable.add(responders);
		initWidget(routeTable);
	}
	
	public void loadResponders(MessageForum messageForum)
	{
		mf = messageForum;
		responders.setEnabled(true);
		
		// load up responders for this forum
		JSONRequest request = new JSONRequest();
	    request.doFetchURL(AoAPI.RESPONDERS + mf.getForum().getId() + "/", new ResponderRequestor());
	}
	
	private class ResponderRequestor implements JSONRequester {
		 
		public void dataReceived(List<JSOModel> models) {
			User u;
			
			for (JSOModel model : models)
		  	{
				u = new User(model);
		  		responders.addItem(u.getName(), u.getId());
		  	}
			
			// now that responders have been loaded,
			// check which have been assigned
			loadSelectedResponders(mf);

		}
	 }
	 
	private void loadSelectedResponders(MessageForum messageForum)
	{
		JSONRequest request = new JSONRequest();
	    request.doFetchURL(AoAPI.MESSAGE_RESPONDERS + mf.getId() + "/", new MessageResponderRequestor());
	}
	
	private class MessageResponderRequestor implements JSONRequester {
		 
		public void dataReceived(List<JSOModel> models) 
		{
			MessageResponder ms;
			int idx = 0;
			
			for (JSOModel model : models)
		  	{
				ms = new MessageResponder(model);
		  		User responder = ms.getResponder();
		  		for (int i=0; i < responders.getItemCount(); i++)
		  		{
		  			if (responders.getValue(i).equals(responder.getId()))
		  			{
		  				responders.setItemSelected(i, true);
		  			}
		  		}
		  	}
		}
	}
	
	public void reset()
	{
		responders.setEnabled(false);
		responders.clear();
		respondersChanged.setValue("0");
	}
}
