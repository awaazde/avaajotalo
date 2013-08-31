/*
 * Copyright (c) 2013 Awaaz.De Infosystem Pvt Ltd.
 *  
 */
package org.otalo.ao.client;

import java.util.List;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.MessageForum;
import org.otalo.ao.client.model.Tag;

import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.Label;
import com.watopi.chosen.client.ChosenOptions;
import com.watopi.chosen.client.gwt.ChosenListBox;

/**
 * @author nikhil
 * This is class which provides an auto complete kind of tag widget
 */
public class AOAutoCompleteTagWidget extends TagWidget{

	private Hidden tagsChanged;
	private MessageForum mf;
	private ChosenListBox tagInput;
	
	public AOAutoCompleteTagWidget() {
		ChosenOptions options = new ChosenOptions();
		options.setPlaceholderTextSingle("Select a tag...");
		options.setPlaceholderTextMultiple("Select tags...");
		options.setAllowSingleDeselect(true);
		options.setSingleBackstrokeDelete(true);
		options.setHideNoResult(true);
		options.setAddNewOptionVal(true);

		tagInput = new ChosenListBox(true, options);
		tagInput.setWidth("390px");
		tagInput.setHeight("25px");

		tagInput.setName("tags");
				
		Label tagLabel = new Label("Tags");
		tagsChanged = new Hidden("tags_changed", "");

		FlexTable tagTable = new FlexTable();
		tagTable.setWidget(0, 0, tagLabel);
		tagTable.setWidget(0, 1, tagInput);
		tagTable.setWidget(1, 0, tagsChanged);
		initWidget(tagTable);
	}

	@Override
	public void loadTags(MessageForum messageForum) {
		mf = messageForum;
		JSONRequest request = new JSONRequest();
		String tagSourceURL = AoAPI.TAGS + mf.getForum().getId(); // + "/?type=" + AoAPI.TAG_TYPE_CROP + " " + AoAPI.TAG_TYPE_TOPIC;
		request.doFetchURL(tagSourceURL, new TagRequestor());
	}	

	@Override
	public void reset() {
		tagsChanged.setValue("");
		tagInput.clear();
	}
	
	@Override
	public void setSelectedTagData() {
		String selectedTags = "";
		String [] tagVals = tagInput.getValues();
		for(int i=0;i<tagVals.length;i++) {
			selectedTags += tagVals[i] + "##";
		}
		if(selectedTags.length() > 0)
			selectedTags = selectedTags.substring(0, selectedTags.length()-2);
		tagsChanged.setValue(selectedTags);
	}

	/**
	 * Tag requester class
	 * @author nikhil
	 *
	 */
	private class TagRequestor implements JSONRequester {		 
		public void dataReceived(List<JSOModel> models) {
			Tag t;
			//clearing tag input
			tagInput.clear();
			
			for (JSOModel model : models) {
				t = new Tag(model);
				tagInput.addItem(t.getTag(), t.getTag());
			}
			//updating the tag input
			tagInput.update();

			// now that tags have been loaded,
			// check which have been selected
			loadSelectedTags(mf);
			//
			if(tagInput.getItemCount() > 0)
				Messages.get().setTagable(true);
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
			for (JSOModel model : models) {
				t = new Tag(model);
				for (int i=0; i<tagInput.getItemCount(); i++) {
			  		if (t.getTag().equals(tagInput.getValue(i)))
			  			tagInput.setItemSelected(i, true);
			  	}
			}
			tagInput.update();
		}
	}
}
