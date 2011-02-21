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

import net.sourceforge.htmlunit.corejs.javascript.ast.ParenthesizedExpression;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.Prompt;
import org.otalo.ao.client.model.Survey;
import org.otalo.ao.client.model.Message.MessageStatus;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.resources.client.ClientBundle;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.Tree;
import com.google.gwt.user.client.ui.TreeItem;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

/**
 * A panel of fora, each presented as a tree.
 */
public class Broadcasts extends Composite implements JSONRequester, ClickHandler {
  private ArrayList<SurveyWidget> widgets = new ArrayList<SurveyWidget>();
	
	/**
   * Specifies the images that will be bundled for this Composite and specify
   * that tree's images should also be included in the same bundle.
   */
  public interface Images extends ClientBundle, Tree.Resources {
  	ImageResource inbox();  
    ImageResource sent();
    ImageResource responses();
    ImageResource reject_sm();
    ImageResource drafts();
  }

  private Images images;
  private VerticalPanel p;

  /**
   * Constructs a new list of forum widgets with a bundle of images.
   * 
   * @param images a bundle that provides the images for this widget
   */
  public Broadcasts(Images images) {
	  this.images = images;
	  p = new VerticalPanel();
  
	  initWidget(p);
  }
  
  public void load()
  {
  	// Get surveys
	  JSONRequest request = new JSONRequest();
	  String lineId = Messages.get().getLine() != null ? "?lineid=" + Messages.get().getLine().getId() : ""; 
		request.doFetchURL(AoAPI.SURVEY + lineId, this);
  }

	public void dataReceived(List<JSOModel> models) {
		Survey s;
		SurveyWidget w;
		List<Survey> surveys = new ArrayList<Survey>();
		
		p.clear();
//		p.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_DEFAULT);
//		p.setVerticalAlignment(HasVerticalAlignment.ALIGN_TOP);
		
		for (JSOModel model : models)
	  {
				s = new Survey(model);
				surveys.add(s);
				w = new SurveyWidget(s, images, this);
				
				p.add(w.getWidget());
				widgets.add(w);
	  }
		
    
//    Anchor broadcast = new Anchor("New Broadcast");
//    broadcast.addClickHandler(new ClickHandler() {
//			public void onClick(ClickEvent event) {
//				Messages.get().broadcastSomething();
//			}
//		});
    
//    p.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
//    p.setVerticalAlignment(HasVerticalAlignment.ALIGN_BOTTOM);
//    p.add(broadcast);
		
	}
	
	public void selectFirst()
	{
		for (SurveyWidget w : widgets)
		{
				w.close();
		}
		if (widgets.size() > 0)
			widgets.get(0).selectFirst();
	}
	/**
	 * This is for clicked tree items. Unselect all other ones
	 * and collapse their trees
	 * @param event
	 */
	public void onClick(ClickEvent event) {
		Object source = event.getSource();
		for (SurveyWidget w : widgets)
		{
			if (!w.contains(source))
				w.close();
		}
		
	}

}
