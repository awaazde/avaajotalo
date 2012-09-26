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
import java.util.Date;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.JSONRequest.AoAPI.ValidationError;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.MessageForum;
import org.otalo.ao.client.model.User;

import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.logical.shared.ValueChangeEvent;
import com.google.gwt.event.logical.shared.ValueChangeHandler;
import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HasAlignment;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.RadioButton;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.datepicker.client.DateBox;


public class UploadDialog extends DialogBox {
	private FormPanel uploadForm = new FormPanel();
	private Hidden forumId = new Hidden("forumid");
	private Hidden messageForumId = new Hidden("messageforumid");
	private Hidden dateField;
	private TextBox number;
	private HorizontalPanel numberPanel = new HorizontalPanel();
	private HorizontalPanel contentPanel = new HorizontalPanel();
	private HorizontalPanel datePanel;
	private Button saveButton, cancelButton;
	private RadioButton now, date;
	private ListBox hour;
	
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
		
		if (Messages.get().canManage())
		{
			// no author number; but future date option is available
			
			// Label
			Label dateLabel = new Label("Broadcast Time: ");
			// Note on bcasting date
			Label dateNote = new Label("Your broadcast will begin 10-15 minutes from the time you specify here");
			dateNote.setStyleName("helptext");
			
			// Start now option
	  	now = new RadioButton("when","Now");
	  	now.setFormValue("now");
	  	
	  	date = new RadioButton("when");
			date.setFormValue("date");
			
			// Date Box
			DateTimeFormat dateFormat = DateTimeFormat.getFormat("MMM-dd-yyyy");
	    DateBox dateBox = new DateBox();
	    dateBox.setFormat(new DateBox.DefaultFormat(dateFormat));
	    dateBox.addValueChangeHandler(new ValueChangeHandler<Date>() {
				
				public void onValueChange(ValueChangeEvent<Date> event) {
					now.setValue(false);
					date.setValue(true);
					Date d = event.getValue();
					dateField.setValue(DateTimeFormat.getFormat("MMM-dd-yyyy").format(d));
				}
			});
	    
	    // Hour box
	    hour = new ListBox();
	    hour.setName("hour");
	    for(int i=0; i < 24; i++)
	    {
	    	String hourStr;
	    	if (i < 10)
	    		hourStr = "0"+String.valueOf(i);
	    	else
	    		hourStr = String.valueOf(i);
	    	
				hour.addItem(hourStr);
	    }
	    hour.addChangeHandler(new ChangeHandler() {
				
				public void onChange(ChangeEvent event) {
					now.setValue(false);
					date.setValue(true);
					
				}
			});
	    
	    // Minute box
	    ListBox min = new ListBox();
	    min.setName("min");
	    for(int i=0; i < 60; i+=5)
			{
				String minStr;
	    	if (i < 10)
					minStr = "0"+String.valueOf(i);
	    	else
	    		minStr = String.valueOf(i);
	    	
	    	min.addItem(minStr);
			}
	    min.addChangeHandler(new ChangeHandler() {
				
				public void onChange(ChangeEvent event) {
					now.setValue(false);
					date.setValue(true);
					
				}
			});
	    
	    int row = outer.getRowCount();
	    outer.setWidget(row,0, dateLabel);
	    outer.getCellFormatter().setWordWrap(1, 0, false);
	    
	    HorizontalPanel nowPanel = new HorizontalPanel();
	    //nowPanel.setHorizontalAlignment(HasAlignment.ALIGN_LEFT);
	    nowPanel.setSpacing(4);
	    nowPanel.add(now);
	    DOM.setStyleAttribute(nowPanel.getElement(), "textAlign", "left");
	    outer.setWidget(row, 1, nowPanel);
	    
	    HorizontalPanel datePicker = new HorizontalPanel();
	    datePicker.setSpacing(4);
	    datePicker.add(date);
	    datePicker.add(dateBox);
	    datePicker.add(hour);
	    datePicker.add(new Label(":"));
	    datePicker.add(min);
	    row = outer.getRowCount();
	    
	    datePanel = new HorizontalPanel();
	    outer.setWidget(row, 0, datePanel);
	    DOM.setStyleAttribute(datePicker.getElement(), "textAlign", "left");
	    outer.setWidget(row, 1, datePicker);
	    
	    row = outer.getRowCount();
	    outer.setWidget(row, 1, dateNote);
	    outer.getCellFormatter().setWordWrap(row, 1, false);
	    dateField = new Hidden("date");
	    outer.setWidget(outer.getRowCount(), 0, dateField);
	    
		}
		else
		{
			outer.setWidget(1, 0, numberLabel);
			outer.getCellFormatter().setWordWrap(1, 0, false);
			numberPanel.setSpacing(2);	
			DOM.setStyleAttribute(numberPanel.getElement(), "textAlign", "left");
			numberPanel.add(number);
			outer.setWidget(1, 1, numberPanel);
		}

		
		HorizontalPanel buttons = new HorizontalPanel();
		// tables don't obey the setHorizontal of parents, and buttons is a table,
		// so use float instead
		DOM.setStyleAttribute(buttons.getElement(), "cssFloat", "right");
		buttons.add(saveButton);
		buttons.add(cancelButton);
		outer.setWidget(outer.getRowCount(), 1, buttons);
		
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
		else if (error == ValidationError.INVALID_DATE && datePanel.getWidgetCount() == 0)
		{
			datePanel.insert(msgHTML, 0);
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
		if (Messages.get().canManage())
		{
			now.setValue(true);
			hour.setSelectedIndex(9);
		}
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
