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
import java.util.Map.Entry;

import org.otalo.ao.client.Broadcasts.Images;
import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.model.BaseModel;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.Prompt;
import org.otalo.ao.client.model.Survey;
import org.otalo.ao.client.model.User;
import org.otalo.ao.client.model.Survey.SurveyStatus;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.logical.shared.CloseEvent;
import com.google.gwt.event.logical.shared.CloseHandler;
import com.google.gwt.event.logical.shared.SelectionEvent;
import com.google.gwt.event.logical.shared.SelectionHandler;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.Tree;
import com.google.gwt.user.client.ui.TreeItem;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

/**
 * A wrapper class for Forums to be able to act on their widget
 * representation in the interface.
 * 
 * @author dsc
 *
 */
public class SurveyWidget implements ClickHandler, JSONRequester {
	private Survey survey;
	private Images images;
	private Tree tree;
	private TreeItem root;
	private HTML rootHTML, detailsHTML, cancelHTML;
	private Composite parent;
	private HashMap<HTML,Prompt> promptMap = new HashMap<HTML, Prompt>();
	private HashMap<HTML,TreeItem> leaves = new HashMap<HTML, TreeItem>();
	private AreYouSureDialog confirm;
	private JSOModel detailsModel;
	
	public SurveyWidget(Survey s, Images images, Composite parent)
	{
		this.survey = s;
		this.images = images;
		this.parent = parent;
		
		tree = new Tree(images);
		String title = s.getName() + " ";
		SurveyStatus status = survey.getStatus();		
		switch (status)
		{
			case ACTIVE:
				title += "<span style='color:green'>(Active)</span>";
				break;
			case CANCELLED:
				title += "<span style='color:red'>(Cancelled)</span>";
				break;
			case EXPIRED:
				title += "(Expired)";
		}
		rootHTML = imageItemHTML(images.inbox(), title);
    root = new TreeItem(rootHTML);
    tree.addItem(root);
    
    tree.addSelectionHandler(new SelectionHandler<TreeItem>() {

			public void onSelection(SelectionEvent<TreeItem> event) {
				TreeItem item = event.getSelectedItem();
				
				if (promptMap.containsKey(item))
				{
					Prompt p = promptMap.get(item);
					Messages.get().displaySurveyInput(p, 0);
				}
			}
		});
    
    JSONRequest request = new JSONRequest();
		request.doFetchURL(AoAPI.SURVEY_INPUT + survey.getId() + "/", this);
    
    request = new JSONRequest();
		request.doFetchURL(AoAPI.SURVEY_DETAILS + survey.getId() + "/", new SurveyDetailsRequester() );
    
    detailsHTML = imageItemHTML(images.drafts(), "Details");
    detailsHTML.addClickHandler(new ClickHandler() {

			public void onClick(ClickEvent event) {
				DetailsDialog details = new DetailsDialog(detailsModel);
				details.show();
				details.center();
				
			}
		});
    
    TreeItem details = new TreeItem(detailsHTML);
  	root.addItem(details);
    
    if (status == SurveyStatus.ACTIVE)
    {
    	cancelHTML = imageItemHTML(images.reject_sm(), "Cancel");
    	cancelHTML.addClickHandler(new ClickHandler() {
				public void onClick(ClickEvent event) {
					confirm = new AreYouSureDialog("Are you sure you want to cancel all future calls for this broadcast?");
					confirm.show();
					confirm.center();
					
					confirm.addCloseHandler(new CloseHandler<PopupPanel>() {
						public void onClose(CloseEvent<PopupPanel> event) {
							if (confirm.isConfirmed())
							{
								JSONRequest request = new JSONRequest();
								request.doFetchURL(AoAPI.CANCEL_SURVEY + survey.getId() + "/", new CancelSurveyRequester() );
							}
							
						}
					});
					
					
				}
			});
    	
    	TreeItem cancel = new TreeItem(cancelHTML);
    	root.addItem(cancel);
    }
    
	}
	
	public void dataReceived(List<JSOModel> models) {
		HTML promptHTML;
		TreeItem prompt;
		String pName;
		Prompt p;
		
    for (JSOModel model : models)
		{
			p = new Prompt(model);
    	pName = p.getName() != null ? p.getName() : "Prompt " + p.getOrder(); 
			promptHTML = imageItemHTML(images.responses(), pName);
			prompt = new TreeItem(promptHTML);
			promptMap.put(promptHTML, p);
			leaves.put(promptHTML, prompt);
			//root.addItem(prompt);
			root.insertItem(0, prompt);
		}
		
	}
	
	private class SurveyDetailsRequester implements JSONRequester {
		public void dataReceived(List<JSOModel> models) {
			detailsModel = models.get(0);
		}
		
	}
	
	private class CancelSurveyRequester implements JSONRequester {
		public void dataReceived(List<JSOModel> models) {
			ConfirmDialog saved = new ConfirmDialog("Survey Cancelled!");
			saved.show();
			saved.center();
			
			Messages.get().loadBroadcasts();
		}
		
	}

  /**
   * Generates HTML for a tree item with an attached icon.
   * 
   * @param imageProto the image prototype to use
   * @param title the title of the item
   * @return the resultant HTML
   */
  private HTML imageItemHTML(ImageResource res, String title) {
  	AbstractImagePrototype imageProto = AbstractImagePrototype.create(res);
    HTML label = new HTML(imageProto.getHTML() + " " + title);
    label.addClickHandler(this);
  	label.addClickHandler((ClickHandler)parent);
  	return label;
  }
	
	public Widget getWidget()
	{
		return tree;
	}
	
	public void close()
	{
		tree.setSelectedItem(null);
		root.setState(false);
	}
	
	public boolean contains(Object w)
	{
		return w == rootHTML || promptMap.containsKey(w) || w == cancelHTML || w == detailsHTML;
	}
	
	public void selectFirst()
	{
		root.setState(true);		
		TreeItem firstPrompt = root.getChild(0);
		tree.setSelectedItem(firstPrompt);
		root.setState(true);
		
		HTML leaf = null;
		for (Entry<HTML, TreeItem> entry : leaves.entrySet()) {
      if (entry.getValue().equals(firstPrompt)) {
          leaf = entry.getKey();
          break;
      }
		}
		
		if (leaf != null)
		{
			Prompt p = promptMap.get(leaf);
			Messages.get().displaySurveyInput(p, 0);
		}
	}
	
	public void onClick(ClickEvent event) {
		Object sender = event.getSource();
		
		if (sender == rootHTML)
		{
			selectFirst();
		}
		else if (promptMap.containsKey(sender))
		{
			tree.setSelectedItem(null);
			TreeItem leaf = leaves.get(sender);
			leaf.getTree().setSelectedItem(leaf);
			Prompt p = promptMap.get(sender);
			Messages.get().displaySurveyInput(p, 0);
		}
	}

	private class DetailsDialog extends DialogBox {

	  public DetailsDialog(JSOModel details) {
	  	//setWidth("500px");
	    // Use this opportunity to set the dialog's caption.
	    setText("Awaaz De Administration");

	    // Create a VerticalPanel to contain the 'about' label and the 'OK' button.
	    VerticalPanel outer = new VerticalPanel();
	    outer.setWidth("100%");
	    outer.setSpacing(10);

	    // Create the 'about' text and set a style name so we can style it with CSS.
	    String startdate = details.get("startdate");
	    String enddate = details.get("enddate");
			String completed = details.get("completed");
			String pending = details.get("pending");
			
			String surveyDetails = "<b>Start: </b> " + startdate + "<br><br>";
			surveyDetails += "<b>End: </b> " + enddate + "<br><br>";
			surveyDetails += "<b>Num Recipients: </b>" + String.valueOf(completed.split(", ").length+pending.split(", ").length);
			
			surveyDetails += "<br><br><b>Pending:</b>";    
	    HTML pendingHTML = new HTML(surveyDetails);
			pendingHTML.setStyleName("mail-AboutText");
	    outer.add(pendingHTML);
	    
	    Label pendingLbl = new Label(pending, true);
	    pendingLbl.setWordWrap(true);
	    pendingLbl.setStyleName("dialog-NumsText");
	    outer.add(pendingLbl);
	    
	    HTML compHTML = new HTML("<br><b>Completed:</b>");
			compHTML.setStyleName("mail-AboutText");
	    outer.add(compHTML);
	    
	    Label completedLbl = new Label(completed, true);
	    completedLbl.setWordWrap(true);
	    completedLbl.setStyleName("dialog-NumsText");
	    outer.add(completedLbl);

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
