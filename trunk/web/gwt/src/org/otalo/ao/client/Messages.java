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

import org.otalo.ao.client.model.BaseModel;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.Line;
import org.otalo.ao.client.model.Message.MessageStatus;
import org.otalo.ao.client.model.MessageForum;
import org.otalo.ao.client.model.Prompt;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.Scheduler;
import com.google.gwt.dom.client.Style.Unit;
import com.google.gwt.event.logical.shared.ResizeEvent;
import com.google.gwt.event.logical.shared.ResizeHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.DockLayoutPanel;
import com.google.gwt.user.client.ui.DockPanel;
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
  public interface Images extends Shortcuts.Images, Fora.Images, MessageList.Images, BroadcastInterface.Images, Broadcasts.Images {
  }

  /**
   * Gets the singleton Mail instance.
   */
  public static Messages get() {
    return singleton;
  }

  private TopPanel topPanel = new TopPanel();
  private VerticalPanel rightPanel = new VerticalPanel();
  private MessageList messageList;
  private MessageDetail messageDetail = new MessageDetail();
  private Fora fora = new Fora(images);
  private Broadcasts bcasts;
  private Shortcuts shortcuts;
  private BroadcastInterface broadcastIface;

  /**
   * Displays the specified item. 
   * 
   * @param messageForum
   */
  public void setItem(MessageForum messageForum) {
    messageDetail.setItem(messageForum);
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
  	messageDetail.reset();
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
  	messageDetail.reset();
  	fora.setFolder(f, status);
  	displayForumPanel();
  	
  	messageList.getMessages(f, status, start);
  }
  
  public void displayResponses(MessageForum mf)
  {
  	// need to setup panels here 
  	// in case there are no messages
  	messageDetail.reset();
  	fora.setFolderResponses(mf.getForum());
  	
  	messageList.getResponses(mf);
  }
  
  public void displayResponses(Forum f, int start)
  {
  	// need to setup panels here 
  	// in case there are no messages
  	messageDetail.reset();
  	fora.setFolderResponses(f);
  	displayForumPanel();
  	
  	messageList.getResponses(f, start);
  }
  
  public void displayBroadcastPanel(BaseModel back)
  {
  	broadcastIface.reset(back);
  	messageList.setVisible(false);
		messageDetail.setVisible(false);
		broadcastIface.setVisible(true);
  }
  
  public void displaySurveyInputPanel()
  {
  	messageList.setVisible(true);
  	messageDetail.setVisible(false);
		broadcastIface.setVisible(false);
		// you can get rid of this once there
		// is a clickevent attached to a stackpanel header
		shortcuts.showStack(1);
  }
  
  public void displayForumPanel()
  {
  	broadcastIface.setVisible(false);
  	messageList.setVisible(true);
		messageDetail.setVisible(true);
		shortcuts.showStack(0);
  }
  
  public void displaySurveyInput(Prompt p, int start)
  {
  	if (p == null)
  	{
  		bcasts.selectFirst();
  	}
  	else
  	{
	  	displaySurveyInputPanel();
	  	messageList.displaySurveyInput(p, 0);
  	}
  }
  
  public void broadcastSomething()
  {
  	broadcastIface.loadSurveys();
  	displayBroadcastPanel(null);
  }
  
  public void forwardThread(MessageForum thread)
  {
  	broadcastIface.forwardThread(thread);
  }
  
  public Line getLine()
  {
  	return topPanel.getLine();
  }
  /**
   * This method constructs the application user interface by instantiating
   * controls and hooking up event handler.
   */
  public void onModuleLoad() {
    singleton = this;

    topPanel.setWidth("100%");

    // MailList uses Mail.get() in its constructor, so initialize it after
    // 'singleton'.
    messageList = new MessageList(images);
    messageList.setWidth("100%");
    
    broadcastIface = new BroadcastInterface(images);
    bcasts = new Broadcasts(images);
    shortcuts = new Shortcuts(images, fora, bcasts);

    // Create the right panel, containing the email list & details.
    rightPanel.add(messageList);
    rightPanel.add(messageDetail);
    rightPanel.add(broadcastIface);
    rightPanel.setWidth("100%");
    messageDetail.setWidth("100%");
    shortcuts.setWidth("100%");
    
    displayForumPanel();

    // Create a dock panel that will contain the menu bar at the top,
    // the shortcuts to the left, and the mail list & details taking the rest.
    DockPanel outer = new DockPanel();
    //DockLayoutPanel outer = new DockLayoutPanel(Unit.PCT);
    
    outer.add(topPanel, DockPanel.NORTH);
    //outer.addNorth(topPanel, 100);
    outer.add(shortcuts, DockPanel.WEST);
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
}
