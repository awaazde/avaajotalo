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

import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.Message;
import org.otalo.ao.client.model.User;
import org.otalo.ao.client.model.Message.MessageStatus;

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

/**
 * A composite for displaying the details of a voice message.
 */
public class MessageDetail extends Composite {
	private FormPanel detailsForm;
	private Hidden userId, messageId, moveDirection;
	private CheckBox approve;
	private Button saveButton, moveUpButton, moveDownButton, clickedButton;
	private VerticalPanel moveButtons, thread;
	private HorizontalPanel outer;
	private DockPanel threadPanel, controls;
	private FlexTable detailsTable;
	private Map<String, TextBox> callerDetailsMap = new HashMap<String, TextBox>();

  public MessageDetail() {
  	outer = new HorizontalPanel();
  	outer.setSize("100%", "100%");
  	detailsForm = new FormPanel();
  	detailsForm.setWidget(outer);
  	detailsForm.setMethod(FormPanel.METHOD_POST);
  	detailsForm.setEncoding(FormPanel.ENCODING_MULTIPART);
  	
  	// TODO if needed
  	//detailsForm.addSubmitHandler(new CallerDetailsUpdate());
  	detailsForm.addSubmitCompleteHandler(new CallerDetailsUpdate());
  	
  	threadPanel = new DockPanel();
  	controls = new DockPanel();
  	detailsTable = new FlexTable();
  	
  	outer.setSpacing(3);
  	outer.add(detailsTable);
  	outer.add(threadPanel);
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
  	
  	messageId = new Hidden("messageid");
  	detailsTable.setWidget(detailsTable.getRowCount(), 0, messageId);

  	threadPanel.setSize("100%", "100%");
  	Label threadTitle = new Label("Thread");
  	threadTitle.setStyleName("gwt-Label");
  	threadPanel.add(threadTitle, DockPanel.NORTH);
  	
  	threadPanel.setVerticalAlignment(HasVerticalAlignment.ALIGN_BOTTOM);
  	FileUpload response = new FileUpload();
  	response.setName("response");
  	Label responseLabel = new Label("Response:");
  	HorizontalPanel responsePanel = new HorizontalPanel();
  	responsePanel.setSpacing(10);
  	responsePanel.add(responseLabel);
  	responsePanel.add(response);
  	threadPanel.add(responsePanel, DockPanel.SOUTH);
  	thread = new VerticalPanel();
  	thread.setSize("100%", "100%");
  	thread.setSpacing(3);
  	threadPanel.add(thread, DockPanel.CENTER);
  	
  	
  	approve = new CheckBox("Approve");
  	approve.setName("approve");
  	saveButton = new Button("Save", new ClickHandler() {
      public void onClick(ClickEvent event) {
      	setClickedButton(saveButton);
      	detailsForm.setAction(JSONRequest.BASE_URL+"update/message/");
        detailsForm.submit();
      }
    });
  	
  	moveDirection = new Hidden("direction");
  	detailsTable.setWidget(detailsTable.getRowCount(), 0, moveDirection);
  	
  	moveUpButton = new Button("Move Up", new ClickHandler() {
      public void onClick(ClickEvent event) {
      	setClickedButton(moveUpButton);
      	moveDirection.setValue("up");
      	detailsForm.setAction(JSONRequest.BASE_URL+"move/");
        detailsForm.submit();
      }
    });
  	
  	moveDownButton = new Button("Move Down", new ClickHandler() {
      public void onClick(ClickEvent event) {
      	setClickedButton(moveDownButton);
      	moveDirection.setValue("down");
      	detailsForm.setAction(JSONRequest.BASE_URL+"move/");
        detailsForm.submit();
      }
    });
  	
  	controls.setHorizontalAlignment(HasAlignment.ALIGN_RIGHT);
  	controls.setSpacing(5);
  	controls.add(approve, DockPanel.NORTH);
  	
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
  	buttons.add(moveButtons);
  	buttons.add(saveButton);
  	controls.add(buttons, DockPanel.SOUTH);
  	
  	
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

  public void setItem(Message message) {
  	reset();
  	messageId.setValue(message.getId());
  	approve.setValue(message.isApproved());
    // Populate details pane with caller info.
  	// Load from the server in case the data was updated
  	// since the last load
    JSONRequest request = new JSONRequest();
    request.doFetchURL("user/"+message.getAuthor().getId()+"/", new CallerDetailsRequester());
    
    request = new JSONRequest();
    request.doFetchURL("thread/"+message.getId()+"/", new ThreadRequester());
  	
  }
  
  private class CallerDetailsRequester implements JSONRequester {

		public void dataReceived(List<JSOModel> models) {
			JSOModel caller = models.get(0);
			User u = new User(caller);
			
			loadCallerDetails(u);
		}
		
	}
  
  private class ThreadRequester implements JSONRequester {

		public void dataReceived(List<JSOModel> models) {
			List<Message> threadList = new ArrayList<Message>();
			
			for (JSOModel m : models)
			{
				threadList.add(new Message(m));
			}
			
			loadThread(threadList);
			
		}
		
	}
  
  private void loadCallerDetails(User u)
  {
  	for (Entry<String,TextBox>entry : callerDetailsMap.entrySet())
  	{
  		entry.getValue().setText(u.getField(entry.getKey()));
  	}
  	
  	// also load user id
  	userId.setValue(u.getId());
  }
  
  private void loadThread(List<Message> messages)
  {
  	ArrayList<Message> rgt = new ArrayList<Message>();
  	for (Message m : messages)
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
  		String callerText = "".equals(user.getName()) ? user.getNumber() : user.getName() + " (" + user.getNumber() + ")";
  		String threadText = callerText + " - " + m.getDate();
  		
  		HTML msgHTML = new HTML("<span>"+indent+"<a href='javascript:;'>"+threadText+"</a></span>");
  		msgHTML.addClickHandler(new ThreadMessageHandler(m));
  		
  		thread.add(msgHTML);
  	}
  }
	
  public class ThreadMessageHandler implements ClickHandler {
  	private Message message;
  	
  	public ThreadMessageHandler(Message m) {
  		message = m;
  	}
		public void onClick(ClickEvent event) {
			Messages.get().displayMessages(message.getForum(), "", message);
		}
  	
  }
  
	private class CallerDetailsUpdate implements SubmitCompleteHandler {
		
		public void onSubmitComplete(SubmitCompleteEvent event) {
			// get the message that was updated
			JSOModel model = JSONRequest.getModels(event.getResults()).get(0);
			Message m = new Message(model);
			
			Forum f = m.getForum();
			
			if (clickedButton == saveButton)
			{
				ConfirmDialog saved = new ConfirmDialog("Updated!");
				saved.show();
				saved.center();
				
				// reload messageList with this message highlighted
				Messages.get().displayMessages(f, "", m);
			}
			else if (clickedButton == moveUpButton || clickedButton == moveDownButton)
			{
				Messages.get().displayMessages(f, "status=" + MessageStatus.APPROVED.ordinal(), m);
			}
			
			submitComplete();
			
		}
	}
	
	public void reset()
	{
		detailsForm.reset();
		thread.clear();
	}
	
	public void setMovable(boolean canMove)
	{
		moveButtons.setVisible(canMove);
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
	
	public void setModerated(boolean isModerated)
	{
		if (isModerated)
		{
			detailsTable.setVisible(true);
			threadPanel.setVisible(true);
			saveButton.setVisible(true);
			approve.setVisible(true);
		}
		else
		{
			detailsTable.setVisible(false);
			threadPanel.setVisible(false);
			saveButton.setVisible(false);
			approve.setVisible(false);
			setMovable(true);
		}
	}
}
