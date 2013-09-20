/*
 * Copyright 2013 Google Inc.
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
package org.otalo.ao.client.search;

import java.util.ArrayList;
import java.util.List;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.Messages;
import org.otalo.ao.client.SoundWidget;
import org.otalo.ao.client.model.BaseModel;
import org.otalo.ao.client.model.Call;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.MessageForum;
import org.otalo.ao.client.model.Subject;
import org.otalo.ao.client.model.SurveyInput;
import org.otalo.ao.client.model.User;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.shared.HandlerRegistration;
import com.google.gwt.resources.client.ClientBundle;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HTMLTable.Cell;
import com.google.gwt.user.client.ui.HorizontalPanel;

/**
 * A composite that displays voice messages.
 */
public class SearchResultMsgList extends Composite {

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
	private List<BaseModel> messages = new ArrayList<BaseModel>();
	private int count, selectedRow = -1;
	private String current_page, previous_page, next_page;
	private FlexTable table = new FlexTable();
	private HorizontalPanel navBar = new HorizontalPanel();
	private Images images;

	private SearchFilterPanel filterPanelRef;

	private BaseModel selectMessage;
	private Forum forum;

	/**
	 * Specifies the images that will be bundled for this Composite and specify
	 * that tree's images should also be included in the same bundle.
	 */
	public interface Images extends ClientBundle {
		ImageResource download();
	}

	public SearchResultMsgList(Images images) {
		this.images = images;

		// Setup the table.
		table.setCellSpacing(0);
		table.setCellPadding(0);
		table.setWidth("100%");

		// Hook up events.
		table.addClickHandler(new TableClickHandler());

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

	/**
	 * Initializes the table so that it contains enough rows for a full page of
	 * messages. Also creates the images that will be used as 'read' flags.
	 */
	private void initTable() {
		// Create the header row.
		table.setText(0, 0, "Date");
		table.setText(0, 1, "User");
		table.setText(0, 2, "Source/Forum");
		table.setText(0, 3, "Message");
		table.setWidget(0, 4, navBar);
		table.getFlexCellFormatter().setColSpan(0, 3, 3);
		table.getRowFormatter().setStyleName(0, "mail-ListHeader");

		// Initialize the rest of the rows.
		for (int i = 0; i < VISIBLE_MESSAGE_COUNT; ++i) {
			table.setText(i + 1, 0, "");
			table.setText(i + 1, 1, "");
			table.setText(i + 1, 2, "");
			table.setText(i + 1, 3, "");
			table.setText(i + 1, 4, "");
			table.setText(i + 1, 5, "");
			table.getCellFormatter().setWordWrap(i + 1, 0, false);
			table.getCellFormatter().setWordWrap(i + 1, 1, false);
			table.getCellFormatter().setWordWrap(i + 1, 2, false);
		}
	}

	public void displayMessages(SearchFilterPanel filterPanel, List<JSOModel> models) {
		this.filterPanelRef = filterPanel;
		// Start with a fresh set of messages
		messages.clear();

		// do this instead of initializing selectedRow
		// to 0 in case there are no messages in this folder
		current_page = "1";
		styleRow(selectedRow, false);
		selectedRow = -1;
		count = 0;

		for (JSOModel model : models) {
			if (model.get("model").equals(AoAPI.MSG_METADATA)) {
				count = Integer.valueOf(model.get("count"));
				previous_page = model.get("previous_page");
				if("undefined".equalsIgnoreCase(previous_page))
					previous_page = null;
				next_page = model.get("next_page");
				if("undefined".equalsIgnoreCase(next_page))
					next_page = null;
				current_page = model.get("current_page");
			}
			else {// Assume it's a data model
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

		if (selectMessage != null) {
			// GWT gives some funny compilation problems if the below
			// line is inlined in the if statement, so keep this variable
			int messageId = Integer.valueOf(selectMessage.getId());
			// find this message and select it
			for (int i = selectedRow; i < messages.size(); i++) {
				if (Integer.valueOf(messages.get(i).getId()) == messageId) {
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
				filterPanelRef.requestResultPage(previous_page);
			}
			else if (direction.equals("newer")) {
				// Move back a page.
				filterPanelRef.requestResultPage(next_page);
			}
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

		selectedRow = row;

		BaseModel message = messages.get(row);
		if (MessageForum.isMessageForum(message))
			Messages.get().setItem(new MessageForum(message), false);
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
				table.setHTML(row + 1, 3, sound.getWidget().getHTML());
				if (Messages.get().canManage())
				{
					Anchor downloadLink = new Anchor("Download", AoAPI.DOWNLOAD);
					downloadLink.setHref(AoAPI.DOWNLOAD + message.getId() + "/");
					table.setWidget(row + 1, 5, downloadLink);
					//table.setHTML(row+1, 5, downloadLink.getHTML());
				}


			} else {
				table.getRowFormatter().removeStyleName(row + 1, "mail-SelectedRow");
				table.clearCell(row + 1, 3);
				if (Messages.get().canManage()) table.clearCell(row + 1, 5);
			}
		}
	}

	private void update() {
		// Update the older/newer buttons & label.
		newerButton.setVisible((next_page != null && !next_page.isEmpty()));
		olderButton.setVisible((previous_page != null && !previous_page.isEmpty()));

		if (newButtonReg != null) {newButtonReg.removeHandler(); newButtonReg = null;}
		if (oldButtonReg != null) {oldButtonReg.removeHandler(); oldButtonReg = null;}

		if (count > 0) {
			BaseModel message = messages.get(0);
			newButtonReg = newerButton.addClickHandler(new PageOverHandler("newer", message));
			oldButtonReg = olderButton.addClickHandler(new PageOverHandler("older", message));
		}

		int startIndex = 0;
		int endIndex = 0;
		int currentPageNum = Integer.parseInt(current_page);

		if(currentPageNum == 1 && count > 0) {
			startIndex = 1;
			endIndex = VISIBLE_MESSAGE_COUNT;
		}
		else if(currentPageNum > 1 && count > 0) {
			startIndex = (VISIBLE_MESSAGE_COUNT * currentPageNum) + 1 - VISIBLE_MESSAGE_COUNT;
			endIndex = startIndex;
			if(endIndex + VISIBLE_MESSAGE_COUNT < count)
				endIndex += VISIBLE_MESSAGE_COUNT;
			else
				endIndex+= count - startIndex;
		}

		countLabel.setText("" + startIndex + " - " + endIndex + " of " + count);

		// Show the selected messages.
		int i = 0;
		for (; i < VISIBLE_MESSAGE_COUNT; ++i) {
			// Don't read past the end.
			if (i >= messages.size()) {
				break;
			}

			BaseModel message = messages.get(i);

			if (MessageForum.isMessageForum(message)) {
				MessageForum mf = new MessageForum(message);
				// Add a new row to the table, then set each of its columns
				table.setText(i + 1, 0, mf.getDate());
				User user = mf.getAuthor();
				String callerText = ("".equals(user.getName()) || "null".equals(user.getName())) ? user.getNumber() : user.getName() + " (" + user.getNumber() + ")";
				table.setText(i + 1, 1, callerText);
				table.setText(i + 1, 2, mf.getForum().getName());

				if (forum != null && forum.moderated()) {
					//TODO
				}
				else {
					table.setHTML(i+1, 3, "&nbsp");
					table.setHTML(i+1, 4, "&nbsp");
				}
			}
			else if (SurveyInput.isSurveyInput(message)) {
				SurveyInput input = new SurveyInput(message);
				Call call = input.getCall();

				// Add a new row to the table, then set each of its columns
				table.setText(i + 1, 0, call.getDate());
				Subject subject = call.getSubject();
				String callerText = ("".equals(subject.getName()) || "null".equals(subject.getName())) ? subject.getNumber() : subject.getName() + " (" + subject.getNumber() + ")";
				table.setText(i + 1, 1, callerText);
				table.setText(i + 1, 2, "Survey");

				//TODO: add download link
				Anchor downloadLink = new Anchor("Download", AoAPI.DOWNLOAD_SURVEY_INPUT + input.getId());
				table.setWidget(i+1, 3, downloadLink);
				table.setHTML(i+1, 4, "&nbsp");
			}
			table.setHTML(i+1, 6,"");
		}

		// Clear any remaining slots.
		for (; i < VISIBLE_MESSAGE_COUNT; ++i) {
			table.setHTML(i + 1, 0, "&nbsp;");
			table.setHTML(i + 1, 1, "&nbsp;");
			table.setHTML(i + 1, 2, "&nbsp;");
			table.setHTML(i + 1, 3, "&nbsp;");
			table.setHTML(i + 1, 4, "&nbsp;");
			table.setHTML(i + 1, 5, "&nbsp;");

		}

		// Select the first row if none is selected.
		if (selectedRow == -1 && count > 0) {
			selectRow(0);
		} else {
			Messages.get().getMessageDetail().reset();
		}
	}

	private class TableClickHandler implements ClickHandler {
		@Override
		public void onClick(ClickEvent event) {
			// Select the row that was clicked (-1 to account for header row).
			Cell cell = table.getCellForEvent(event);
			if (cell != null) {
				int row = cell.getRowIndex();
				int col = cell.getCellIndex();
				// apparently styling the row doesn't do well with any cell that has HTML
				// so weed them out of selection
				if (row > 0 && (table.getHTML(row, col).equals("") || (col != 2 && col != 5))) {
					selectRow(row - 1);
				}
			}
		}
	}
}
