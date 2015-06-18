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

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.JSONRequest.AoAPI.ValidationError;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.MessageForum;
import org.otalo.ao.client.model.User;
import org.otalo.ao.client.widget.audio.client.AudioRecordParam;
import org.otalo.ao.client.widget.audio.client.AudioRecorderWidget;
import org.otalo.ao.client.widget.audio.client.RecorderEventObserver;

import com.google.gwt.dom.client.Style.TextAlign;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.logical.shared.ValueChangeEvent;
import com.google.gwt.event.logical.shared.ValueChangeHandler;
import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.RadioButton;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.datepicker.client.DateBox;


public class UploadDialog extends DialogBox implements RecorderEventObserver {
	private FormPanel uploadForm = new FormPanel();
	private Hidden forumId = new Hidden("forumid");
	private Hidden messageForumId = new Hidden("messageforumid");
	private Hidden dateField;
	private TextBox number;
	private HorizontalPanel numberPanel = new HorizontalPanel();
	private HorizontalPanel contentPanel = new HorizontalPanel();
	private HorizontalPanel datePanel;
	private Button saveButton;
	private Anchor cancelButton;
	private RadioButton now, date;
	private ListBox hour, min;

	private RadioButton recordOpt, uploadOpt;
	private AudioRecorderWidget recorder;
	private FileUpload main;
	private DateBox dateBox;
	private Label mainLabel, dateLabel;
	private FlexTable outer;
	private HTML mainMsgHTML;
	
	private final DateTimeFormat dateFormat = DateTimeFormat.getFormat("MMM-dd-yyyy"); //on server side string date should be converted back to date in this format only

	public UploadDialog() {
		setText("Record or Upload Content");
		outer = new FlexTable();
		outer.setSize("100%", "100%");
		uploadForm.setAction(JSONRequest.BASE_URL+AoAPI.RECORD_OR_UPLOAD);
		uploadForm.setMethod(FormPanel.METHOD_POST);
		uploadForm.setEncoding(FormPanel.ENCODING_MULTIPART);

		main = new FileUpload();
		main.setName("main");
		main.setTitle("Content");
		mainLabel = new Label("Content:");

		number = new TextBox();
		number.setName("number");
		User moderator = Messages.get().getModerator();
		if (moderator != null)
			// default is the moderator's number
			number.setValue(moderator.getNumber());
		Label numberLabel = new Label("Author Number:");

		saveButton = new Button("Save", new ClickHandler() {
			public void onClick(ClickEvent event) {
				if(!recorder.isRecorded() && !uploadOpt.getValue())
					setErrorMsg("Please either record message or upload it first!");
				else {
					setClickedButton();
					if(recordOpt.getValue() == true) {
						recorder.uploadData(getParams());
					} else {
						uploadForm.submit();
					}
				}
			}
		});
		
		cancelButton = new Anchor("Cancel");
		cancelButton.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent event) {
				if(recorder.isRecorded())
					recorder.stopRecording();
				hide();
			}
		});


		recordOpt = new RadioButton("options", "Record");
		recordOpt.setFormValue("record");
		recordOpt.addStyleName("label-txt");
		recordOpt.setValue(true);
		recordOpt.addClickHandler(new OptionClickHandler());

		uploadOpt = new RadioButton("options", "Upload");
		uploadOpt.setFormValue("upload");
		uploadOpt.setValue(false);
		uploadOpt.addStyleName("label-txt");
		uploadOpt.addClickHandler(new OptionClickHandler());

		
		outer.setWidget(1, 0, recordOpt);
		mainMsgHTML = new HTML("<span id='recordError'></span>");
		mainMsgHTML.addStyleName("upload-top-msg");
		outer.setWidget(1, 1, mainMsgHTML);
		outer.getCellFormatter().getElement(1, 1).getStyle().setTextAlign(TextAlign.JUSTIFY);
		outer.getCellFormatter().getElement(1, 0).getStyle().setTextAlign(TextAlign.LEFT);
		//creating recorder widget
		recorder = new AudioRecorderWidget(JSONRequest.BASE_URL+AoAPI.RECORD_OR_UPLOAD, this);
		outer.setWidget(2, 0, recorder);
		outer.getFlexCellFormatter().setColSpan(2, 0, 2);

		outer.setWidget(4, 0, uploadOpt);
		outer.getFlexCellFormatter().setColSpan(4, 0, 2);
		outer.getCellFormatter().getElement(4, 0).getStyle().setTextAlign(TextAlign.LEFT);

		outer.setWidget(5, 0, mainLabel);
		outer.getCellFormatter().setWordWrap(0, 0, false);
		outer.getCellFormatter().setStyleName(5, 0, "left-align");
		contentPanel.setSpacing(2);
		DOM.setStyleAttribute(contentPanel.getElement(), "textAlign", "left");
		contentPanel.add(main);
		outer.setWidget(5, 1, contentPanel);
		outer.getCellFormatter().setStyleName(5, 1, "left-align-no-margin");
		main.setEnabled(false);
		mainLabel.addStyleName("gray-text");

		if (Messages.get().canManage())
		{
			// no author number; but future date option is available

			// Label
			dateLabel = new Label("Broadcast Time: ");
			// Note on bcasting date
			Label dateNote = new Label("Your broadcast will begin 10-15 minutes from the time you specify here");
			dateNote.setStyleName("helptext");

			// Start now option
			now = new RadioButton("when","Now");
			now.setFormValue("now");

			date = new RadioButton("when");
			date.setFormValue("date");

			// Date Box
			
			dateBox = new DateBox();
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
			min = new ListBox();
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
			outer.setWidget(7, 0, numberLabel);
			outer.getCellFormatter().setWordWrap(1, 0, false);
			numberPanel.setSpacing(2);	
			DOM.setStyleAttribute(numberPanel.getElement(), "textAlign", "left");
			numberPanel.add(number);
			outer.setWidget(7, 1, numberPanel);
		}


		HorizontalPanel buttons = new HorizontalPanel();
		// tables don't obey the setHorizontal of parents, and buttons is a table,
		// so use float instead
		DOM.setStyleAttribute(buttons.getElement(), "cssFloat", "right");
		buttons.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
		buttons.add(cancelButton);
		buttons.add(saveButton);
		
		outer.setWidget(outer.getRowCount(), 1, buttons);

		outer.setWidget(outer.getRowCount(), 0, forumId);
		outer.setWidget(outer.getRowCount(), 0, messageForumId);
		
		HTML troubleShootLink = new HTML("<a class='trblLink' target=_blank  href='http://awaaz.de/blog/2013/10/record-your-messages-over-web'>Unable to record? Complete the one-time setup instructions</a>");
		int trblCell = outer.getRowCount();
		outer.setWidget(trblCell, 0,troubleShootLink);
		outer.getFlexCellFormatter().setColSpan(trblCell, 0, 2);
		outer.getFlexCellFormatter().addStyleName(trblCell, 0, "left-align");
		
		HTML brodtime_text = new HTML("<span>Broadcast calls will only be scheduled between 8am and 10pm IST.</span>");
		brodtime_text.addStyleName("brodcast-time-text");
		outer.setWidget(trblCell+1, 0,brodtime_text);
		outer.getFlexCellFormatter().setColSpan(trblCell+1, 0, 2);
		outer.getFlexCellFormatter().addStyleName(trblCell+1, 0, "left-align");
		
		uploadForm.setWidget(outer);

		setSaveButtonSate();
		
		setWidget(uploadForm);
	}

	public void setSaveButtonSate() {
		if(!recorder.isRecorded() && !uploadOpt.getValue())
			saveButton.setEnabled(false);
		else
			saveButton.setEnabled(true);
	}
	
	@Override
	public void recordStart() {
		setSaveButtonSate();
	}
	
	@Override
	public void onRecordSuccess(JSOModel model) {
		if (model.get("model").equals("VALIDATION_ERROR")) {
			String msg = model.get("message");
			int type = Integer.valueOf(model.get("type"));
			validationError(ValidationError.getError(type), msg);
		}
		else {
			// get the message that was updated
			MessageForum mf = new MessageForum(model);
			hide();
			ConfirmDialog saved = new ConfirmDialog("Uploaded!");
			saved.center();
			Messages.get().displayMessages(mf);
		}
	}

	@Override
	public void onRecordError(String msg) {
		setErrorMsg(msg);
		saveButton.setEnabled(true);
		cancelButton.setEnabled(true);
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
		else if ((error == ValidationError.NO_CONTENT || error == ValidationError.INVALID_FILE_FORMAT) && contentPanel.getWidgetCount() == 1)
		{
			contentPanel.insert(msgHTML, 0);
		}
		else if (error == ValidationError.INVALID_DATE && datePanel.getWidgetCount() == 0)
		{
			datePanel.insert(msgHTML, 0);
		}
		else {
			setErrorMsg(msg);
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
		recordOpt.setValue(true);
		uploadOpt.setValue(false);
		recorder.reset();
		main.setEnabled(false);
		mainLabel.removeStyleName("normal-text");
		mainLabel.addStyleName("gray-text");
		setSaveButtonSate();
	}
	
	@Override
	public void show() {
		this.reset();
		super.show();
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

			if (!User.UNLIMITED_BALANCE.equals(balance) && Double.valueOf(balance) <= Double.valueOf(User.BCAST_DISALLOW_BALANCE_THRESH) && (f.getStatus() == Forum.ForumStatus.BCAST_CALL_SMS || f.getStatus() == Forum.ForumStatus.BCAST_CALL))
			{
				ConfirmDialog recharge = new ConfirmDialog("Your balance is too low for sending broadcast calls. Please recharge your account.");
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
	
	private void setStreamControlEnabled(boolean isEnable) {
		if(Messages.get().canManage()) {
			if(!isEnable) {
				dateLabel.removeStyleName("normal-text");
				dateLabel.addStyleName("gray-text");
			}
			else {
				dateLabel.removeStyleName("normal-text");
				dateLabel.addStyleName("gray-text");
			}
			now.setEnabled(isEnable);
			date.setEnabled(isEnable);
			dateBox.setEnabled(isEnable);
			hour.setEnabled(isEnable);
			min.setEnabled(isEnable);
		}
	}
	
	private void setErrorMsg(String errorMessage) {
		mainMsgHTML.setHTML("<span id='recordError' style='color:red;'>"+errorMessage+"</span>");
	}

	private void setClickedButton()
	{
		saveButton.setEnabled(false);
		cancelButton.setEnabled(false);
	}

	private class OptionClickHandler implements ClickHandler {
		@Override
		public void onClick(ClickEvent event) {
			Object sender = event.getSource();
			if (sender == recordOpt) {
				recorder.setEnabled(true);
				main.setEnabled(false);
				mainLabel.removeStyleName("normal-text");
				mainLabel.addStyleName("gray-text");
				setSaveButtonSate();
			} 
			else if(sender == uploadOpt) {
				main.setEnabled(true);
				mainLabel.removeStyleName("gray-text");
				mainLabel.addStyleName("normal-text");
				recorder.setEnabled(false);
				
				setSaveButtonSate();
			}
		}
	}

	/**
	 * Returns the params
	 * @return
	 */
	private AudioRecordParam[] getParams() {
		List<AudioRecordParam> params = new ArrayList<AudioRecordParam>();
		if(!Messages.get().canManage()) 
			params.add(new AudioRecordParam(write(number.getName()), write(number.getValue())));
		else {
			//getting when info
			String dateValue = "";
			String hourValue = "";
			String minValue = "";
			if(now.getValue()) {
				Date d = new Date();
				dateValue = dateFormat.format(d);
				hourValue = String.valueOf(d.getHours());
				minValue = String.valueOf(d.getMinutes());
			}
			else {
				params.add(new AudioRecordParam(write("when"), write("date")));
				
				dateValue = dateField.getValue();
				hourValue = hour.getValue(hour.getSelectedIndex());
				minValue = min.getValue(min.getSelectedIndex());
			}
			
			params.add(new AudioRecordParam(write("date"), write(dateValue)));
			params.add(new AudioRecordParam(write("hour"), write(hourValue)));
			params.add(new AudioRecordParam(write("min"), write(minValue)));
		}
		
		params.add(new AudioRecordParam(write(messageForumId.getName()), write(messageForumId.getValue())));
		params.add(new AudioRecordParam(write(forumId.getName()), write(forumId.getValue())));
		if(recordOpt.getValue())
			params.add(new AudioRecordParam(write("options"), write("record")));
		else
			params.add(new AudioRecordParam(write("options"), write("upload")));
		return params.toArray(new AudioRecordParam[0]);
	}
	
	/**
	 * Returns the data
	 * @param data
	 * @param writer
	 */
	private String write(String data) {
		if (data == null) {
			return null;
		}

		StringBuilder builder = new StringBuilder();
		
		for (int i = 0, n = data.length(); i < n; ++i) {
			final char c = data.charAt(i);
			switch (c) {
			case '\\':
			case '"':
				builder.append('\\').append(c);
				break;
			case '\b':
				builder.append("\\b");
				break;
			case '\t':
				builder.append("\\t");
				break;
			case '\n':
				builder.append("\\n");
				break;
			case '\f':
				builder.append("\\f");
				break;
			case '\r':
				builder.append("\\r");
				break;
			default:
				builder.append(c);
			}
		}
		
		return builder.toString();
	}
}
