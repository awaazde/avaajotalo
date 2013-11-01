/*
 * Copyright 2007 Google Inc.
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

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.SMSList.SMSListType;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.Line;
import org.otalo.ao.client.model.Message.MessageStatus;
import org.otalo.ao.client.model.MessageForum;
import org.otalo.ao.client.model.Prompt;
import org.otalo.ao.client.model.User;
import org.otalo.ao.client.search.SearchFilterPanel;
import org.otalo.ao.client.search.SearchResultMsgList;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.Scheduler;
import com.google.gwt.event.logical.shared.ResizeEvent;
import com.google.gwt.event.logical.shared.ResizeHandler;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.DockPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.VerticalPanel;

/**
 * This application demonstrates how to construct a relatively complex user
 * interface, similar to many common email readers. It has no back-end,
 * populating its components with hard-coded data.
 */
public class Messages implements EntryPoint, ResizeHandler {

  private static Messages singleton;

  /**
   * Instantiate an application-level image bundle. This object will provide
   * programmatic access to all the images needed by widgets.
   */
  private static final Images images = GWT.create(Images.class);

  /**
   * An aggragate image bundle that pulls together all the images for this
   * application into a single bundle.
   */
  public interface Images extends Shortcuts.Images, Fora.Images, MessageList.Images, BroadcastInterface.Images, Broadcasts.Images, SMSInterface.Images, SMSs.Images, SMSList.Images, ManageGroups.Images, TopPanel.Images {
	  ImageResource loader();
  }

  /**
   * Gets the singleton Mail instance.
   */
  public static Messages get() {
    return singleton;
  }

  private TopPanel topPanel;
  private VerticalPanel rightPanel = new VerticalPanel();
  private MessageList messageList;
  private MessageDetail messageDetail;
  private SMSList smsList;
  private Fora fora;
  private Broadcasts bcasts = null;
  private SMSs smss = null;
  private Shortcuts shortcuts;
  private BroadcastInterface broadcastIface;
  private ManageGroups groupsIface;
  private SMSInterface smsIface;
  private User moderator;
  private Line line;
  private boolean canManage = false;

  private SearchFilterPanel search;
  private SearchResultMsgList searchResultMsgList;
  private Shortcuts searchShortCut;

  private HTML loaderImage;
 
  
  /**
   * Displays the specified item. 
   * 
   * @param messageForum
   */
  public void setItem(MessageForum messageForum) {
  	if (!canManage()) {
  		messageDetail.setItem(messageForum);
  	}
  }
  
  public void displayMoveButtons(boolean isDisplay) {
	  messageDetail.displayMoveButtons(isDisplay);
  }
  
  public void setTagable(boolean tagable)
  {
  	messageDetail.setTagable(tagable);
  }
  
  /**
   * Display messages in this message's forum
   * with this message's status (to get the folder right)
   * 
   * @param m
   */
  public void displayMessages(MessageForum mf)
  {
  	// need to setup panels here 
  	// in case there are no messages
  	if (!canManage()) messageDetail.reset();
  	fora.setFolder(mf.getForum(), mf.getStatus());
  	displayForumPanel();
  	
  	messageList.getMessages(mf);
  }
  
  /**
   * Display messages in this forum with
   * this status (to get the folder right)
   * @param f
   * @param status
   */
  public void displayMessages(Forum f, MessageStatus status, int start)
  {
  	// need to setup panels here 
  	// in case there are no messages
  	if (!canManage()) messageDetail.reset();
  	fora.setFolder(f, status);
  	displayForumPanel();
  	
  	messageList.getMessages(f, status, start);
  }
  
  public void displayResponses(MessageForum mf)
  {
  	// need to setup panels here 
  	// in case there are no messages
  	if (!canManage()) messageDetail.reset();
  	fora.setFolderResponses(mf.getForum());
  	
  	messageList.getResponses(mf);
  }
  
  public void displayResponses(Forum f, int start)
  {
  	// need to setup panels here 
  	// in case there are no messages
  	if (!canManage()) messageDetail.reset();
  	fora.setFolderResponses(f);
  	displayForumPanel();
  	
  	messageList.getResponses(f, start);
  }
  
  public void resetMessageDetail() {
	  messageDetail.reset();
  }
  
  public void displayBroadcastPanel(MessageForum thread)
  {
  	broadcastIface.reset(thread);
  	messageList.setVisible(false);
  	if (!canManage()) messageDetail.setVisible(false);
		broadcastIface.setVisible(true);
		if (canManage()) groupsIface.setVisible(false);
		if (line.hasSMSConfig())
		{
			smsList.setVisible(false);
			smsIface.setVisible(false);
		}
  }
  
  public void loadBroadcasts(int start)
  {
  	bcasts.load(start);
  }
  
  public void displaySurveyInputPanel()
  {
  	messageList.setVisible(true);
  	if (!canManage()) messageDetail.setVisible(false);
		broadcastIface.setVisible(false);
		if (line.hasSMSConfig())
		{
			smsList.setVisible(false);
			smsIface.setVisible(false);
		}
		if (canManage()) groupsIface.setVisible(false);
		// you can get rid of this once there
		// is a clickevent attached to a stackpanel header
		shortcuts.showStack(1);
  }
  
  public void displayForumPanel()
  {
	shortcuts.setVisible(true);
	if(searchShortCut != null && searchShortCut.isVisible())
		searchShortCut.setVisible(false);
	if(searchResultMsgList != null && searchResultMsgList.isVisible())
		searchResultMsgList.setVisible(false);
	
  	if (line.bcastingAllowed()) broadcastIface.setVisible(false);
  	messageList.setVisible(true);
  	if (!canManage()) messageDetail.setVisible(true);
		if (line.hasSMSConfig())
		{
			smsList.setVisible(false);
			smsIface.setVisible(false);
		}
		if (canManage()) groupsIface.setVisible(false);
		shortcuts.showStack(0);
	
	topPanel.displaySearch();
  }
  
  public void displaySearchPanel(String searchPhrase, boolean isAdvanceSearch) {
	  messageDetail.reset();
	  search.setVisible(true);
	  shortcuts.setVisible(false);
	  searchShortCut.setVisible(true);
	  searchShortCut.showStack(0);
	  search.setSearchPharse(searchPhrase, isAdvanceSearch);
	  searchResultMsgList.setVisible(true);
	  searchResultMsgList.reset();
	  messageList.setVisible(false);

	  if (line.bcastingAllowed()) broadcastIface.setVisible(false);
	  if (!canManage()) messageDetail.setVisible(true);
	  if (line.hasSMSConfig()) {
		  smsList.setVisible(false);
		  smsIface.setVisible(false);
	  }
	  if (canManage()) groupsIface.setVisible(false);
  }
  
  public void hideSearchPanel() {
	  search.setVisible(false);
	  shortcuts.setVisible(true);
	  searchShortCut.setVisible(false);
	  searchResultMsgList.setVisible(false);
	  topPanel.displaySearch();
	  messageList.setVisible(true);
	  fora.selectMain();
  }
  
  public void displaySMS(SMSListType type, int start)
  {
  	smsList.reset(type);
  	smsList.setVisible(true);
  	if (line.bcastingAllowed()) broadcastIface.setVisible(false);
  	messageList.setVisible(false);
  	if (!canManage()) messageDetail.setVisible(false);
		if (canManage()) groupsIface.setVisible(false);
		smsIface.setVisible(false);
		shortcuts.showStack(2);
		
		smsList.getMessages(type, start);
  }
  
  public void displaySMSInterface()
  {
  	smsIface.reset();
  	smsIface.setVisible(true);
  	if (line.bcastingAllowed()) broadcastIface.setVisible(false);
  	messageList.setVisible(false);
  	if (!canManage()) messageDetail.setVisible(false);
		if (canManage()) groupsIface.setVisible(false);
		smsList.setVisible(false);
		shortcuts.showStack(2);
  }
  
  public void displayManageGroupsInterface(Forum group)
  {
  	if (line.hasSMSConfig())
  	{
	  	smsIface.reset();
	  	smsIface.setVisible(false);
	  	smsList.setVisible(false);
  	}
  	if (line.bcastingAllowed()) broadcastIface.setVisible(false);
  	messageList.setVisible(false);
  	if (!canManage()) messageDetail.setVisible(false);
		groupsIface.setVisible(true);
		fora.setFolder(group, MessageStatus.MANAGE);
		
		shortcuts.showStack(0);
  }
  
  public void reloadGroups(List<JSOModel> models)
  {
  	fora.loadFora(models);
  }
  
  /**
   * Separate this out from displayManageGroupsInterface() to avoid
   * the flickering that happens on loading of new data. This loads the
   * data, and at the end of that process displayManageGroupsInterface()
   * will be invoked to pull the curtain
   * 
   * @param line
   * @param group
   */
  public void loadManageGroupsInterface(Line line, Forum group)
  {
  	groupsIface.reset(line, group);
  }
  
  public void reloadGroup(Line l, Forum f)
  {
  	fora.setGroup(l, f);
  }
  
  public void displaySurveyInput(Prompt p, int start)
  {
  	displaySurveyInputPanel();
  	if (p == null)
  	{
  		bcasts.selectFirst();
  	}
  	else
  	{
	  	messageList.displaySurveyInput(p, start);
  	}
  }
  
  public void forwardThread(MessageForum thread)
  {
  	broadcastIface.broadcastThread(thread);
  }
  
  public Line getLine()
  {
  	return line;
  }
  
  public boolean canManage()
  {
  	return canManage;
  }
  
  public User getModerator()
  {
  	return moderator;
  }
  /**
   * This method constructs the application user interface by instantiating
   * controls and hooking up event handler.
   */
  public void onModuleLoad() {
    singleton = this;
    // before kicking off, get line and moderator info
    JSONRequest request = new JSONRequest();
	  request.doFetchURL(AoAPI.MODERATOR, new ModeratorRequestor());
  }
  
  public void loadRest() {

    topPanel = new TopPanel(line, moderator, images);
    topPanel.setWidth("100%");
    
    fora = new Fora(images);
    messageList = new MessageList(images);
    messageList.setWidth("100%");
    
    
    // Create the right panel, containing the email list & details.
    rightPanel.add(messageList);
    if(!canManage()) {
    	searchResultMsgList = new SearchResultMsgList();
	    searchResultMsgList.setWidth("100%");
	    searchResultMsgList.setVisible(false);
    	rightPanel.add(searchResultMsgList);
    }
    
    if (line.bcastingAllowed())
    {
    	broadcastIface = new BroadcastInterface(images);
    	bcasts = new Broadcasts(images);
    	rightPanel.add(broadcastIface);
    }
    if (line.hasSMSConfig())
    {
      smsList = new SMSList(images);
    	smsList.setWidth("100%");
    	smsIface = new SMSInterface(images);
    	smss = new SMSs(images);
	    rightPanel.add(smsIface);
	    rightPanel.add(smsList);
    }
    
    shortcuts = new Shortcuts(images, fora, bcasts, smss, search);
    shortcuts.setWidth("100%");
    rightPanel.setWidth("100%");
    
    if (canManage())
    {
      groupsIface = new ManageGroups(images);
    	rightPanel.add(groupsIface);
    	
    	//showing help if its stream
    	String helpHtmlStr = "<div id='help_tab' class='help-tab-right'>"
    			+ "<a href='http://awaaz.de/blog/2013/09/awaaz-de-streams-start-up-guide-and-glossary/' target=_blank  id='help-link>"
    			+ "<span>H</span>"
    			+ "<span>E</span>"
    			+ "<span>L</span>"
    			+ "<span>P</span></a></div>";
    	HTML helpHtml = new HTML(helpHtmlStr);
    	RootPanel.get().add(helpHtml);
    }
    else
    {
    	messageDetail = new MessageDetail();
    	messageDetail.setWidth("100%");
    	rightPanel.add(messageDetail);
    	
    	search = new SearchFilterPanel(searchResultMsgList);
    	searchShortCut = new Shortcuts(images, null, null, null, search);
    	searchShortCut.setWidth("100%");
    	searchShortCut.setVisible(false);
    }
    
    displayForumPanel();
    
    // creating a loader
    loaderImage = new HTML(AbstractImagePrototype.create(images.loader()).getHTML());
	loaderImage.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
	loaderImage.addStyleName("loader-img");
	showLoader(false);
	
	rightPanel.add(loaderImage);
	
	// Create a dock panel that will contain the menu bar at the top,
    // the shortcuts to the left, and the mail list & details taking the rest.
    DockPanel outer = new DockPanel();
    //DockLayoutPanel outer = new DockLayoutPanel(Unit.PCT);
   
    outer.add(topPanel, DockPanel.NORTH);
    outer.add(shortcuts, DockPanel.WEST);
    if(!canManage()) {
    	if(searchShortCut.isVisible())
    		searchShortCut.setVisible(false);
    	outer.add(searchShortCut, DockPanel.WEST);
    }
    
    //outer.addWest(shortcuts, 100);
    outer.add(rightPanel, DockPanel.CENTER);
    //outer.add(rightPanel);
    outer.setWidth("100%");

    outer.setSpacing(4);
    outer.setCellWidth(rightPanel, "100%");

    // Hook the window resize event, so that we can adjust the UI.
    Window.addResizeHandler(this);

    // Get rid of scrollbars, and clear out the window's built-in margin,
    // because we want to take advantage of the entire client area.
    //Window.enableScrolling(false);
    Window.setMargin("0px");

    // Finally, add the outer panel to the RootPanel, so that it will be
    // displayed.
    RootPanel.get().add(outer);

    // Call the window resized handler to get the initial sizes setup. Doing
    // this in a deferred command causes it to occur after all widgets' sizes
    // have been computed by the browser.
    Scheduler.get().scheduleDeferred(new Scheduler.ScheduledCommand() {
		public void execute() {
			onWindowResized(Window.getClientWidth(), Window.getClientHeight());
			
		}
	});

    onWindowResized(Window.getClientWidth(), Window.getClientHeight());
  }

  
  public void showLoader(boolean isShow) {
	  loaderImage.setVisible(isShow);
  }
  
 
  
  public void onResize(ResizeEvent event) {
    onWindowResized(event.getWidth(), event.getHeight());
  }

  public void onWindowResized(int width, int height) {
    // Adjust the shortcut panel and detail area to take up the available room
    // in the window.
    int shortcutHeight = height - shortcuts.getAbsoluteTop() - 8;
    if (shortcutHeight < 1) {
      shortcutHeight = 1;
    }
    shortcuts.setHeight(shortcutHeight + "px");

  }
  
  private class ModeratorRequestor implements JSONRequester {
		 
		public void dataReceived(List<JSOModel> models) 
		{
			// for e.g. superuser will not have an associated AO_admin record
			if (models.size() > 0)
			{
				moderator = new User(models.get(0));
			}
			
			JSONRequest request = new JSONRequest();
		  request.doFetchURL(AoAPI.LINE, new LineRequestor());
		}
	 }
  
  public void setModerator(User moderator)
  {
  	this.moderator = moderator;
  }
  
  private class LineRequestor implements JSONRequester {
		 
		public void dataReceived(List<JSOModel> models) 
		{
			List<Line> lines = new ArrayList<Line>();
			Line l;
			for (JSOModel model : models)
			{
				l = new Line(model);
				if (l.canManage()) {
					// as long as one line can be managed, enable it for
					// the admin
					canManage = true;
				}
				lines.add(l);
			}
			// This worked when all forums came from the same line
			// but may not be true if you're admining across multiple
			// lines. Should be replaced by full line list, with operations
			// and queries on a list of listids
			line = lines.get(0);
			// do all the stuff that depends on line being loaded
			loadRest();

		}
	 }
}