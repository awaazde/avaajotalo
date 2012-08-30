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
import java.util.List;

import org.otalo.ao.client.Fora.Images;
import org.otalo.ao.client.JSONRequest.AoAPI.ValidationError;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.Line;
import org.otalo.ao.client.model.Message.MessageStatus;
import org.otalo.ao.client.model.MessageForum;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Tree;
import com.google.gwt.user.client.ui.TreeItem;
import com.google.gwt.user.client.ui.Widget;

/**
 * A wrapper class for Forums to be able to act on their widget
 * representation in the interface.
 * 
 * @author dsc
 *
 */
public class ForumWidget implements ClickHandler {
	private Tree tree;
	private TreeItem root, inbox, approved, rejected, responses, upload, manage;
	private HTML rootHTML, inboxHTML, approvedHTML, rejectedHTML, responsesHTML, uploadHTML, manageHTML;
	private Forum forum;
	private Composite parent;
	private List<HTML>options = new ArrayList<HTML>();
	private UploadDialog uploadDlg = new UploadDialog();
	private boolean responsesSelected = false;
	private Line line;
	
	public ForumWidget(Forum f, Line l, Images images, Composite parent)
	{
		this.forum = f;
		this.line = l;
		this.parent = parent;
		
		tree = new Tree(images);
		rootHTML = imageItemHTML(images.home(), forum.getName());
	    root = new TreeItem(rootHTML);
	    tree.addItem(root);
    
    if (forum.moderated())
    {
    	inboxHTML = imageItemHTML(images.inbox(), "Inbox");
        inbox = new TreeItem(inboxHTML);
        root.addItem(inbox);
    
    	approvedHTML = imageItemHTML(images.approve_sm(), "Approved");
	    approved = new TreeItem(approvedHTML);
	    root.addItem(approved);

	    rejectedHTML = imageItemHTML(images.reject_sm(), "Rejected");
	    rejected = new TreeItem(rejectedHTML);
	    root.addItem(rejected);
    }
    else // there is only approved content
    {
    	approvedHTML = imageItemHTML(images.approve_sm(), "Approved");
	    approved = new TreeItem(approvedHTML);
	    root.addItem(approved);
    }
    
    // if responses can be made by either admin only or anyone
    if (forum.postingAllowed() | forum.responsesAllowed())
    {
    	responsesHTML = imageItemHTML(images.responses(), "Responses");
	    responses = new TreeItem(responsesHTML);
	    root.addItem(responses);
    }
    
    uploadHTML = imageItemHTML(images.sent(), "Upload");
    upload = new TreeItem(uploadHTML);
    root.addItem(upload);
    
    uploadDlg.setForum(f);
    uploadDlg.setCompleteHandler(new UploadComplete());
    
    if (line != null && line.canManage())
    {
    	manageHTML = imageItemHTML(images.manage(), "Manage");
      manage = new TreeItem(manageHTML);
      root.addItem(manage);
    }
    
    options.add(rootHTML);
    options.add(inboxHTML);
    options.add(approvedHTML);
    options.add(rejectedHTML);
    options.add(responsesHTML);
    options.add(uploadHTML);
    options.add(manageHTML);
    
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
	
	public Forum getForum()
	{
		return forum;
	}
	
	public void expand() 
	{
		root.setState(true);
	}

	public void onClick(ClickEvent event) {
     Object sender = event.getSource();
    if (sender == inboxHTML) 
    {
    	Messages.get().displayMessages(forum, MessageStatus.PENDING, 0);
    } 
    else if (sender == approvedHTML) 
    {
    	Messages.get().displayMessages(forum, MessageStatus.APPROVED, 0);
    }
    else if (sender == rejectedHTML) 
    {
    	Messages.get().displayMessages(forum, MessageStatus.REJECTED, 0);
    }
    else if (sender == responsesHTML) 
    {
  		responsesSelected = true;
    	Messages.get().displayResponses(forum, 0);
    }
    else if (sender == uploadHTML)
    {
    	uploadDlg.reset();
    	uploadDlg.center();
    }
    else if (sender == manageHTML)
    {
    	Messages.get().loadManageGroupsInterface(line, forum);
    }
    else if (sender == rootHTML)
    {
    	selectMain();
    }
	}
	
	public boolean contains(Object widget)
	{
		return options.contains(widget);
	}
	
	public void close()
	{
		tree.setSelectedItem(null);
		root.setState(false);
	}
	
	public void selectMain()
	{
  	this.expand();
  	
  	if (forum.moderated())
  	{
  		Messages.get().displayMessages(forum, MessageStatus.PENDING, 0);
  	}
  	else
  	{
  		Messages.get().displayMessages(forum, MessageStatus.APPROVED, 0);
  	}
	}
	public class UploadComplete implements SubmitCompleteHandler {

		public void onSubmitComplete(SubmitCompleteEvent event) {
			JSOModel model = JSONRequest.getModels(event.getResults()).get(0);
			if (model.get("model").equals("VALIDATION_ERROR"))
			{
				String msg = model.get("message");
				int type = Integer.valueOf(model.get("type"));
				uploadDlg.validationError(ValidationError.getError(type), msg);
			}
			else
			{
				// get the message that was updated
				MessageForum mf = new MessageForum(model);
				uploadDlg.hide();
				ConfirmDialog saved = new ConfirmDialog("Uploaded!");
				saved.center();
				
				Messages.get().displayMessages(mf);
				
			}

		}
	}
	
	public void setFolderResponses(Forum f)
	{
		if (f.getId().equals(forum.getId())) responsesSelected = true;
		setFolder(f, null);
	}
	
	public void setFolder(Forum f, MessageStatus status)
	{
		if (f.getId().equals(forum.getId()))
		{
			this.expand();
			if (responsesSelected())
			{
				// special case
				tree.setSelectedItem(responses);
			}
			else		
			{
				switch (status) {
				case PENDING:
					tree.setSelectedItem(inbox);
					break;
				case APPROVED:
					tree.setSelectedItem(approved);
					break;
				case REJECTED:
					tree.setSelectedItem(rejected);
					break;
				case MANAGE:
					tree.setSelectedItem(manage);
				}
			}
						
			// reset it now that we've selected something,
			// otherwise the flag will stay set when we click
			// on something else
			responsesSelected = false;
		}
		else
		{
			close();
		}
	}
	
	public boolean responsesSelected()
	{
		return responsesSelected;
	}
	
}
