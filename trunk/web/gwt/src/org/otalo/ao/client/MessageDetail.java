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
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Stack;
import java.util.Map.Entry;

import org.apache.commons.digester.SetRootRule;
import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.Message;
import org.otalo.ao.client.model.MessageForum;
import org.otalo.ao.client.model.User;
import org.otalo.ao.client.model.Message.MessageStatus;

import com.google.gwt.dev.util.msg.Message2ClassClass;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.http.client.URL;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DockPanel;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HTMLTable;
import com.google.gwt.user.client.ui.HasAlignment;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.SimplePanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.FormPanel.SubmitEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitHandler;
import com.google.gwt.user.client.ui.HasHorizontalAlignment.HorizontalAlignmentConstant;
import com.google.gwt.user.client.ui.HasVerticalAlignment.VerticalAlignmentConstant;

/**
 * A composite for displaying the details of a voice message.
 */
public class MessageDetail extends Composite {
	private FormPanel detailsForm;
	private Hidden userId, messageForumId, moveDirection;
	private Button saveButton, moveUpButton, moveDownButton, clickedButton;
	private VerticalPanel moveButtons, thread, controls, metadata;
	private HorizontalPanel outer, responsePanel;
	private DockPanel threadPanel;
	private FlexTable detailsTable;
	private CheckBox sticky;
	private Map<String, TextBox> callerDetailsMap = new HashMap<String, TextBox>();
	private TagWidget tags;
	private RoutingWidget routing;

  public MessageDetail() {
  	outer = new HorizontalPanel();
  	outer.setSize("100%", "100%");
  	detailsForm = new FormPanel();
  	detailsForm.setWidget(outer);
  	detailsForm.setMethod(FormPanel.METHOD_POST);
  	detailsForm.setEncoding(FormPanel.ENCODING_MULTIPART);
  	
  	// TODO if needed
  	//detailsForm.addSubmitHandler(new CallerDetailsUpdate());
  	detailsForm.addSubmitCompleteHandler(new MessageDetailsUpdate());
  	
  	threadPanel = new DockPanel();
  	controls = new VerticalPanel();
  	detailsTable = new FlexTable();
  	metadata = new VerticalPanel();
  	metadata.setHeight("100%");
  	tags = new AOTagWidget();
  	routing = new AORoutingWidget();
  	metadata.setVerticalAlignment(HasVerticalAlignment.ALIGN_TOP);
  	metadata.add(tags);
  	metadata.setVerticalAlignment(HasVerticalAlignment.ALIGN_BOTTOM);
  	metadata.add(routing);
  	
  	outer.setSpacing(3);
  	outer.add(detailsTable);
  	outer.add(threadPanel);
  	outer.add(metadata);
  	outer.add(controls);
  	
  	controls.setSize("100%", "100%");
  	Label detailsTitle = new Label("Caller Details");
  	detailsTitle.setStyleName("gwt-Label");
  	detailsTable.setWidget(0,0,detailsTitle);
  	detailsTable.getFlexCellFormatter().setColSpan(0, 0, 2);
  	
  	addCallerDetailsField(detailsTable, "Number", "number");
  	addCallerDetailsField(detailsTable, "Name", "name");
  	addCallerDetailsField(detailsTable, "District", "district");
  	addCallerDetailsField(detailsTable, "Taluka", "taluka");
  	addCallerDetailsField(detailsTable, "Village", "village");
  	
  	userId = new Hidden("userid");
  	detailsTable.setWidget(detailsTable.getRowCount(), 0, userId);
  	
  	messageForumId = new Hidden("messageforumid");
  	detailsTable.setWidget(detailsTable.getRowCount(), 0, messageForumId);

  	threadPanel.setSize("100%", "100%");
  	Label threadTitle = new Label("Thread");
  	threadTitle.setStyleName("gwt-Label");
  	threadPanel.add(threadTitle, DockPanel.NORTH);
  	
  	threadPanel.setVerticalAlignment(HasVerticalAlignment.ALIGN_BOTTOM);
  	FileUpload response = new FileUpload();
  	response.setName("response");
  	Label responseLabel = new Label("Response:");
  	responsePanel = new HorizontalPanel();
  	responsePanel.setSpacing(10);
  	responsePanel.add(responseLabel);
  	responsePanel.add(response);
  	threadPanel.add(responsePanel, DockPanel.SOUTH);
  	thread = new VerticalPanel();
  	thread.setSize("100%", "100%");
  	thread.setSpacing(3);
  	threadPanel.add(thread, DockPanel.NORTH);
  	
  	sticky = new CheckBox("Sticky");
  	sticky.setName("position");
  	
  	saveButton = new Button("Save", new ClickHandler() {
      public void onClick(ClickEvent event) {
      	setClickedButton(saveButton);
      	detailsForm.setAction(JSONRequest.BASE_URL + AoAPI.UPDATE_MESSAGE);
        detailsForm.submit();
      }
    });
  	
  	moveDirection = new Hidden("direction");
  	detailsTable.setWidget(detailsTable.getRowCount(), 0, moveDirection);
  	
  	moveUpButton = new Button("Move Up", new ClickHandler() {
      public void onClick(ClickEvent event) {
      	setClickedButton(moveUpButton);
      	moveDirection.setValue("up");
      	detailsForm.setAction(JSONRequest.BASE_URL+ AoAPI.MOVE);
        detailsForm.submit();
      }
    });
  	
  	moveDownButton = new Button("Move Down", new ClickHandler() {
      public void onClick(ClickEvent event) {
      	setClickedButton(moveDownButton);
      	moveDirection.setValue("down");
      	detailsForm.setAction(JSONRequest.BASE_URL+AoAPI.MOVE);
        detailsForm.submit();
      }
    });
  	
  	controls.setHorizontalAlignment(HasAlignment.ALIGN_RIGHT);
  	controls.setSpacing(5);
  	
  	// to snap the button to the bottom of the panel
  	controls.setVerticalAlignment(HasAlignment.ALIGN_BOTTOM);
  	
  	VerticalPanel buttons = new VerticalPanel();
  	buttons.setSize("100%", "100%");
  	buttons.setVerticalAlignment(HasVerticalAlignment.ALIGN_BOTTOM);
  	buttons.setHorizontalAlignment(HasAlignment.ALIGN_CENTER);
  	
  	moveButtons = new VerticalPanel();
  	moveButtons.setSize("100%", "100%");
  	moveButtons.setVerticalAlignment(HasVerticalAlignment.ALIGN_BOTTOM);
  	// To center the movebuttons in the panel when no moderation
  	moveButtons.setHorizontalAlignment(HasAlignment.ALIGN_CENTER);
  	moveButtons.add(moveUpButton);
  	moveButtons.add(moveDownButton);
  	moveButtons.setSpacing(5);
  	buttons.add(sticky);
  	buttons.add(moveButtons);
  	buttons.add(saveButton);
  	controls.add(buttons);
  	
  	
    outer.setStyleName("mail-Detail");
  	
    initWidget(detailsForm);
    
    
  }
  
  /**
   * Add a text box with label to the table, one field per row.
   * The field is if you want to submit this as part of a form, 
   * and also corresponds to the field in the db model for Users
   * 
   * @param table
   * @param label
   * @param inputID
   */
  private TextBox addCallerDetailsField(HTMLTable table, String label, String field)
  {
  	TextBox box = new TextBox();
  	box.setName(field);
  	callerDetailsMap.put(field, box);
  	
  	Label lab = new Label(label);
  	
  	int row = table.getRowCount();
  	table.setWidget(row, 0, lab);
  	table.setWidget(row, 1, box);
  	
  	return box;
  }

  public void setItem(MessageForum messageForum) {  
  	// in case selection is done from msgList
  	reset();
  	
  	Forum f = messageForum.getForum();
  	setModerated(f.moderated());
  	setRouteable(f.routeable());
  	setTagable(f);
  	
  	switch (messageForum.getStatus())
  	{
  		case PENDING:
	  	  	setMovable(false); 
	  	  	setCanRespond(false); 
	  	  	setSticky(false);
	  	  	break;
  		case APPROVED:
	  	  	setMovable(true);
	  	  	setCanRespond(true); 
	  	  	setSticky(true);
	  	  	break;
  		case REJECTED:
  			setMovable(false);
  			setCanRespond(false);
  			setSticky(false);
  	}
  	
  	//special case
  	if (messageForum.isResponse() && messageForum.getStatus() != MessageStatus.PENDING)
  	{
  		setMovable(false);
  		setCanRespond(false); 
  		setSticky(false);
  	}
  	messageForumId.setValue(messageForum.getId());
  	if ("null".equals(messageForum.getPosition()) || "".equals(messageForum.getPosition()))
  	{
  		sticky.setValue(false);
  	}
  	else
  	{
  		sticky.setValue(true);
  	}
  	
  	// Load Tags
  	tags.loadTags(messageForum);
  	
  	// Load routing info
  	routing.loadRoutingInfo(messageForum);
  	
    // Populate details pane with caller info.
  	// Load from the server in case the data was updated
  	// since the last load
    JSONRequest request = new JSONRequest();
    request.doFetchURL(AoAPI.USER + messageForum.getAuthor().getId() + "/", new CallerDetailsRequester());
    
    request = new JSONRequest();
    request.doFetchURL(AoAPI.THREAD + messageForum.getId() + "/", new ThreadRequester(messageForum));
  	
  }
  
  private class CallerDetailsRequester implements JSONRequester {

		public void dataReceived(List<JSOModel> models) {
			JSOModel caller = models.get(0);
			User u = new User(caller);
			
			loadCallerDetails(u);
		}
		
	}
  
  private class ThreadRequester implements JSONRequester {
  	private MessageForum mf;
  	
  	public ThreadRequester(MessageForum mf)
  	{
  		this.mf = mf;
  	}
		public void dataReceived(List<JSOModel> models) {
			List<MessageForum> threadList = new ArrayList<MessageForum>();
			
			for (JSOModel m : models)
			{
				threadList.add(new MessageForum(m));
			}
			
			loadThread(mf, threadList);
			
		}
		
	}
  
  private void loadCallerDetails(User u)
  {
  	for (Entry<String,TextBox>entry : callerDetailsMap.entrySet())
  	{
  		String val = u.getField(entry.getKey());
  		if (!"null".equals(val))
  			entry.getValue().setText(val);
  	}
  	
  	// also load user id
  	userId.setValue(u.getId());
  }
  
  private void loadThread(MessageForum selectedMessage, List<MessageForum> messages)
  {
  	ArrayList<MessageForum> rgt = new ArrayList<MessageForum>();
  	for (MessageForum m : messages)
  	{
  		String indent = "";
  		if (rgt.size() > 0)
  		{
  			for (int i=rgt.size()-1; i >= 0 ; i--)
  			{
  				if (Integer.valueOf(rgt.get(i).getRgt()) < Integer.valueOf(m.getRgt()))
  					rgt.remove(i);
  			}
  		}
  		
  		for (int i=0; i<rgt.size(); i++)
  		{
  			indent += "&nbsp&nbsp&nbsp&nbsp";
  		}
  		
  		rgt.add(m);
  		User user = m.getAuthor();
  		String callerText = ("".equals(user.getName()) || "null".equals(user.getName())) ? user.getNumber() : user.getName() + " (" + user.getNumber() + ")";
  		String threadText = callerText + " - " + m.getDate();
  		
  		HTML msgHTML;
  		if (selectedMessage.getId().equals(m.getId()))
  		{
  			msgHTML = new HTML("<span>"+indent+ " " +threadText+"</span>");
  			msgHTML.setStyleName("selectedThreadMessage");
  		}
  		else
  		{
  			msgHTML = new HTML("<span>"+indent+"<a href='javascript:;'>"+threadText+"</a></span>");
  			msgHTML.addClickHandler(new ThreadMessageHandler(m));
  		}
  		
  		
  		thread.add(msgHTML);
  	}
  }
	
  public class ThreadMessageHandler implements ClickHandler {
  	private MessageForum mf;
  	
  	public ThreadMessageHandler(MessageForum mf) {
  		this.mf = mf;
  	}
		public void onClick(ClickEvent event) {
			Messages.get().displayMessages(mf);
		}
  	
  }
  
	private class MessageDetailsUpdate implements SubmitCompleteHandler {
		
		public void onSubmitComplete(SubmitCompleteEvent event) {
			// get the message that was updated
			JSOModel model = JSONRequest.getModels(event.getResults()).get(0);
			MessageForum m = new MessageForum(model);
			
			if (clickedButton == saveButton)
			{
				ConfirmDialog saved = new ConfirmDialog("Updated!");
				saved.show();
				saved.center();
			}
			
			// reload messageList
			// need to go to the server so that the caller details
			// are reflected in the other messages
			Messages.get().displayMessages(m);
			
			submitComplete();
			
		}
	}
	
	public String validateTags()
	{
		return tags.getErrorText();
	}
	
	public void reset()
	{
		detailsForm.reset();
		thread.clear();
		sticky.setValue(false);
		messageForumId.setValue("");
		tags.reset();
		routing.reset();
	}
	
	private void setMovable(boolean canMove)
	{
		moveButtons.setVisible(canMove);
	}
	
	private void setCanRespond(boolean canRespond)
	{
		responsePanel.setVisible(canRespond);
	}
	
	private void setSticky(boolean canStick)
	{
		sticky.setVisible(canStick);
	}
	
	private void setRouteable(boolean isRouteable)
	{
		routing.setVisible(isRouteable);
	}
	
	private void setTagable(Forum f)
	{
		tags.setVisible(f.postingAllowed() || f.responsesAllowed());
	}
	
	/**
	 * We are keeping track of which button was clicked in this class
	 * because the onSubmit event does not tell us that. To make it work
	 * we need to make sure there aren't multiple button clicks at once
	 * @param button
	 */
	private void setClickedButton(Button button)
	{
		clickedButton = button;
		saveButton.setEnabled(false);
		moveUpButton.setEnabled(false);
		moveDownButton.setEnabled(false);
	}
	
	private void submitComplete()
	{
		clickedButton = null;
		saveButton.setEnabled(true);
		moveUpButton.setEnabled(true);
		moveDownButton.setEnabled(true);
	}
	
	private void setModerated(boolean isModerated)
	{
		if (isModerated)
		{
			detailsTable.setVisible(true);
			threadPanel.setVisible(true);
		}
		else
		{
			detailsTable.setVisible(false);
			threadPanel.setVisible(false);
			setMovable(true);
		}
	}

}
