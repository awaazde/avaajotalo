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

import java.util.List;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.Line;
import org.otalo.ao.client.model.User;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;

/**
 * The top panel, which contains the 'welcome' message and various links.
 */
public class TopPanel extends Composite implements ClickHandler {

  private Anchor signOutLink = new Anchor("Sign Out", AoAPI.LOGOUT);
  private HTML aboutLink = new HTML("<a href='javascript:;'>About</a>");
  private HorizontalPanel outer, inner;

  public TopPanel(Line line, User moderator) {
    outer = new HorizontalPanel();
    inner = new HorizontalPanel();

    if (line != null)
    {
	    Image logo = new Image(line.getLogoFile());
	    outer.add(logo);
			outer.setCellHorizontalAlignment(logo, HorizontalPanel.ALIGN_LEFT);
    }
    outer.setHorizontalAlignment(HorizontalPanel.ALIGN_RIGHT);
    inner.setHorizontalAlignment(HorizontalPanel.ALIGN_RIGHT);
    inner.setSpacing(4);

    outer.add(inner);
    if (moderator != null)
    	inner.add(new HTML("<b>Welcome back, " + moderator.getName() + "</b>&nbsp;|&nbsp;"));
    inner.add(signOutLink);
    inner.add(aboutLink);
    
    signOutLink.addClickHandler(this);
    aboutLink.addClickHandler(this);

    initWidget(outer);
    setStyleName("mail-TopPanel");
    inner.setStyleName("mail-TopPanelLinks");

  }

  public void onClick(ClickEvent event) {
    Object sender = event.getSource();
    if (sender == signOutLink) {
    	JSONRequest request = new JSONRequest();
      	request.doFetchURL(AoAPI.LOGOUT, null);
    } else if (sender == aboutLink) {
      // When the 'About' item is selected, show the AboutDialog.
      // Note that showing a dialog box does not block -- execution continues
      // normally, and the dialog fires an event when it is closed.
      AboutDialog dlg = new AboutDialog();
      dlg.show();
      dlg.center();
    }
  }
}
