/*
g * Copyright 2007 Google Inc.
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
import com.google.gwt.resources.client.ClientBundle;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.uibinder.client.UiConstructor;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HasHorizontalAlignment.HorizontalAlignmentConstant;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.TextBox;

/**
 * The top panel, which contains the 'welcome' message and various links.
 */
public class TopPanel extends Composite implements ClickHandler {

  private Anchor signOutLink = new Anchor("Sign Out", AoAPI.LOGOUT);
  
  private HorizontalPanel outer, inner, search;
  private Images images;
  //search functionality
  private Button searchBtn;
  private TextBox searchBox;
  private HTML homeLink = new HTML("<a href='javascript:;'>Home</a>");
  private HTML asearchLink = new HTML("<a href='javascript:;'>Advance Search</a>");
  private FlexTable layout;
  /**
   * Specifies the images that will be bundled for this Composite and specify
   * that tree's images should also be included in the same bundle.
   */
  public interface Images extends ClientBundle {
    ImageResource recharge();
  }

  @UiConstructor
  public TopPanel(Line line, User moderator, Images images) {
    this.outer = new HorizontalPanel();
    this.inner = new HorizontalPanel();
    this.searchBtn = new Button();
    this.layout = new FlexTable();
    this.search = new HorizontalPanel();
    
    this.images = images;

    if (line != null)
    {
	    Image logo = new Image(line.getLogoFile());
	    outer.add(logo);
			outer.setCellHorizontalAlignment(logo, HorizontalPanel.ALIGN_LEFT);
    }
    outer.setHorizontalAlignment(HorizontalPanel.ALIGN_RIGHT);
    inner.setHorizontalAlignment(HorizontalPanel.ALIGN_RIGHT);
    search.setHorizontalAlignment(HorizontalPanel.ALIGN_RIGHT);
    inner.setSpacing(10);
    search.setSpacing(10);
    
    inner.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);
    layout.setWidget(0, 0, inner);
    outer.add(layout);
    if (moderator != null)
    	inner.add(new HTML("Welcome back, " + moderator.getName() + "&nbsp;(" + moderator.getNumber() + ")&nbsp;|&nbsp;"));
    
    if (Messages.get().canManage())
    {
    	JSONRequest request = new JSONRequest();
      request.doFetchURL(AoAPI.BALANCE, new BalanceRequestor());
    }
    
    homeLink.setVisible(false);
    inner.add(homeLink);
    inner.add(signOutLink);
   
    
    if(!Messages.get().canManage()) {
	    searchBox = new TextBox();
	    searchBox.setTitle("Search");
	    searchBox.setName("search_keywords");
	    search.add(searchBox);
	    searchBtn.setText("Search");
	    searchBtn.setTitle("Search");
	    searchBtn.addClickHandler(new SearchButtonHandler());
	    search.add(searchBtn);
	    search.add(asearchLink);
	    layout.setWidget(1, 0, search);
    }
    
    signOutLink.addClickHandler(this);
    homeLink.addClickHandler(this);
    asearchLink.addClickHandler(this);

    initWidget(outer);
    setStyleName("mail-TopPanel");
    //inner.setStyleName("mail-TopPanelLinks");
    
  }

  public void onClick(ClickEvent event) {
    Object sender = event.getSource();
    if (sender == signOutLink) {
    	JSONRequest request = new JSONRequest();
    	request.doFetchURL(AoAPI.LOGOUT, null);
    } else if(sender == homeLink) {
    	homeLink.setVisible(false);
    	search.setVisible(true);
    	searchBox.setText("");
    	Messages.get().displayForumPanel();
    } 
    else if(sender == asearchLink) {
    	homeLink.setVisible(true);
		search.setVisible(false);
		Messages.get().displaySerchPanel(searchBox.getText());
    }
  }
  
  public void displaySearch() {
	  if(!Messages.get().canManage())  {
		  homeLink.setVisible(false);
		  search.setVisible(true);
		  searchBox.setText("");
	  }
  }
  
  private class SearchButtonHandler implements ClickHandler {
	@Override
	public void onClick(ClickEvent event) {
		if(searchBox.getText() == null || searchBox.getText().isEmpty()) {
			ConfirmDialog validate = new ConfirmDialog("Please enter search word to search anything");
			validate.center();
		}
		else {
			homeLink.setVisible(true);
			search.setVisible(false);
			Messages.get().displaySerchPanel(searchBox.getText());
		}
	}
  }
  
  private class BalanceRequestor implements JSONRequester {
		 
		public void dataReceived(List<JSOModel> models) 
		{
			// for e.g. superuser will not have an associated AO_admin record
			if (models.size() > 0)
			{
				// reset with updated balance
				User moderator = new User(models.get(0));
				Messages.get().setModerator(moderator);
			}
			
			HTML balanceLabel = new HTML("<b>Credits:</b>");
			String balance = Messages.get().getModerator().getBalance();
			if ("null".equals(balance))
				balance = "0";
			else if (User.FREE_TRIAL_BALANCE.equals(balance))
			{
				balance = "TRIAL";
			}
				
			Label balanceAmount = new Label(balance);
			AbstractImagePrototype rechargeHTML = AbstractImagePrototype.create(images.recharge());
  	  //HTML rechargeButton = new HTML(rechargeHTML.getHTML());
  	  Anchor rechargeButton = new Anchor(rechargeHTML.getHTML(), true);
  	  rechargeButton.setStyleName("clickableimage");
			rechargeButton.addClickHandler(new ClickHandler() {
				
				public void onClick(ClickEvent event) {
					ConfirmDialog recharge = new ConfirmDialog("Online payment coming soon! For now, please send us a cheque or contact info@awaaz.de for bank e-transfer details.");
					recharge.show();
					recharge.center();
					
				}
			});
			
			// insert items right to left
			inner.insert(new Label(" | "), 1);
			inner.insert(rechargeButton, 1);
			inner.insert(balanceAmount, 1);
			inner.insert(balanceLabel, 1);
			
		}
	 }
}
