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

import org.otalo.ao.client.ForumWidget.UploadComplete;
import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.model.Forum;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HasAlignment;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.SimplePanel;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;


public class UploadDialog extends DialogBox {
	private FormPanel uploadForm = new FormPanel();
	private Hidden forumId = new Hidden("forumid");
	
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
		
		FileUpload summary = new FileUpload();
		summary.setName("summary");
		summary.setTitle("Summary");
		Label summaryLabel = new Label("Summary (optional):");
		
		Button saveButton = new Button("Save", new ClickHandler() {
      public void onClick(ClickEvent event) {
      	uploadForm.submit();
      }
    });
		
		Button cancelButton = new Button("Cancel", new ClickHandler() {
      public void onClick(ClickEvent event) {
      	hide();
      }
    });
		
		outer.setWidget(0, 0, mainLabel);
		outer.getCellFormatter().setWordWrap(0, 0, false);
		outer.setWidget(0, 1, main);
		outer.setWidget(1, 0, summaryLabel);
		outer.getCellFormatter().setWordWrap(1, 0, false);
		outer.setWidget(1, 1, summary);
		
		HorizontalPanel buttons = new HorizontalPanel();
		// tables don't obey the setHorizontal of parents, and buttons is a table,
		// so use float instead
		DOM.setStyleAttribute(buttons.getElement(), "cssFloat", "right");
		buttons.add(saveButton);
		buttons.add(cancelButton);
		outer.setWidget(2, 1, buttons);
		
		outer.setWidget(outer.getRowCount(), 0, forumId);
		
		uploadForm.setWidget(outer);
		
		setWidget(uploadForm);
	}
	
	public void setForum(Forum f)
	{
		forumId.setValue(f.getId());
	}
	
	public void reset()
	{
		uploadForm.reset();		
	}
	
	public void setCompleteHandler(SubmitCompleteHandler handler)
	{
		uploadForm.addSubmitCompleteHandler(handler);
	}
}
