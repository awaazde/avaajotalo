/*
 * Copyright 2007 Google Inc.
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

import java.util.ArrayList;
import java.util.List;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.model.BaseModel;
import org.otalo.ao.client.model.Call;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.Message.MessageStatus;
import org.otalo.ao.client.model.MessageForum;
import org.otalo.ao.client.model.Prompt;
import org.otalo.ao.client.model.Subject;
import org.otalo.ao.client.model.SurveyInput;
import org.otalo.ao.client.model.User;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.shared.HandlerRegistration;
import com.google.gwt.resources.client.ClientBundle;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HTMLTable.Cell;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.HorizontalPanel;

/**
 * A composite that displays voice messages.
 */
public class MessageList extends Composite implements ClickHandler, JSONRequester {

	/*
	 * This variable should be consistent with otalo/views.py
	 */
  private static final int VISIBLE_MESSAGE_COUNT = 10;

  private HTML countLabel = new HTML();
  private HTML newerButton = new HTML("<a href='javascript:;'>&lt; newer</a>",
      true);
  private HTML olderButton = new HTML("<a href='javascript:;'>older &gt;</a>",
      true);
  private HandlerRegistration newButtonReg=null, oldButtonReg=null;
  private int startIndex, count, selectedRow = -1;
  private FlexTable table = new FlexTable();
  private FormPanel detailsForm = new FormPanel();
  private HorizontalPanel navBar = new HorizontalPanel();
  private List<BaseModel> messages = new ArrayList<BaseModel>();
  private BaseModel selectMessage;
  private Forum forum;
  private Hidden messageForumId;
  private Images images;
  
  /**
   * Specifies the images that will be bundled for this Composite and specify
   * that tree's images should also be included in the same bundle.
   */
  public interface Images extends ClientBundle {
    ImageResource approve();
    
    ImageResource reject();
  }

  public MessageList(Images images) {
  	this.images = images;
  	
  	detailsForm.setWidget(table);
  	detailsForm.setMethod(FormPanel.METHOD_POST);
  	detailsForm.addSubmitCompleteHandler(new MessageStatusUpdated());

  	// Setup the table.
    table.setCellSpacing(0);
    table.setCellPadding(0);
    table.setWidth("100%");

    // Hook up events.
    table.addClickHandler(this);

    // Create the 'navigation' bar at the upper-right.
    HorizontalPanel innerNavBar = new HorizontalPanel();
    navBar.setStyleName("mail-ListNavBar");
    innerNavBar.add(newerButton);
    innerNavBar.add(countLabel);
    innerNavBar.add(olderButton);

    navBar.setHorizontalAlignment(HorizontalPanel.ALIGN_RIGHT);
    navBar.add(innerNavBar);
    navBar.setWidth("100%");

    initWidget(detailsForm);
    setStyleName("mail-List");

    initTable();
  }

  public void onClick(ClickEvent event) {
    Object sender = event.getSource();
	  // Select the row that was clicked (-1 to account for header row).
	  Cell cell = table.getCellForEvent(event);
	  if (cell != null) {
	    int row = cell.getRowIndex();
	    if (row > 0) {
	      selectRow(row - 1);
	    }
	  }
  }

  /**
   * Initializes the table so that it contains enough rows for a full page of
   * messages. Also creates the images that will be used as 'read' flags.
   */
  private void initTable() {
    // Create the header row.
    table.setText(0, 0, "Date");
    table.setText(0, 1, "User");
    table.setText(0, 2, "Message");
    table.setWidget(0, 3, navBar);
    table.getFlexCellFormatter().setColSpan(0, 3, 2);
    table.getRowFormatter().setStyleName(0, "mail-ListHeader");

    // Initialize the rest of the rows.
    for (int i = 0; i < VISIBLE_MESSAGE_COUNT; ++i) {
      table.setText(i + 1, 0, "");
      table.setText(i + 1, 1, "");
      table.setText(i + 1, 2, "");
      table.setText(i + 1, 3, "");
      table.setText(i + 1, 4, "");
      table.getCellFormatter().setWordWrap(i + 1, 0, false);
      table.getCellFormatter().setWordWrap(i + 1, 1, false);
      table.getCellFormatter().setWordWrap(i + 1, 2, false);
    }
  }

  /**
   * Selects the given row (relative to the current page).
   * 
   * @param row the row to be selected
   */
  private void selectRow(int row) {
    // When a row (other than the first one, which is used as a header) is
    // selected, display its associated details.
    if (messages.size() <= row || messages.get(row) == null) {
      return;
    }
    
    styleRow(selectedRow, false);
    styleRow(row, true);

    // TODO
    //message.read = true;
    selectedRow = row;

    BaseModel message = messages.get(row);
    if (MessageForum.isMessageForum(message))
    	Messages.get().setItem(new MessageForum(message));
  }

  private void styleRow(int row, boolean selected) {
    if (row != -1) {
      if (selected) {
        table.getRowFormatter().addStyleName(row + 1, "mail-SelectedRow");
        BaseModel message = messages.get(row);
        String content = "";
        if (MessageForum.isMessageForum(message))
        	content = (new MessageForum(message)).getContent();
        else if (SurveyInput.isSurveyInput(message))
        {
        	content = (new SurveyInput(message)).getInput();
        }
        SoundWidget sound = new SoundWidget(content);
        table.setHTML(row + 1, 2, sound.getWidget().getHTML());
      } else {
        table.getRowFormatter().removeStyleName(row + 1, "mail-SelectedRow");
        table.clearCell(row + 1, 2);
      }
    }
  }

  private void update() {
    // Update the older/newer buttons & label.
    int max = startIndex + VISIBLE_MESSAGE_COUNT;
    if (max > count) {
      max = count;
    }
    
    newerButton.setVisible(startIndex != 0);
    olderButton.setVisible(startIndex + VISIBLE_MESSAGE_COUNT < count);
    
    if (newButtonReg != null) {newButtonReg.removeHandler(); newButtonReg = null;}
    if (oldButtonReg != null) {oldButtonReg.removeHandler(); oldButtonReg = null;}
   
    if (count > 0)
    {
	    BaseModel message = messages.get(0);
	    newButtonReg = newerButton.addClickHandler(new PageOverHandler("newer", message));
	    oldButtonReg = olderButton.addClickHandler(new PageOverHandler("older", message));

    }

    countLabel.setText("" + (startIndex + 1) + " - " + max + " of " + count);

    // Show the selected messages.
    int i = 0;
    for (; i < VISIBLE_MESSAGE_COUNT; ++i) {
    	// Don't read past the end.
      if (i >= messages.size()) {
        break;
      }
      
      BaseModel message = messages.get(i);
      
      if (MessageForum.isMessageForum(message))
      {
	      MessageForum mf = new MessageForum(message);
      	// Add a new row to the table, then set each of its columns
	      table.setText(i + 1, 0, mf.getDate());
	      User user = mf.getAuthor();
	      String callerText = ("".equals(user.getName()) || "null".equals(user.getName())) ? user.getNumber() : user.getName() + " (" + user.getNumber() + ")";
	      table.setText(i + 1, 1, callerText);
	      
	      if (forum != null && forum.moderated())
	      {
	    	  AbstractImagePrototype approveHTML = AbstractImagePrototype.create(images.approve());
	    	  HTML approveButton = new HTML(approveHTML.getHTML());
		      approveButton.addClickHandler(new MessageApproveHandler(AoAPI.APPROVE, mf));
		      
		      AbstractImagePrototype rejectHTML = AbstractImagePrototype.create(images.reject());
		      HTML rejectButton = new HTML(rejectHTML.getHTML());
		      rejectButton.addClickHandler(new MessageApproveHandler(AoAPI.REJECT, mf));
		      
		      switch (mf.getStatus()){
		      case APPROVED:
		        table.setWidget(i+1, 3, rejectButton);
		        table.setHTML(i+1, 4, "&nbsp");
		      	break;
		      case REJECTED:
		      	table.setWidget(i+1, 3, approveButton);
			    table.setHTML(i+1, 4, "&nbsp");
		      	break;
		      case PENDING:
		      	table.setWidget(i+1, 3, approveButton);
		      	table.setWidget(i+1, 4, rejectButton);
		      }
	      }
	      else
	      {
	      	table.setHTML(i+1, 3, "&nbsp");
	      	table.setHTML(i+1, 4, "&nbsp");
	      }
      }
      else if (SurveyInput.isSurveyInput(message))
      {
      	SurveyInput input = new SurveyInput(message);
        Call call = input.getCall();

        // Add a new row to the table, then set each of its columns
	      table.setText(i + 1, 0, call.getDate());
	      Subject subject = call.getSubject();
	      String callerText = ("".equals(subject.getName()) || "null".equals(subject.getName())) ? subject.getNumber() : subject.getName() + " (" + subject.getNumber() + ")";
	      table.setText(i + 1, 1, callerText);
	       
	     	// TODO: add download link
	      Anchor downloadLink = new Anchor("Download", AoAPI.DOWNLOAD_SURVEY_INPUT + input.getId());
	      table.setWidget(i+1, 3, downloadLink);
	      table.setHTML(i+1, 4, "&nbsp");
      }
    }

    // Clear any remaining slots.
    for (; i < VISIBLE_MESSAGE_COUNT; ++i) {
      table.setHTML(i + 1, 0, "&nbsp;");
      table.setHTML(i + 1, 1, "&nbsp;");
      table.setHTML(i + 1, 2, "&nbsp;");
      table.setHTML(i + 1, 3, "&nbsp;");
      table.setHTML(i + 1, 4, "&nbsp;");

    }
    // set the hidden field in the last row
    messageForumId = new Hidden("messageforumid");
    table.setWidget(VISIBLE_MESSAGE_COUNT+1, 0, messageForumId);
    
    // Select the first row if none is selected.
    if (selectedRow == -1 && count > 0) {
      selectRow(0);
    }
  }
  public void reset()
  {
		messages.clear();
		startIndex = 0;
		count = 0;
		styleRow(selectedRow, false);
		update();
  }
	public void displaySurveyInput(Prompt p, int start)
	{
		styleRow(selectedRow, false);
		JSONRequest request = new JSONRequest();
		request.doFetchURL(AoAPI.PROMPT_RESPONSES + p.getId() + "/?start=" + String.valueOf(start), this);
	}
  
  private class MessageApproveHandler implements ClickHandler {
  	private String action;
  	private MessageForum messageForum;
  	
  	MessageApproveHandler(String action, MessageForum messageForum)
  	{
  		this.action = action;
  		this.messageForum = messageForum;
  	}
		public void onClick(ClickEvent event) {
			// save to get the old status when we return
			selectMessage = messageForum;
			messageForumId.setValue(messageForum.getId());
			detailsForm.setAction(JSONRequest.BASE_URL + AoAPI.UPDATE_STATUS + action);
			detailsForm.submit();
			
		}
  	
  }
  
  private class MessageStatusUpdated implements SubmitCompleteHandler {
		
		public void onSubmitComplete(SubmitCompleteEvent event) {
			ConfirmDialog saved = new ConfirmDialog("Updated!");
			saved.show();
			saved.center();
			
			// call the dispatcher just so we can search
			// in the code
			MessageForum mf = new MessageForum(selectMessage);
			selectMessage = null;
			if (mf.isResponse() && mf.getStatus() != MessageStatus.PENDING)
			{
				// only from in the responses folder
				// do you not want to reload the folder
				// that you were originally in
				// (as specified by mf.getStatus())
				Messages.get().displayMessages(mf);
			}
			else
			{
				// reload this message's old home folder
				Messages.get().displayMessages(mf.getForum(), mf.getStatus(), startIndex);
			}
			
		}
	}
  
  public void getMessages(MessageForum m)
  {
  	selectMessage = m;
  	
  	if (m.isResponse() && m.getStatus() != MessageStatus.PENDING)
  	{
  		// call dispatcher in order to set forum widget
  		Messages.get().displayResponses(m);
  	}
  	else
  	{
  		ArrayList<MessageStatus> statuses = new ArrayList<MessageStatus>();
    	statuses.add(m.getStatus());
    	String filterParams = getFilterParams(statuses) + "&start=" + String.valueOf(startIndex) + "&messageforumid=" + m.getId();
  		getMessages(m.getForum(), filterParams);
  	}
  }
  
  public void getMessages(Forum f, MessageStatus status, int start)
  {
  	ArrayList<MessageStatus> statuses = new ArrayList<MessageStatus>();
  	statuses.add(status);
  	String filterParams = getFilterParams(statuses) + "&start=" + String.valueOf(start);
  	getMessages(f, filterParams);
  	
  }
  
  public void getResponses(MessageForum mf)
  {
  	ArrayList<MessageStatus> statuses = new ArrayList<MessageStatus>();
  	statuses.add(MessageStatus.APPROVED);
  	statuses.add(MessageStatus.REJECTED);
  	String filterParams = getFilterParams(statuses) + "&start=" + String.valueOf(startIndex) + "&messageforumid=" + mf.getId();
  	getMessages(mf.getForum(), filterParams);
  	
  }
  
  public void getResponses(Forum f, int start)
  {
  	ArrayList<MessageStatus> statuses = new ArrayList<MessageStatus>();
  	statuses.add(MessageStatus.APPROVED);
  	statuses.add(MessageStatus.REJECTED);
  	String filterParams = getFilterParams(statuses) + "&start=" + String.valueOf(start);
  	getMessages(f, filterParams);
  	
  }
  
  private String getFilterParams(List<MessageStatus> statuses)
  {
  	String filterParams = "/?status=";
  	for (MessageStatus status : statuses)
  	{
  		filterParams += status.ordinal() + " ";
  	}
  	
  	if (statuses.size() == 1 && (statuses.get(0) == MessageStatus.APPROVED || statuses.get(0) == MessageStatus.REJECTED) )
  	{
  		filterParams += "&posttype=" + AoAPI.POSTS_TOP;
  	}
  	else if (statuses.size() == 1 && statuses.get(0) == MessageStatus.PENDING)
  	{
  		filterParams += "&posttype=" + AoAPI.POSTS_ALL;
  	}
  	else
  	{
  		filterParams += "&posttype=" + AoAPI.POSTS_RESPONSES;
  	}
  	
  	return filterParams;
  }
  
  private void getMessages(Forum f, String filterParams)
  {
  	styleRow(selectedRow, false);
  	String forumId = f.getId();
  	JSONRequest request = new JSONRequest();
  	request.doFetchURL(AoAPI.MESSAGES + forumId + filterParams, this);
  }

	public void dataReceived(List<JSOModel> models) 
	{
		// Start with a fresh set of messages
		messages.clear();
  	
  	// do this instead of initializing selectedRow
  	// to 0 in case there are no messages in this folder
  	startIndex = 0;
  	selectedRow = -1;
  	count = 0;
  	
  	for (JSOModel model : models)
  	{
  		if (model.get("model").equals(AoAPI.MSG_METADATA))
  		{
  			count = Integer.valueOf(model.get("count"));
  			startIndex = Integer.valueOf(model.get("start"));
  		}
  		else // Assume it's a data model
  		{
  			messages.add(new BaseModel(model));
  		}
  	}
  	
  	boolean msgFound = false;
  	if (!messages.isEmpty()) {
  		if (MessageForum.isMessageForum(messages.get(0)))
  			forum = new MessageForum(messages.get(0)).getForum();
  		// at the very least we will select the first msg
  		msgFound = true;
  		selectedRow = 0;
  	}
  	
  	if (selectMessage != null)
  	{
  		// GWT gives some funny compilation problems if the below
  		// line is inlined in the if statement, so keep this variable
  		int messageId = Integer.valueOf(selectMessage.getId());
  		// find this message and select it
  		for (int i = selectedRow; i < messages.size(); i++)
  		{
  			if (Integer.valueOf(messages.get(i).getId()) == messageId)
  			{
  				break;
  			}
  			
  			selectedRow++;
  			
  		}
  	}
  	update();
  	if (msgFound) selectRow(selectedRow);
  	selectMessage = null;
	}
	
	public class PageOverHandler implements ClickHandler {
  	private String direction;
		private BaseModel message;
  	
  	public PageOverHandler(String direction, BaseModel message) {
  		this.direction = direction;
  		this.message = message;
  	}
		public void onClick(ClickEvent event) {
			 if (direction.equals("older")) {
				 // Move forward a page.
				 startIndex += VISIBLE_MESSAGE_COUNT;
				 if (startIndex >= count) {
					 startIndex -= VISIBLE_MESSAGE_COUNT;
				 } 
			 }
			 else if (direction.equals("newer")) {
				 // Move back a page.
		     startIndex -= VISIBLE_MESSAGE_COUNT;
		     if (startIndex < 0) {
		       startIndex = 0;
		     }
			 }
			 
			 styleRow(selectedRow, false);
		   selectedRow = -1;
		   if (MessageForum.isMessageForum(message))
		   {
			   MessageForum mf = new MessageForum(message);
		  	 if (mf.isResponse() && mf.getStatus() != MessageStatus.PENDING)
			  	 Messages.get().displayResponses(mf.getForum(), startIndex);
			   else
			  	 Messages.get().displayMessages(mf.getForum(), mf.getStatus(), startIndex);
		   }
		   else if (SurveyInput.isSurveyInput(message))
		   {
		  	 SurveyInput input = new SurveyInput(message);
		  	 Messages.get().displaySurveyInput(input.getPrompt(), startIndex);
		   }
		}
  	
  }
	
}
