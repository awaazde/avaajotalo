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
import org.otalo.ao.client.model.Tag;
import org.otalo.ao.client.model.User;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.ImageBundle;
import com.google.gwt.user.client.ui.VerticalPanel;

/**
 * The top panel, which contains the 'welcome' message and various links.
 */
public class TopPanel extends Composite implements ClickHandler {

  /**
   * An image bundle for this widgets images.
   */
  public interface Images extends ImageBundle {
    AbstractImagePrototype logo();
  }

  private Anchor signOutLink = new Anchor("Sign Out", AoAPI.LOGOUT);
  private HTML aboutLink = new HTML("<a href='javascript:;'>About</a>");
  private HorizontalPanel inner;

  public TopPanel(Images images) {
    HorizontalPanel outer = new HorizontalPanel();
    inner = new HorizontalPanel();

    outer.setHorizontalAlignment(HorizontalPanel.ALIGN_RIGHT);
    inner.setHorizontalAlignment(HorizontalPanel.ALIGN_RIGHT);

    inner.setSpacing(4);

    final Image logo = images.logo().createImage();
    outer.add(logo);
    outer.setCellHorizontalAlignment(logo, HorizontalPanel.ALIGN_LEFT);

    outer.add(inner);
    inner.add(signOutLink);
    inner.add(aboutLink);
    
    signOutLink.addClickHandler(this);
    aboutLink.addClickHandler(this);

    initWidget(outer);
    setStyleName("mail-TopPanel");
    inner.setStyleName("mail-TopPanelLinks");
    getUsername();
  }
  
  private void getUsername()
  {
	  JSONRequest request = new JSONRequest();
	  request.doFetchURL(AoAPI.USERNAME, new UsernameRequestor());
  }
  
  private class UsernameRequestor implements JSONRequester {
		 
		public void dataReceived(List<JSOModel> models) 
		{
			// for e.g. superuser will not have an associated AO_admin record
			if (models.size() > 0)
			{
				User u = new User(models.get(0));
				inner.insert(new HTML("<b>Welcome back, " + u.getName() + "</b>&nbsp;|&nbsp;"), 0);
			}

		}
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
