package org.otalo.ao.client;

import java.util.List;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.MessageForum;
import org.otalo.ao.client.model.MessageTag;
import org.otalo.ao.client.model.Tag;

import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;

public class AOTagWidget extends TagWidget {
	private ListBox crop, topic;
	private boolean tagged;
	
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
		
		FlexTable tagTable = new FlexTable();
		tagTable.setWidget(0, 0, cropLabel);
		tagTable.setWidget(0, 1, crop);
		tagTable.setWidget(1, 0, topicLabel);
		tagTable.setWidget(1, 1, topic);
		
		initWidget(tagTable);
		loadTags();
	}
	
	public String getErrorText() {
		String errorText = null;
		if (!tagged)
			errorText = "Please choose and save a crop and/or topic for this message";
		
		return errorText;
	}
	
	private void loadTags()
	{
		JSONRequest request = new JSONRequest();
	    request.doFetchURL(AoAPI.TAGS + "?type=" + AoAPI.TAG_TYPE_CROP + " " + AoAPI.TAG_TYPE_TOPIC, new TagRequestor());
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

		}
	 }
	 
	public void loadSelectedTags(MessageForum messageForum) {		
		JSONRequest request = new JSONRequest();
	    request.doFetchURL(AoAPI.MESSAGE_TAGS + messageForum.getId() + "/", new MessageTagRequestor());
	}
	
	 private class MessageTagRequestor implements JSONRequester {
		 
			public void dataReceived(List<JSOModel> models) {
				// pre-select the tags previously selected for this message
				MessageTag mt;
				tagged = false;
				
				for (JSOModel model : models)
			  	{
			  		tagged = true;
					mt = new MessageTag(model);
			  		Tag t = mt.getTag();
			  		
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
		 crop.setSelectedIndex(0);
		 topic.setSelectedIndex(0);
	}


}
