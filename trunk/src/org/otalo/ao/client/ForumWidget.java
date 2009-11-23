package org.otalo.ao.client;

import java.util.ArrayList;
import java.util.List;

import org.otalo.ao.client.Fora.Images;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.Message;
import org.otalo.ao.client.model.Message.MessageStatus;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Tree;
import com.google.gwt.user.client.ui.TreeItem;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;

/**
 * A wrapper class for Forums to be able to act on their widget
 * representation in the interface.
 * 
 * @author dsc
 *
 */
public class ForumWidget implements ClickHandler {
	private Tree tree;
	private TreeItem root, inbox, approved, upload;
	private HTML rootHTML, inboxHTML, approvedHTML, uploadHTML;
	private Forum forum;
	private Composite parent;
	private List<HTML>options = new ArrayList<HTML>();
	private UploadDialog uploadDlg = new UploadDialog();
	
	public ForumWidget(Forum f, Images images, Composite parent)
	{
		forum = f;
		this.parent = parent;
		
		tree = new Tree(images);
		rootHTML = imageItemHTML(images.home(), forum.getName());
    root = new TreeItem(rootHTML);
    tree.addItem(root);

    inboxHTML = imageItemHTML(images.inbox(), "Inbox");
    inbox = new TreeItem(inboxHTML);
    root.addItem(inbox);
    
    if (forum.moderated())
    {
	    approvedHTML = imageItemHTML(images.drafts(), "Approved");
	    approved = new TreeItem(approvedHTML);
	    root.addItem(approved);
    }
    
    uploadHTML = imageItemHTML(images.sent(), "Upload");
    upload = new TreeItem(uploadHTML);
    root.addItem(upload);
    
    uploadDlg.setForum(f);
    uploadDlg.setCompleteHandler(new UploadComplete());
    
    options.add(rootHTML);
    options.add(inboxHTML);
    options.add(approvedHTML);
    options.add(uploadHTML);
	}

  /**
   * Generates HTML for a tree item with an attached icon.
   * 
   * @param imageProto the image prototype to use
   * @param title the title of the item
   * @return the resultant HTML
   */
  private HTML imageItemHTML(AbstractImagePrototype imageProto, String title) {
    HTML label = new HTML(imageProto.getHTML() + " " + title);
    label.addClickHandler(this);
  	label.addClickHandler((ClickHandler)parent);
  	return label;
  }
	
	public Widget getWidget()
	{
		return tree;
	}
	
	public void expand() 
	{
		root.setState(true);
	}

	public void onClick(ClickEvent event) {
     Object sender = event.getSource();
    if (sender == inboxHTML) 
    {
    	selectMain();
    } 
    else if (sender == approvedHTML) 
    {
    	Messages.get().displayMessages(forum, "status="+MessageStatus.APPROVED.ordinal());
    	Messages.get().setMovable(true);
    }
    else if (sender == uploadHTML)
    {
    	uploadDlg.reset();
    	uploadDlg.center();
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
  	Messages.get().displayMessages(forum, "");
  	Messages.get().setMovable(false);
  	Messages.get().setModerated(forum.moderated());
  	
		this.expand();
		tree.setSelectedItem(inbox);
	}
	
	public class UploadComplete implements SubmitCompleteHandler {

		public void onSubmitComplete(SubmitCompleteEvent event) {
				uploadDlg.hide();
				ConfirmDialog saved = new ConfirmDialog("Uploaded!");
				saved.setText("Result");
				saved.center();
				
				// get the message that was updated
				selectMain();
		}
	}
	
}
