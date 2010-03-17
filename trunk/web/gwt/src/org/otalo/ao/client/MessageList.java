/*
 * Copyright 2007 Google Inc.
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
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.Message;
import org.otalo.ao.client.model.MessageForum;
import org.otalo.ao.client.model.User;
import org.otalo.ao.client.model.Message.MessageStatus;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.ImageBundle;
import com.google.gwt.user.client.ui.TreeImages;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.HTMLTable.Cell;
import com.google.gwt.user.client.ui.ImageBundle.Resource;

/**
 * A composite that displays voice messages.
 */
public class MessageList extends Composite implements ClickHandler, JSONRequester {

  private static final int VISIBLE_MESSAGE_COUNT = 10;

  private HTML countLabel = new HTML();
  private HTML newerButton = new HTML("<a href='javascript:;'>&lt; newer</a>",
      true);
  private HTML olderButton = new HTML("<a href='javascript:;'>older &gt;</a>",
      true);
  private int startIndex, selectedRow = -1;
  private FlexTable table = new FlexTable();
  private FormPanel detailsForm = new FormPanel();
  private HorizontalPanel navBar = new HorizontalPanel();
  private List<MessageForum> messages = new ArrayList();
  private MessageForum selectMessage;
  private Forum forum;
  private Hidden messageForumId;
  private Images images;
  
  /**
   * Specifies the images that will be bundled for this Composite and specify
   * that tree's images should also be included in the same bundle.
   */
  public interface Images extends ImageBundle {
    AbstractImagePrototype approve();
    
    AbstractImagePrototype reject();
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
    newerButton.addClickHandler(this);
    olderButton.addClickHandler(this);

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
    if (sender == olderButton) {
      // Move forward a page.
      startIndex += VISIBLE_MESSAGE_COUNT;
      if (startIndex >= messages.size()) {
        startIndex -= VISIBLE_MESSAGE_COUNT;
      } else {
        styleRow(selectedRow, false);
        selectedRow = -1;
        update();
      }
    } else if (sender == newerButton) {
      // Move back a page.
      startIndex -= VISIBLE_MESSAGE_COUNT;
      if (startIndex < 0) {
        startIndex = 0;
      } else {
        styleRow(selectedRow, false);
        selectedRow = -1;
        update();
      }
    } else if (sender == table) {
      // Select the row that was clicked (-1 to account for header row).
      Cell cell = table.getCellForEvent(event);
      if (cell != null) {
        int row = cell.getRowIndex();
        if (row > 0) {
          selectRow(row - 1);
        }
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
    MessageForum message = messages.get(startIndex + row);
    if (message == null) {
      return;
    }

    styleRow(selectedRow, false);
    styleRow(row, true);

    // TODO
    //message.read = true;
    selectedRow = row;

    Messages.get().setItem(message);
  }

  private void styleRow(int row, boolean selected) {
    if (row != -1) {
      if (selected) {
        table.getRowFormatter().addStyleName(row + 1, "mail-SelectedRow");
      } else {
        table.getRowFormatter().removeStyleName(row + 1, "mail-SelectedRow");
      }
    }
  }

  private void update() {
    // Update the older/newer buttons & label.
    int count = messages.size();
    int max = startIndex + VISIBLE_MESSAGE_COUNT;
    if (max > count) {
      max = count;
    }

    newerButton.setVisible(startIndex != 0);
    olderButton.setVisible(startIndex + VISIBLE_MESSAGE_COUNT < count);
    countLabel.setText("" + (startIndex + 1) + " - " + max + " of " + count);

    // Show the selected messages.
    int i = 0;
    for (; i < VISIBLE_MESSAGE_COUNT; ++i) {
      // Don't read past the end.
      if (startIndex + i >= messages.size()) {
        break;
      }

      MessageForum message = messages.get(startIndex + i);

      // Add a new row to the table, then set each of its columns
      table.setText(i + 1, 0, message.getDate());
      User user = message.getAuthor();
      String callerText = ("".equals(user.getName()) || "null".equals(user.getName())) ? user.getNumber() : user.getName() + " (" + user.getNumber() + ")";
      table.setText(i + 1, 1, callerText);
      SoundWidget sound = new SoundWidget(message.getContent());
      table.setHTML(i + 1, 2, sound.getWidget().getHTML());
      
      if (forum != null && forum.moderated())
      {
    	  HTML approveButton = new HTML(images.approve().getHTML());
	      approveButton.addClickHandler(new MessageApproveHandler(AoAPI.APPROVE, message));
	      
	      HTML rejectButton = new HTML(images.reject().getHTML());
	      rejectButton.addClickHandler(new MessageApproveHandler(AoAPI.REJECT, message));
	      
	      switch (message.getStatus()){
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
  
  private class MessageApproveHandler implements ClickHandler {
  	private String action;
  	private MessageForum messageForum;
  	
  	MessageApproveHandler(String action, MessageForum messageForum)
  	{
  		this.action = action;
  		this.messageForum = messageForum;
  	}
		public void onClick(ClickEvent event) {
			String tagErrorText = Messages.get().validateTags();
			if (tagErrorText == null) {
				// save to get the old status when we return
				selectMessage = messageForum;
				messageForumId.setValue(messageForum.getId());
				detailsForm.setAction(JSONRequest.BASE_URL + AoAPI.UPDATE_STATUS + action);
				detailsForm.submit();
			} else {
				ConfirmDialog tagValidation = new ConfirmDialog(tagErrorText);
				tagValidation.show();
				tagValidation.center();
			}
			
			
		}
  	
  }
  
  private class MessageStatusUpdated implements SubmitCompleteHandler {
		
		public void onSubmitComplete(SubmitCompleteEvent event) {
			// get the message that was updated
			JSOModel model = JSONRequest.getModels(event.getResults()).get(0);
			MessageForum m = new MessageForum(model);
			
			
			ConfirmDialog saved = new ConfirmDialog("Updated!");
			saved.show();
			saved.center();
			
			// call the dispatcher just so we can search
			// in the code
			MessageForum mf = selectMessage;
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
				Messages.get().displayMessages(mf.getForum(), mf.getStatus());
			}
			
		}
	}
  
  public void getMessages(MessageForum m)
  {
  	selectMessage = m;
  	if (m.isResponse() && m.getStatus() != MessageStatus.PENDING)
  	{
  		// call dispatcher in order to set forum widget
  		Messages.get().displayResponses(m.getForum());
  	}
  	else
  	{
  		ArrayList<MessageStatus> statuses = new ArrayList<MessageStatus>();
    	statuses.add(m.getStatus());
  		getMessages(m.getForum(), statuses);
  	}
  }
  
  public void getMessages(Forum f, MessageStatus status)
  {
  	ArrayList<MessageStatus> statuses = new ArrayList<MessageStatus>();
  	statuses.add(status);
  	getMessages(f, statuses);
  	
  }
  
  public void getResponses(Forum f)
  {
  	ArrayList<MessageStatus> statuses = new ArrayList<MessageStatus>();
  	statuses.add(MessageStatus.APPROVED);
  	statuses.add(MessageStatus.REJECTED);
  	getMessages(f, statuses);
  	
  }
  
  private void getMessages(Forum f, List<MessageStatus> statuses)
  {
  	String filterParams = "status=";
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
  	
  	styleRow(selectedRow, false);
  	String forumId = f.getId();
  	JSONRequest request = new JSONRequest();
		request.doFetchURL(AoAPI.MESSAGES + forumId + "/?" + filterParams, this);
  }

	public void dataReceived(List<JSOModel> models) 
	{
		// Start with a fresh set of messages
		messages.clear();
  	
  	for (JSOModel model : models)
  	{
  		messages.add(new MessageForum(model));
  	}
  	
  	// do this instead of initializing selectedRow
  	// to 0 in case there are no messages in this folder
  	startIndex = 0;
  	selectedRow = -1;
  	
  	boolean msgFound = false;
  	if (!messages.isEmpty()) {
  		forum = messages.get(0).getForum();
  		// at the very least we will select the first msg
  		msgFound = true;
  		selectedRow = 0;
  	}
  	
  	if (selectMessage != null)
  	{
  		// GWT gives some funny compilation problems if the below
  		// line is inlined in the if statement, so keep this variable
  		int messageForumId = Integer.valueOf(selectMessage.getId());
  		// find this message and select it
  		for (int i = selectedRow; i < messages.size(); i++)
  		{
  			if (Integer.valueOf(messages.get(i).getId()) == messageForumId)
  			{
  				break;
  			}
  			
  			selectedRow++;
  			
  			if (selectedRow == VISIBLE_MESSAGE_COUNT) 
  			{
  				startIndex += VISIBLE_MESSAGE_COUNT;
  				selectedRow = 0;
  			}
  		}
  	}
  	update();
 		if (msgFound) selectRow(selectedRow);
		selectMessage = null;
	}
}
