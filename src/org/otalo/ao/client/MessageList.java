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

import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.Message;
import org.otalo.ao.client.model.User;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.HTMLTable.Cell;

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
  private HorizontalPanel navBar = new HorizontalPanel();
  private List<Message> messages = new ArrayList();
  private Message selectMessage;
  private Forum forum;

  public MessageList() {
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

    initWidget(table);
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
    table.getRowFormatter().setStyleName(0, "mail-ListHeader");

    // Initialize the rest of the rows.
    for (int i = 0; i < VISIBLE_MESSAGE_COUNT; ++i) {
      table.setText(i + 1, 0, "");
      table.setText(i + 1, 1, "");
      table.setText(i + 1, 2, "");
      table.getCellFormatter().setWordWrap(i + 1, 0, false);
      table.getCellFormatter().setWordWrap(i + 1, 1, false);
      table.getCellFormatter().setWordWrap(i + 1, 2, false);
      table.getFlexCellFormatter().setColSpan(i + 1, 2, 2);
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
    Message message = messages.get(startIndex + row);
    if (message == null) {
      return;
    }

    styleRow(selectedRow, false);
    styleRow(row, true);

    message.read = true;
    selectedRow = row;
    Messages.get().displayMessage(message);
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

      Message message = messages.get(startIndex + i);

      // Add a new row to the table, then set each of its columns
      table.setText(i + 1, 0, message.getDate());
      User user = message.getAuthor();
      String callerText = "".equals(user.getName()) ? user.getNumber() : user.getName() + " (" + user.getNumber() + ")";
      table.setText(i + 1, 1, callerText);
      SoundWidget sound = new SoundWidget(message.getContent());
      table.setHTML(i + 1, 2, sound.getWidget().getHTML());
    }

    // Clear any remaining slots.
    for (; i < VISIBLE_MESSAGE_COUNT; ++i) {
      table.setHTML(i + 1, 0, "&nbsp;");
      table.setHTML(i + 1, 1, "&nbsp;");
      table.setHTML(i + 1, 2, "&nbsp;");

    }

    // Select the first row if none is selected.
    if (selectedRow == -1 && count > 0) {
      selectRow(0);
    }
  }
  
  public void getMessages(Forum f)
  {
  	getMessages(f, "");
  }
  
  
  public void getMessages(Forum f, String filterParams)
  {
  	getMessages(f, filterParams, null);
  }
  
  public void getMessages(Forum f, String filterParams, Message m)
  {
  	selectMessage = m;
  	
  	styleRow(selectedRow, false);
  	String forumId = f.getId();
  	JSONRequest request = new JSONRequest();
		request.doFetchURL("messages/" + forumId + "/?" + filterParams, this);
  }

	public void dataReceived(List<JSOModel> models) 
	{
		// Start with a fresh set of messages
		messages.clear();
  	
  	for (JSOModel model : models)
  	{
  		messages.add(new Message(model));
  	}
  	
  	startIndex = 0;
  	// initialize to 0 instead of -1 so that
  	// update() below doesn't call selectRow itself
  	selectedRow = 0;
  	
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
  			
  			if (selectedRow == VISIBLE_MESSAGE_COUNT) 
  			{
  				startIndex += VISIBLE_MESSAGE_COUNT;
  				selectedRow = 0;
  			}
  		}
  	}
  	update();
 		selectRow(selectedRow);
		
	}
}
