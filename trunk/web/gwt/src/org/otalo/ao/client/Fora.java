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
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.JSONRequest.AoAPI.ValidationError;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.Line;
import org.otalo.ao.client.model.Message.MessageStatus;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.resources.client.ClientBundle;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasAlignment;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.HasHorizontalAlignment.HorizontalAlignmentConstant;
import com.google.gwt.user.client.ui.HasVerticalAlignment.VerticalAlignmentConstant;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Tree;
import com.google.gwt.user.client.ui.VerticalPanel;

/**
 * A panel of fora, each presented as a tree.
 */
public class Fora extends Composite implements JSONRequester, ClickHandler {
  private ArrayList<ForumWidget> widgets = new ArrayList<ForumWidget>();
	// lookup of lines that map to the given group
	
	/**
   * Specifies the images that will be bundled for this Composite and specify
   * that tree's images should also be included in the same bundle.
   */
  public interface Images extends ClientBundle, Tree.Resources {
  	ImageResource inbox();  
    ImageResource home();
    ImageResource sent();
    ImageResource treeLeaf();
    ImageResource broadcast();
    ImageResource approve_sm();
    ImageResource reject_sm();
    ImageResource responses();
    ImageResource manage();
  }

  private Images images;
  private VerticalPanel p;
  private CreateGroupDialog createGroupDlg = new CreateGroupDialog();

  /**
   * Constructs a new list of forum widgets with a bundle of images.
   * 
   * @param images a bundle that provides the images for this widget
   */
  public Fora(Images images) {
	  this.images = images;
	  p = new VerticalPanel();
	  
		// Get fora
		JSONRequest request = new JSONRequest();
		String params = "";
		if (Messages.get().canManage())
		{
			params = "?latestfirst=1";
		}
		request.doFetchURL(AoAPI.GROUP + params, this);
	  
		createGroupDlg.setCompleteHandler(new CreateGroupComplete());
		
	  initWidget(p);
  }

	public void dataReceived(List<JSOModel> models) {
		reloadFora(models);
	}
	
	public void reloadFora(List<JSOModel> models)
	{
		List<Line> lines = new ArrayList<Line>();
		for (JSOModel model : models)
	  {
				lines.add(new Line(model));
	  }
  	
  	loadFora(lines);
	}

	private void loadFora(List<Line> lines)
	{
		p.clear();
		widgets.clear();
		
		for (int i = 0; i < lines.size(); ++i) 
		{
			Line l = lines.get(i);
			// ASSUME one group per line
			Forum f = l.getForums().get(0);
			ForumWidget w = new ForumWidget(f, l, images, this);
	    
			p.add(w.getWidget());
			widgets.add(w);
		}
	  
	  if (Messages.get().canManage())
	  {
	  	Button create = new Button("Create group");
		  create.addClickHandler(new ClickHandler() {
				
				public void onClick(ClickEvent event) {
					createGroupDlg.reset();
					createGroupDlg.center();
					
				}
			});
		  
		  VerticalAlignmentConstant v = p.getVerticalAlignment();
		  HorizontalAlignmentConstant h = p.getHorizontalAlignment();
		  p.setVerticalAlignment(HasVerticalAlignment.ALIGN_BOTTOM);
		  p.setHorizontalAlignment(HasAlignment.ALIGN_CENTER);
		  p.add(create);
		  // to account for the fact that new forums can be
		  // added on action in the console (create group)
		  p.setVerticalAlignment(v);
		  p.setHorizontalAlignment(h);
	  }
	  
		// Hackish Initialization of the forum panel
		widgets.get(0).selectMain();
	}
	
	public void setFolder(Forum f, MessageStatus status)
	{
		for (ForumWidget w : widgets)
		{
			w.setFolder(f, status);
		}
	}
	
	public void setFolderResponses(Forum f)
	{
		for (ForumWidget w : widgets)
		{
			w.setFolderResponses(f);
		}
	}
	
	/**
	 * This is for clicked tree items. Unselect all other ones
	 * and collapse their trees
	 * @param event
	 */
	public void onClick(ClickEvent event) {
		Object source = event.getSource();
		for (ForumWidget w : widgets)
		{
			if (!w.contains(source))
				w.close();
		}
		
	}
	
	public class CreateGroupDialog extends DialogBox {
		private FormPanel createGroupForm = new FormPanel();
		private HorizontalPanel namePanel = new HorizontalPanel();
		private  ListBox language;
		
		public CreateGroupDialog() {
			setText("Create New Group");
			
			FlexTable outer = new FlexTable();
			outer.setSize("100%", "100%");
			createGroupForm.setAction(JSONRequest.BASE_URL+AoAPI.CREATE_GROUP);
			createGroupForm.setMethod(FormPanel.METHOD_POST);
			
			TextBox groupName = new TextBox();
			groupName.setName("groupname");
			Label groupLabel = new Label("Name:");
			namePanel.setSpacing(2);
			DOM.setStyleAttribute(namePanel.getElement(), "textAlign", "left");
			namePanel.add(groupLabel);
			
			language = new ListBox();
			language.setName("language");
			language.addItem("Hindi", "hin");
			language.addItem("Gujarati", "guj");
			language.addItem("English", "eng");
			Label langLabel = new Label("Language:");
			
			Button createButton = new Button("Create", new ClickHandler() {
	      public void onClick(ClickEvent event) {
	      	createGroupForm.submit();
	      }
	    });
			
			Button cancelButton = new Button("Cancel", new ClickHandler() {
	      public void onClick(ClickEvent event) {
	      	hide();
	      }
	    });
			
			outer.setWidget(0, 0, namePanel);
			outer.setWidget(0, 1, groupName);
			outer.setWidget(1, 0, langLabel);
			HorizontalPanel langPanel = new HorizontalPanel();
			langPanel.setSpacing(2);
			DOM.setStyleAttribute(langPanel.getElement(), "textAlign", "left");
			langPanel.add(language);
			outer.setWidget(1, 1, langPanel);

			
			HorizontalPanel buttons = new HorizontalPanel();
			// tables don't obey the setHorizontal of parents, and buttons is a table,
			// so use float instead
			DOM.setStyleAttribute(buttons.getElement(), "cssFloat", "right");
			buttons.add(createButton);
			buttons.add(cancelButton);
			outer.setWidget(3, 1, buttons);
			
			createGroupForm.setWidget(outer);
			
			setWidget(createGroupForm);
		}
		
		public void validationError(ValidationError error, String msg)
		{
			HTML msgHTML = new HTML("<span style='color:red'>("+msg+")</span>");
			if ((error == ValidationError.NO_CONTENT || error == ValidationError.INVALID_GROUPNAME) && namePanel.getWidgetCount() == 1)
			{
				namePanel.insert(msgHTML, 1);
			}
		}
		
		public void reset()
		{
			createGroupForm.reset();
			if (namePanel.getWidgetCount() == 2)
				namePanel.remove(1);
			language.setSelectedIndex(0);
		}
		
		public void setCompleteHandler(SubmitCompleteHandler handler)
		{
			createGroupForm.addSubmitCompleteHandler(handler);
		}
	
	}
	
	private class CreateGroupComplete implements SubmitCompleteHandler {

		public void onSubmitComplete(SubmitCompleteEvent event) {
			List<JSOModel> models = JSONRequest.getModels(event.getResults());
			JSOModel model = models.get(0);
			if (model.get("model").equals("VALIDATION_ERROR"))
			{
				String msg = model.get("message");
				int type = Integer.valueOf(model.get("type"));
				createGroupDlg.validationError(ValidationError.getError(type), msg);
			}
			else
			{
				createGroupDlg.hide();
				ConfirmDialog saved = new ConfirmDialog("Group created! Get its number in Manage -> Settings");
				saved.show();
				saved.center();
				
				// These models are Lines with connected forums. Lines since 
				// line info can be shared to also populate 
				// the group management UI (save a server hit)
				reloadFora(models);
			}

		}
	}

}
