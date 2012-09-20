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

import java.math.BigDecimal;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.JSONRequest.AoAPI.ValidationError;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.MessageForum;
import org.otalo.ao.client.model.User;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.TextBox;


public class UploadDialog extends DialogBox {
	private FormPanel uploadForm = new FormPanel();
	private Hidden forumId = new Hidden("forumid");
	private Hidden messageForumId = new Hidden("messageforumid");
	private TextBox number;
	private HorizontalPanel numberPanel = new HorizontalPanel();
	private HorizontalPanel contentPanel = new HorizontalPanel();
	private Button saveButton, cancelButton;
	
	public UploadDialog() {
		setText("Upload Content");
		FlexTable outer = new FlexTable();
		outer.setSize("100%", "100%");
		uploadForm.setAction(JSONRequest.BASE_URL+AoAPI.UPLOAD);
		uploadForm.setMethod(FormPanel.METHOD_POST);
		uploadForm.setEncoding(FormPanel.ENCODING_MULTIPART);
		
		FileUpload main = new FileUpload();
		main.setName("main");
		main.setTitle("Content");
		Label mainLabel = new Label("Content:");
		
		number = new TextBox();
		number.setName("number");
		User moderator = Messages.get().getModerator();
		if (moderator != null)
			// default is the moderator's number
			number.setValue(moderator.getNumber());
		Label numberLabel = new Label("Author Number:");
		
		saveButton = new Button("Save", new ClickHandler() {
      public void onClick(ClickEvent event) {
      	setClickedButton();
      	uploadForm.submit();
      }
    });
		
		cancelButton = new Button("Cancel", new ClickHandler() {
      public void onClick(ClickEvent event) {
      	hide();
      }
    });
		
		outer.setWidget(0, 0, mainLabel);
		outer.getCellFormatter().setWordWrap(0, 0, false);
		contentPanel.setSpacing(2);
		DOM.setStyleAttribute(contentPanel.getElement(), "textAlign", "left");
		contentPanel.add(main);
		outer.setWidget(0, 1, contentPanel);
		outer.setWidget(1, 0, numberLabel);
		outer.getCellFormatter().setWordWrap(1, 0, false);
		numberPanel.setSpacing(2);	
		DOM.setStyleAttribute(numberPanel.getElement(), "textAlign", "left");
		numberPanel.add(number);
		outer.setWidget(1, 1, numberPanel);

		
		HorizontalPanel buttons = new HorizontalPanel();
		// tables don't obey the setHorizontal of parents, and buttons is a table,
		// so use float instead
		DOM.setStyleAttribute(buttons.getElement(), "cssFloat", "right");
		buttons.add(saveButton);
		buttons.add(cancelButton);
		outer.setWidget(3, 1, buttons);
		
		outer.setWidget(outer.getRowCount(), 0, forumId);
		outer.setWidget(outer.getRowCount(), 0, messageForumId);
		
		uploadForm.setWidget(outer);
		
		setWidget(uploadForm);
	}
	
	public void setForum(Forum f)
	{
		forumId.setValue(f.getId());
	}
	
	public void setMessageForum(MessageForum mf)
	{
		messageForumId.setValue(mf.getId());
	}
	
	public void validationError(ValidationError error, String msg)
	{
		HTML msgHTML = new HTML("<span style='color:red'>("+msg+")</span>");
		if (error == ValidationError.INVALID_NUMBER && numberPanel.getWidgetCount() == 1)
		{
			numberPanel.insert(msgHTML, 0);
		}
		else if (error == ValidationError.NO_CONTENT && contentPanel.getWidgetCount() == 1)
		{
			contentPanel.insert(msgHTML, 0);
		}
		saveButton.setEnabled(true);
		cancelButton.setEnabled(true);
	}
	
	public void reset()
	{
		uploadForm.reset();
		saveButton.setEnabled(true);
		cancelButton.setEnabled(true);
		User moderator = Messages.get().getModerator();
		if (numberPanel.getWidgetCount() == 2)
			numberPanel.remove(0);
		if (contentPanel.getWidgetCount() == 2)
			contentPanel.remove(0);
		if (moderator != null)
			// default is the moderator's number
			number.setValue(moderator.getNumber());
	}
	
	public void setCompleteHandler(SubmitCompleteHandler handler)
	{
		uploadForm.addSubmitCompleteHandler(handler);
	}
	
	public void center(Forum f)
	{
		if (Messages.get().canManage())
		{
			String balance = Messages.get().getModerator().getBalance();
			
			if (!User.FREE_TRIAL_BALANCE.equals(balance) && Double.valueOf(balance) <= Double.valueOf(User.BCAST_DISALLOW_BALANCE_THRESH) && f.getStatus() == Forum.ForumStatus.BCAST_CALL_SMS)
			{
				ConfirmDialog recharge = new ConfirmDialog("Your balance is too low for sending broadcast calls. Please recharge your account or set your group's delivery type setting to 'SMS only'");
				recharge.center();
			}
			else
			{
				super.center();
			}
		}
		else
			super.center();
	}
	
	private void setClickedButton()
	{
		saveButton.setEnabled(false);
		cancelButton.setEnabled(false);
	}

}
