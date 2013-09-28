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
import org.otalo.ao.client.model.Tag;

import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;

/**
 * This class is deprecated now. Use AutoCompleteTagWidget class instead of this.
 *
 */
@Deprecated
public class AOTagWidget extends TagWidget {
	private ListBox crop, topic;
	private Hidden tagsChanged;
	private MessageForum mf;
	
	public AOTagWidget()
	{
		crop = new ListBox();
		topic = new ListBox();
		
		crop.setName("crop");
		topic.setName("topic");
		
		crop.addItem("", "-1");
		topic.addItem("", "-1");
		
		Label cropLabel = new Label("Crop");
		Label topicLabel = new Label("Topic");
		
		tagsChanged = new Hidden("tags_changed", "0");
		crop.addChangeHandler(new TopicChangedHandler());
		topic.addChangeHandler(new TopicChangedHandler());
		
		FlexTable tagTable = new FlexTable();
		tagTable.setWidget(0, 0, cropLabel);
		tagTable.setWidget(0, 1, crop);
		tagTable.setWidget(1, 0, topicLabel);
		tagTable.setWidget(1, 1, topic);
		tagTable.setWidget(2, 0, tagsChanged);
		
		initWidget(tagTable);
	}
	
	private class TopicChangedHandler implements ChangeHandler {

		public void onChange(ChangeEvent event) {
			tagsChanged.setValue("1");	
		}
		
	}
	
	public void loadTags(MessageForum messageForum)
	{
		mf = messageForum;
		
		JSONRequest request = new JSONRequest();
	    request.doFetchURL(AoAPI.TAGS + mf.getForum().getId() + "/?type=" + AoAPI.TAG_TYPE_CROP + " " + AoAPI.TAG_TYPE_TOPIC, new TagRequestor());
	}
	
	 private class TagRequestor implements JSONRequester {
		 
		public void dataReceived(List<JSOModel> models) {
			Tag t;
			
			for (JSOModel model : models)
		  	{
				t = new Tag(model);
		  		if (t.getType().equals(AoAPI.TAG_TYPE_CROP))
		  			crop.addItem(t.getTag(), t.getId());
		  		else if (t.getType().equals(AoAPI.TAG_TYPE_TOPIC))
		  			topic.addItem(t.getTag(), t.getId());
		  	}
			
			// now that tags have been loaded,
			// check which have been selected
			loadSelectedTags(mf);
			
			// now that tags have been loaded,
			// set the widget in details accordingly
			if (crop.getItemCount() + topic.getItemCount() > 2)
			{
				Messages.get().setTagable(true);
			}
			else
			{
				Messages.get().setTagable(false);
			}

		}
	 }
	 
	private void loadSelectedTags(MessageForum messageForum) {		
		JSONRequest request = new JSONRequest();
	    request.doFetchURL(AoAPI.MESSAGE_TAGS + messageForum.getId() + "/", new MessageTagRequestor());
	}
	
	 private class MessageTagRequestor implements JSONRequester {
		 
			public void dataReceived(List<JSOModel> models) {
				// pre-select the tags previously selected for this message
				Tag t;
				
				for (JSOModel model : models)
			  	{
					t = new Tag(model);
			  		
			  		if (t.getType().equals(AoAPI.TAG_TYPE_CROP))
			  		{
			  			for (int i=0; i<crop.getItemCount(); i++)
			  			{
			  				if (t.getId().equals(crop.getValue(i)))
			  				{
			  					crop.setSelectedIndex(i);
			  				}
			  			}
			  		}
			  		else if (t.getType().equals(AoAPI.TAG_TYPE_TOPIC))
			  		{
			  			for (int i=0; i<topic.getItemCount(); i++)
			  			{
			  				if (t.getId().equals(topic.getValue(i)))
			  				{
			  					topic.setSelectedIndex(i);
			  				}
			  			}
			  		}
			  		
			  	}
			}
		 }
	
	public void reset()
	{
		crop.clear();
		topic.clear();
		crop.addItem("", "-1");
		topic.addItem("", "-1");
		tagsChanged.setValue("0");
		 
	}
	
	public void setSelectedTagData() {
		//nothing to do here
	}
}
