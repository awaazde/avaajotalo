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

import org.otalo.ao.client.SMSList.SMSListType;
import org.otalo.ao.client.model.User;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.resources.client.ClientBundle;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Tree;
import com.google.gwt.user.client.ui.VerticalPanel;

/**
 * A panel of SMSs, each presented as a tree.
 */
public class SMSs extends Composite {
	
	/**
   * Specifies the images that will be bundled for this Composite and specify
   * that tree's images should also be included in the same bundle.
   */
  public interface Images extends ClientBundle, Tree.Resources {
  	ImageResource sent();  
    ImageResource responses();
  }

  private Images images;
  private VerticalPanel p;

  private Anchor inboxHTML, sentHTML;
  
  /*
	 * This variable should be consistent with otalo/views.py
	 */
  private static final int BCAST_PAGE_SIZE = 10;

  /**
   * Constructs the SMS panel
   * 
   * @param images a bundle that provides the images for this widget
   */
  public SMSs(Images images) {
	  this.images = images;
	  p = new VerticalPanel();
	  p.setSpacing(10);
	  
	  inboxHTML = imageItemHTML(images.responses(), "Inbox", SMSListType.IN);
	  sentHTML = imageItemHTML(images.sent(), "Sent", SMSListType.SENT);
	  Anchor newsms = new Anchor("Compose");
	  newsms.addClickHandler(new ClickHandler() {

			public void onClick(ClickEvent event) {
				String balance = Messages.get().getModerator().getBalance();
				if (!User.UNLIMITED_BALANCE.equals(balance) && Double.valueOf(balance) <= Double.valueOf(User.BCAST_DISALLOW_BALANCE_THRESH))
				{
					ConfirmDialog recharge = new ConfirmDialog("Your balance is too low for sending SMS. Please recharge your account.");
					recharge.center();
				}
				else
					Messages.get().displaySMSInterface();
			}
	  	
	  });
	 
	  p.add(newsms);
	  if (!Messages.get().canManage())
	  	p.add(inboxHTML);
	  p.add(sentHTML);
	  
  
	  initWidget(p);
  }
	
  private Anchor imageItemHTML(ImageResource res, String title, SMSListType type) {
  	AbstractImagePrototype imageProto = AbstractImagePrototype.create(res);
    Anchor label = new Anchor(imageProto.getHTML() + " " + title, true);
    label.addClickHandler(new SMSListClickHander(type));
  	return label;
  }
  
  private class SMSListClickHander implements ClickHandler{
  	private SMSListType type;
		public SMSListClickHander(SMSListType type)
		{
			this.type = type;
		}
		public void onClick(ClickEvent event) {
			Messages.get().displaySMS(type, 0);
			
		}
  	
		
  } 

}
