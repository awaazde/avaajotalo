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

import java.util.Iterator;
import java.util.List;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.MessageForum;
import org.otalo.ao.client.model.MessageResponder;
import org.otalo.ao.client.model.Tag;
import org.otalo.ao.client.model.User;
import org.otalo.ao.client.model.Message.MessageStatus;

import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class AORoutingWidget extends RoutingWidget {
	private MessageForum mf;
	private CheckBox routeEnabled = new CheckBox("Call Automatically");
	private VerticalPanel routeTable = new VerticalPanel();
	
	public AORoutingWidget()
	{
		routeEnabled.setText("Call Automatically");
		routeEnabled.setName("routeEnabled");
		routeTable.add(routeEnabled);
		initWidget(routeTable);
	}
	
	public void loadRoutingInfo(MessageForum messageForum)
	{
		mf = messageForum;
		
		if (!messageForum.isResponse())
		{
			// Check to see if checkbox should be enabled and checked.
			// First thing is to check if this message has been tagged
			JSONRequest request = new JSONRequest();
		    request.doFetchURL(AoAPI.MESSAGE_TAGS + mf.getId() + "/", new MessageTagRequestor());
		}
	}
	
	 private class MessageTagRequestor implements JSONRequester {
		 
			public void dataReceived(List<JSOModel> models) 
			{
				if (models.size() > 0)
				{
					// This message has been tagged, so proceed to check
					// if it has been assigned responders
					loadResponders();
				}
			}
	 }
	 
	private void loadResponders()
	{
		if (mf.getStatus() == MessageStatus.PENDING || mf.getStatus() == MessageStatus.APPROVED)
		{
			routeEnabled.setEnabled(true);
			// get responders
			JSONRequest request = new JSONRequest();
		    request.doFetchURL(AoAPI.MESSAGE_RESPONDERS + mf.getId() + "/", new MessageResponderRequestor());
		}
	}
	
	private class MessageResponderRequestor implements JSONRequester {
		 
		public void dataReceived(List<JSOModel> models) 
		{
			if (models.size() > 0) routeEnabled.setValue(true);
			MessageResponder ms;
			int idx = 0;
			
			for (JSOModel model : models)
		  	{
				ms = new MessageResponder(model);
		  		User responder = ms.getResponder();
		  		String label = responder.getName().equals("null") ? responder.getNumber() : responder.getName();
		  		
		  		routeTable.add(new Label(label));
		  		routeTable.add(new Hidden("responder"+idx++, responder.getId()));	
		  	}
		}
	}
	
	public void reset()
	{
		routeEnabled.setEnabled(false);
		routeEnabled.setValue(false);
		for (Iterator<Widget> iter = routeTable.iterator(); iter.hasNext();)
		{
			if (!iter.next().equals(routeEnabled))
			{
				iter.remove();
			}
		}
	}
}
