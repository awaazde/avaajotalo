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
import org.otalo.ao.client.widget.chlist.client.ChosenOptions;
import org.otalo.ao.client.widget.chlist.gwt.ChosenListBox;

import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.Label;

/**
 * @author nikhil
 * This is class which provides an auto complete kind of tag widget
 */
public class AutoCompleteTagWidget extends TagWidget{

	/*
	 * This is separator for all the selected tags. On server side, value for selectedTags is splitted using this.
	 */
	public static final String TAG_SEPERATOR = "##";
	protected Hidden selectedTags;
	private MessageForum mf;
	protected ChosenListBox tagInput;
	
	public AutoCompleteTagWidget(boolean isShowLabel, boolean isEditable) {
		ChosenOptions options = new ChosenOptions();
		options.setPlaceholderTextSingle("Select a tag...");
		options.setPlaceholderTextMultiple("Begin typing here »");
		options.setAllowSingleDeselect(true);
		options.setSingleBackstrokeDelete(true);
		options.setHideNoResult(true);
		options.setAddNewOptionVal(isEditable);
		options.setSearchContains(true);

		tagInput = new ChosenListBox(true, options);
		tagInput.setWidth("390px");
		tagInput.setHeight("25px");

		tagInput.setName("tags");
		
		selectedTags = new Hidden("selected_tags", "");

		FlexTable tagTable = new FlexTable();
		if(isShowLabel) {
			Label tagLabel = new Label("Tags");
			tagTable.setWidget(0, 0, tagLabel);
			tagTable.setWidget(0, 1, tagInput);
		}
		else {
			tagTable.setWidget(0, 0, tagInput);
		}
		tagTable.setWidget(1, 0, selectedTags);
		
		initWidget(tagTable);
	}

	@Override
	public void loadTags(MessageForum messageForum) {
		mf = messageForum;
		JSONRequest request = new JSONRequest();
		String tagSourceURL = AoAPI.TAGS;
		if(mf != null)
			tagSourceURL+= mf.getForum().getId();
		request.doFetchURL(tagSourceURL, new TagRequestor());
	}	

	@Override
	public void reset() {
		selectedTags.setValue("");
		tagInput.clear();
	}
	
	@Override
	public void setSelectedTagData() {
		String selectedTagsStr = "";
		String [] tagVals = tagInput.getValues();
		for(int i=0;i<tagVals.length;i++) {
			selectedTagsStr += tagVals[i] + TAG_SEPERATOR;
		}
		if(selectedTagsStr.length() > 0)
			selectedTagsStr = selectedTagsStr.substring(0, selectedTagsStr.length()-2);
		selectedTags.setValue(selectedTagsStr);
	}
	
	public void setHeight(String heightStyleTxt) {
		if(heightStyleTxt == null || heightStyleTxt.isEmpty())
			tagInput.setHeight("25px");
		else
			tagInput.setHeight(heightStyleTxt);
	}
	
	public void setWidth(String widthStyleTxt) {
		if(widthStyleTxt == null || widthStyleTxt.isEmpty())
			tagInput.setWidth("390px");
		else
			tagInput.setWidth(widthStyleTxt);
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
			if(mf != null)
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
