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
import org.otalo.ao.client.model.SMSMessage;
import org.otalo.ao.client.model.Subject;
import org.otalo.ao.client.model.SurveyInput;
import org.otalo.ao.client.model.User;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.shared.HandlerRegistration;
import com.google.gwt.resources.client.ClientBundle;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HTMLTable.Cell;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.HorizontalPanel;

/**
 * A composite that displays voice messages.
 */
public class SMSList extends Composite implements ClickHandler, JSONRequester {

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
  private HorizontalPanel navBar = new HorizontalPanel();
  private List<SMSMessage> messages = new ArrayList<SMSMessage>();
  private Images images;
  
  public enum SMSListType {
		IN, SENT
	}
  
  /**
   * Specifies the images that will be bundled for this Composite and specify
   * that tree's images should also be included in the same bundle.
   */
  public interface Images extends ClientBundle {
    ImageResource approve();
    
    ImageResource reject();
  }

  public SMSList(Images images) {
  	this.images = images;

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

    initWidget(table);
    setStyleName("mail-List");

    initTable();
  }

  public void onClick(ClickEvent event) {
    Object sender = event.getSource();
	  // Select the row that was clicked (-1 to account for header row).
	  Cell cell = table.getCellForEvent(event);
	  if (cell != null) {
	    int row = cell.getRowIndex();
	    int col = cell.getCellIndex();
	    if (row > 0 && (table.getHTML(row, col).equals("") || col != 2)) {
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
    //table.getFlexCellFormatter().setColSpan(0, 3, 2);
    table.getRowFormatter().setStyleName(0, "mail-ListHeader");

    // Initialize the rest of the rows.
    for (int i = 0; i < VISIBLE_MESSAGE_COUNT; ++i) {
      table.setText(i + 1, 0, "");
      table.setText(i + 1, 1, "");
      table.setText(i + 1, 2, "");
      table.getFlexCellFormatter().setColSpan(0, 2, 2);
      table.getCellFormatter().setWordWrap(i + 1, 0, false);
      table.getCellFormatter().setWordWrap(i + 1, 1, false);
      table.getCellFormatter().setWordWrap(i + 1, 2, true);
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
      } else {
        table.getRowFormatter().removeStyleName(row + 1, "mail-SelectedRow");
      }
    }
  }

  private void update(SMSListType type) {
    // Update the older/newer buttons & label.
    int max = startIndex + VISIBLE_MESSAGE_COUNT;
    if (max > count) {
      max = count;
    }
    
    if (type == SMSListType.IN)
    {
    	table.setText(0, 1, "Sender");
    }
    else if (type == SMSListType.SENT)
    {
    	table.setText(0, 1, "Recipients");
    }
    
    newerButton.setVisible(startIndex != 0);
    olderButton.setVisible(startIndex + VISIBLE_MESSAGE_COUNT < count);
    
    if (newButtonReg != null) {newButtonReg.removeHandler(); newButtonReg = null;}
    if (oldButtonReg != null) {oldButtonReg.removeHandler(); oldButtonReg = null;}
   
    if (count > 0)
    {
	    SMSMessage message = messages.get(0);
	    newButtonReg = newerButton.addClickHandler(new PageOverHandler("newer", message, type));
	    oldButtonReg = olderButton.addClickHandler(new PageOverHandler("older", message, type));

    }

    countLabel.setText("" + (startIndex + 1) + " - " + max + " of " + count);

    // Show the selected messages.
    int i = 0;
    for (; i < VISIBLE_MESSAGE_COUNT; ++i) {
    	// Don't read past the end.
      if (i >= messages.size()) {
        break;
      }
      
      SMSMessage message = messages.get(i);

    	// Add a new row to the table, then set each of its columns
      table.setText(i + 1, 0, message.getSentOn());
      
      if (type == SMSListType.IN)
      {
	      User user = message.getSender();
	      String senderText = ("".equals(user.getName()) || "null".equals(user.getName())) ? user.getNumber() : user.getName() + " (" + user.getNumber() + ")";
      
	      table.setText(i + 1, 1, senderText);
      }
      else
      {
      	Anchor recipientsLink = new Anchor("List");
      	recipientsLink.addClickHandler(new RecipientsClickHandler(message));
 	      table.setWidget(i+1, 1, recipientsLink);
      }
      String text = message.getText();
      table.setText(i+1, 2, text);
      table.getFlexCellFormatter().setColSpan(i+1, 2, 2);

    }

    // Clear any remaining slots.
    for (; i < VISIBLE_MESSAGE_COUNT; ++i) {
      table.setHTML(i + 1, 0, "&nbsp;");
      table.setHTML(i + 1, 1, "&nbsp;");
      table.setHTML(i + 1, 2, "&nbsp;");
      table.setHTML(i + 1, 3, "&nbsp;");

    }
    
    // Select the first row if none is selected.
    if (selectedRow == -1 && count > 0) {
      selectRow(0);
    }
  }
  
  private class RecipientsClickHandler implements ClickHandler{
  	private SMSMessage message;
		public RecipientsClickHandler(SMSMessage message)
		{
			this.message = message;
		}
		public void onClick(ClickEvent event) {
			JSONRequest request = new JSONRequest();
			request.doFetchURL(AoAPI.SMS_RECIPIENTS + message.getId() + "/", new SMSRecipientRequester());
			
		}
  	
  }
  
  private class SMSRecipientRequester implements JSONRequester {
		public void dataReceived(List<JSOModel> models) {
			ArrayList<User> recipients = new ArrayList<User>();
			for (JSOModel model : models)
	  	{
	  			recipients.add(new User(model));
	  	}
			
			RecipientsDialog recipientsDlg = new RecipientsDialog(recipients);
			recipientsDlg.show();
			recipientsDlg.center();
		}
		
	}
  
  public void reset(SMSListType type)
  {
		messages.clear();
		startIndex = 0;
		count = 0;
		styleRow(selectedRow, false);
		update(type);
  }
	public void displaySurveyInput(Prompt p, int start)
	{
		styleRow(selectedRow, false);
		JSONRequest request = new JSONRequest();
		request.doFetchURL(AoAPI.PROMPT_RESPONSES + p.getId() + "/?start=" + String.valueOf(start), this);
	}

  
  
  public void getMessages(SMSListType type, int start)
  {
  	styleRow(selectedRow, false);
  	String lineId = Messages.get().getLine().getId();
  	String filterParams = "/?type="+String.valueOf(type.ordinal())+"&start=" + String.valueOf(start);
  	JSONRequest request = new JSONRequest();
  	request.doFetchURL(AoAPI.SMS + lineId + filterParams, this);
  	
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
  	int type=0;
  	
  	for (JSOModel model : models)
  	{
  		if (model.get("model").equals(AoAPI.MSG_METADATA))
  		{
  			count = Integer.valueOf(model.get("count"));
  			startIndex = Integer.valueOf(model.get("start"));
  			type = Integer.valueOf(model.get("type"));
  		}
  		else // Assume it's a data model
  		{
  			messages.add(new SMSMessage(model));
  		}
  	}
  	
  	boolean msgFound = false;
  	if (!messages.isEmpty()) {
  		
  		// at the very least we will select the first msg
  		msgFound = true;
  		selectedRow = 0;
  	}
  	
  	update(SMSListType.values()[type]);
  	if (msgFound) selectRow(selectedRow);
	}
	
	public class PageOverHandler implements ClickHandler {
  	private String direction;
		private SMSMessage message;
		private SMSListType type;
  	
  	public PageOverHandler(String direction, SMSMessage message, SMSListType type) {
  		this.direction = direction;
  		this.message = message;
  		this.type = type;
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
		   Messages.get().displaySMS(type, startIndex);
		}
  	
  }
	
	private class RecipientsDialog extends DialogBox {

	  public RecipientsDialog(ArrayList<User> recipients) {
	  	//setWidth("500px");
	    // Use this opportunity to set the dialog's caption.
	    setText("Awaaz De Administration");

	    // Create a VerticalPanel to contain the 'about' label and the 'OK' button.
	    VerticalPanel outer = new VerticalPanel();
	    outer.setWidth("100%");
	    outer.setSpacing(10);

	    // Create the 'about' text and set a style name so we can style it with CSS
			String recipientsStr="";
			for (User u : recipients)
			{
				recipientsStr += u.getNumber() + ", ";
			}
			// remove trailing comma
			recipientsStr = recipientsStr.substring(0, recipientsStr.length()-2);
			
			String smsDetails = "<b>Num Recipients: </b>" + String.valueOf(recipients.size());
			
			smsDetails += "<br><br><b>Recipients:</b>";    
	    HTML recHTML = new HTML(smsDetails);
			recHTML.setStyleName("mail-AboutText");
	    outer.add(recHTML);
	    
	    Label recLbl = new Label(recipientsStr, true);
	    recLbl.setWordWrap(true);
	    recLbl.setStyleName("dialog-NumsText");
	    outer.add(recLbl);
	    

	    // Create the 'OK' button, along with a handler that hides the dialog
	    // when the button is clicked.
	    outer.add(new Button("Close", new ClickHandler() {
	      public void onClick(ClickEvent event) {
	        hide();
	      }
	    }));

	    setWidget(outer);
	  }

	  @Override
	  public boolean onKeyDownPreview(char key, int modifiers) {
	    // Use the popup's key preview hooks to close the dialog when either
	    // enter or escape is pressed.
	    switch (key) {
	      case KeyCodes.KEY_ENTER:
	      case KeyCodes.KEY_ESCAPE:
	        hide();
	        break;
	    }

	    return true;
	  }
	}
	
}
